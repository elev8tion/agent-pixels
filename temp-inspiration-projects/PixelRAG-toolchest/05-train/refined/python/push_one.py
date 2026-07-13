def push_one(comp, run_dir, step, judge, config):
    src = Path(BASE_CKPT_DIR) / run_dir / f"checkpoint-{step}"
    assert src.exists(), f"missing {src}"

    repo_id = f"{USER}/qwen3vl-4b-wiki-screenshot-{comp}-lora"
    print(f"\n=== {repo_id} ===")
    print(f"  src:  {src}")
    print(f"  step: {step}, judge: {judge}")

    # Stage files in a temp dir
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        for name in KEEP_FILES:
            p = src / name
            if p.exists():
                shutil.copy2(p, tmp / name)
                print(f"  + {name}")
            else:
                print(f"  - {name} (not present, skipped)")

        # Write README
        base_judge = BASE_BASELINE[comp]
        (tmp / "README.md").write_text(
            build_readme(comp, step, judge, config, base_judge)
        )
        print("  + README.md")

        # Create repo + upload
        create_repo(repo_id, token=TOKEN, exist_ok=True, private=False)
        upload_folder(
            folder_path=str(tmp),
            repo_id=repo_id,
            token=TOKEN,
            commit_message=f"Upload {comp} LoRA adapter (step {step}, LLM-judge {judge})",
        )
        print(f"  uploaded → https://huggingface.co/{repo_id}")
