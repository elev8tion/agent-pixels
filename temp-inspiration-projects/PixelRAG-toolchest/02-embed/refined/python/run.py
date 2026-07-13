def run(
        self,
        tile_infos: list[TileInfo],
        batch_size: int,
        result_dir: str,
    ) -> list[str]:
        """Distribute tile_infos dynamically across workers and collect results.

        Splits tile_infos into small work chunks and puts them into the shared
        queue. Workers pull chunks as they finish, so fast GPUs process more.
        """
        round_id = f"{time.time_ns()}"
        t_round_start = time.time()

        # Respawn dead workers from previous rounds (skip permanently excluded GPUs)
        dead_before = [
            gid
            for gid, p in self.workers.items()
            if not p.is_alive() and gid not in self._excluded_gpus
        ]
        for gid in dead_before:
            self._gpu_death_count[gid] = self._gpu_death_count.get(gid, 0) + 1
            if self._gpu_death_count[gid] > 2:
                logger.error(
                    "GPU %d: died %d times — permanently excluding from pool",
                    gid,
                    self._gpu_death_count[gid],
                )
                self._excluded_gpus.add(gid)
                self.workers[gid].close()
                del self.workers[gid]
                continue
            logger.warning(
                "GPU %d: worker died (exitcode=%s), respawning (death #%d)",
                gid,
                self.workers[gid].exitcode,
                self._gpu_death_count[gid],
            )
            self.workers[gid].close()
            p = self.ctx.Process(
                target=_gpu_worker_persistent_entry,
                args=(
                    self.work_queue,
                    self.result_queue,
                    gid,
                    self._model_path,
                    self._backend,
                    self._io_workers,
                    self._compress_npz,
                    self._max_pixels,
                    self._chunk_height,
                    self._enforce_eager,
                    None,
                    self._adapter_path,
                ),  # no barrier for respawned workers
                daemon=False,
            )
            p.start()
            self.workers[gid] = p
            logger.info("GPU %d: respawned worker (pid=%d)", gid, p.pid)
        if dead_before:
            # Give respawned workers time to load model
            logger.info(
                "Waiting 30s for %d respawned workers to load model...",
                len(dead_before),
            )
            time.sleep(30)
        n_workers = len(self.workers)
        if n_workers == 0:
            raise RuntimeError("All persistent workers are dead, cannot run")

        # Split into work chunks
        work_items = []
        for i in range(0, len(tile_infos), _WORK_CHUNK_SIZE):
            chunk = tile_infos[i : i + _WORK_CHUNK_SIZE]
            work_items.append(
                {
                    "task_id": f"{round_id}_{len(work_items)}",
                    "round_id": round_id,
                    "tile_infos": chunk,
                    "batch_size": batch_size,
                    "result_dir": result_dir,
                }
            )

        logger.info(
            "Dynamic distribution: %d tiles -> %d work items for %d GPUs",
            len(tile_infos),
            len(work_items),
            n_workers,
        )

        # Enqueue all work items (no sentinels — we count results instead)
        for item in work_items:
            self.work_queue.put(item)
        n_work_items = len(work_items)

        # Collect results until we've received one result per work item
        partial_paths: list[str] = []
        errors: list[str] = []
        results_received = 0
        gpu_work_counts: dict[int, int] = {}
        gpu_consecutive_errors: dict[int, int] = {}  # track per-GPU error streaks

        dead_reported: set[int] = set()
        stall_count = 0  # consecutive timeouts with no new results

        while results_received < n_work_items:
            try:
                msg = self.result_queue.get(timeout=10)
                stall_count = 0  # got something, reset
            except queue.Empty:
                stall_count += 1
                # Check for dead workers
                for gid, p in self.workers.items():
                    if gid not in dead_reported and not p.is_alive():
                        dead_reported.add(gid)
                        errors.append(f"GPU {gid}: worker died (exitcode={p.exitcode})")
                        logger.error(
                            "GPU %d: worker died (exitcode=%s), %d/%d results so far",
                            gid,
                            p.exitcode,
                            results_received,
                            n_work_items,
                        )
                alive = [gid for gid, p in self.workers.items() if p.is_alive()]
                if not alive:
                    remaining = n_work_items - results_received
                    errors.append(
                        f"All workers dead, {remaining} work items unprocessed"
                    )
                    break
                # If a worker died and we've stalled for 60s, remaining items
                # were likely in that worker's pipeline — stop waiting
                if dead_reported and stall_count >= 6:
                    remaining = n_work_items - results_received
                    logger.warning(
                        "Stalled 60s after worker death, giving up on %d remaining items",
                        remaining,
                    )
                    break
                continue

            if msg.get("round_done"):
                # Stale sentinel from a previous round — ignore
                continue

            # Normal work result
            results_received += 1
            gid = msg.get("gpu_id", -1)
            gpu_work_counts[gid] = gpu_work_counts.get(gid, 0) + 1

            if msg.get("error"):
                gpu_consecutive_errors[gid] = gpu_consecutive_errors.get(gid, 0) + 1
                if gpu_consecutive_errors[gid] >= 3 and gid not in dead_reported:
                    dead_reported.add(gid)
                    logger.error(
                        "GPU %d: %d consecutive task errors — treating as dead, "
                        "killing worker to prevent it from stealing work",
                        gid,
                        gpu_consecutive_errors[gid],
                    )
                    # Kill the worker process so it stops pulling from the shared queue
                    p = self.workers.get(gid)
                    if p and p.is_alive():
                        p.kill()
                errors.append(
                    f"GPU {gid} task {msg.get('task_id')} failed:\n{msg['error']}"
                )
                continue
            # Successful result — reset error streak for this GPU
            gpu_consecutive_errors[gid] = 0
            pp = msg.get("partial_path", "")
            if pp:
                partial_paths.append(pp)

        # Log per-GPU work distribution and round summary
        round_elapsed = time.time() - t_round_start
        total_chunks = len(tile_infos)
        throughput = total_chunks / round_elapsed if round_elapsed > 0 else 0
        per_gpu_tp = throughput / n_workers if n_workers > 0 else 0
        gpu_summary = ", ".join(
            f"GPU {gid}: {gpu_work_counts.get(gid, 0)}" for gid in sorted(self.workers)
        )
        logger.info(
            "Round done: %d chunks in %.1fs = %.1f chunks/s (%.1f/GPU) | %s",
            total_chunks,
            round_elapsed,
            throughput,
            per_gpu_tp,
            gpu_summary,
        )

        if errors:
            logger.error("Dynamic worker errors:\n%s", "\n".join(errors))
            if not partial_paths:
                raise RuntimeError("All dynamic workers failed:\n" + "\n".join(errors))
            # If a GPU died and stole work, the shard is incomplete — raise so caller retries
            if dead_reported:
                raise RuntimeError(
                    f"GPU(s) {dead_reported} died during round — shard is incomplete "
                    f"({len(partial_paths)} partial results from {n_work_items} work items). "
                    f"Caller should retry without dead GPU(s)."
                )
            logger.warning(
                "%d errors, continuing with %d partial results",
                len(errors),
                len(partial_paths),
            )

        return partial_paths
