# Cleansed Extracted Modules

**Source:** `/Users/kc/PixelRAG-toolchest/01-render`
**Extracted:** 2026-07-08 04:28
**Extracted items:** 189
**Raw source files preserved:** 27 in `raw/`

## Analysis Summary

- **Health Score:** 34/100
- **Long Functions:** 30
- **Duplication Pairs:** 20
- **High Coupling Items:** 20
- **Potential Dead Code:** 162 items (49 high-confidence)
- **Modules (Directories):** 1
- **Cross-Module Dependencies:** 0

## Languages

- **python:** 189 items

## Contents

| Name | Type | Language | Source File | Valid |
|------|------|----------|-------------|-------|
| _find_chrome | function | python | `cdp.py:55` | Yes |
| _connect_cdp | function | python | `cdp.py:61` | Yes |
| _http_base_from_cdp_url | function | python | `cdp.py:87` | Yes |
| _connect_ws | function | python | `cdp.py:102` | Yes |
| _fetch_json | function | python | `cdp.py:109` | Yes |
| _browser_ws_url | function | python | `cdp.py:123` | Yes |
| _page_ws_url_for_target | function | python | `cdp.py:135` | Yes |
| _cdp_send | function | python | `cdp.py:154` | Yes |
| _readiness_expr | function | python | `cdp.py:178` | Yes |
| capture_url | function | python | `cdp.py:262` | Yes |
| _setup_page | function | python | `cdp.py:371` | Yes |
| _drain_queue | function | python | `cdp.py:393` | Yes |
| _worker | function | python | `cdp.py:446` | Yes |
| _derive_stems | function | python | `cdp.py:514` | Yes |
| _run_batch | function | python | `cdp.py:542` | Yes |
| _attached_worker | function | python | `cdp.py:589` | Yes |
| _run_batch_attached | function | python | `cdp.py:655` | Yes |
| render_urls | function | python | `cdp.py:709` | Yes |
| compress_tile | function | python | `fast_cdp.py:87` | Yes |
| _next_base_port | function | python | `fast_cdp.py:113` | Yes |
| _launch_chrome | function | python | `fast_cdp.py:119` | Yes |
| _Conn | class | python | `fast_cdp.py:165` | Yes |
| _Conn.__init__ | method | python | `fast_cdp.py:168` | Yes |
| _Conn._ensure_recv | method | python | `fast_cdp.py:177` | Yes |
| _Conn._recv_loop | method | python | `fast_cdp.py:181` | Yes |
| _Conn.cdp | method | python | `fast_cdp.py:214` | Yes |
| _Conn.wait_for_event | method | python | `fast_cdp.py:227` | Yes |
| _Conn.close | method | python | `fast_cdp.py:245` | Yes |
| _run_render | function | python | `fast_cdp.py:264` | Yes |
| render_articles | function | python | `fast_cdp.py:601` | Yes |
| render_pdf | function | python | `pdf.py:16` | Yes |
| prepare_articles | function | python | `bench_throughput.py:52` | Yes |
| cleanup_articles | function | python | `bench_throughput.py:117` | Yes |
| gt_cache_key | function | python | `bench_throughput.py:132` | Yes |
| generate_ground_truth | function | python | `bench_throughput.py:138` | Yes |
| _make_gt_strategy | function | python | `bench_throughput.py:192` | Yes |
| validate_gt | function | python | `bench_throughput.py:204` | Yes |
| decode_tile | function | python | `bench_throughput.py:237` | Yes |
| verify_tile | function | python | `bench_throughput.py:253` | Yes |
| run_and_verify | function | python | `bench_throughput.py:272` | Yes |
| Bench | class | python | `bench_throughput.py:387` | Yes |
| Bench.__init__ | method | python | `bench_throughput.py:395` | Yes |
| Bench.prepare | method | python | `bench_throughput.py:411` | Yes |
| Bench.ensure_gt | method | python | `bench_throughput.py:418` | Yes |
| Bench.run | method | python | `bench_throughput.py:443` | Yes |
| Bench._build_experiment | method | python | `bench_throughput.py:455` | Yes |
| Bench._dump_experiment | method | python | `bench_throughput.py:479` | Yes |
| format_result_line | function | python | `bench_throughput.py:494` | Yes |
| print_results | function | python | `bench_throughput.py:504` | Yes |
| _candidate_chrome_paths | function | python | `chrome.py:37` | Yes |
| find_chrome | function | python | `chrome.py:97` | Yes |
| get_installed_version | function | python | `chrome.py:124` | Yes |
| is_turbo_capable | function | python | `chrome.py:136` | Yes |
| install_chrome | function | python | `chrome.py:155` | Yes |
| _progress_hook | function | python | `chrome.py:237` | Yes |
| main | function | python | `chrome.py:246` | Yes |
| render_url | function | python | `render.py:20` | Yes |
| render_urls | function | python | `render.py:59` | Yes |
| render_pdf | function | python | `render.py:111` | Yes |
| render_file | function | python | `render.py:136` | Yes |
| main | function | python | `render.py:189` | Yes |
| TileCapture | class | python | `base.py:15` | Yes |
| ArticleCapture | class | python | `base.py:29` | Yes |
| article_url | function | python | `base.py:42` | Yes |
| ChromeConnection | class | python | `base.py:48` | Yes |
| ChromeConnection.cdp | method | python | `base.py:51` | Yes |
| ChromeConnection.close | method | python | `base.py:55` | Yes |
| CaptureStrategy | class | python | `base.py:58` | Yes |
| CaptureStrategy.name | method | python | `base.py:62` | No (SyntaxError: unexpected indent (line 2)) |
| CaptureStrategy.fmt | method | python | `base.py:65` | No (SyntaxError: unexpected indent (line 2)) |
| CaptureStrategy.setup | method | python | `base.py:67` | Yes |
| CaptureStrategy.teardown | method | python | `base.py:69` | Yes |
| CaptureStrategy.capture_articles | method | python | `base.py:71` | Yes |
| CDPDCsingleStrategy | class | python | `cdp_dc_single.py:49` | Yes |
| CDPDCsingleStrategy.name | method | python | `cdp_dc_single.py:62` | No (SyntaxError: unexpected indent (line 2)) |
| CDPDCsingleStrategy.setup | method | python | `cdp_dc_single.py:65` | Yes |
| CDPDCsingleStrategy.teardown | method | python | `cdp_dc_single.py:90` | Yes |
| CDPDCsingleStrategy.capture_articles | method | python | `cdp_dc_single.py:95` | Yes |
| CDPDCsingleStrategy._capture_one | method | python | `cdp_dc_single.py:114` | Yes |
| CDPDirectClipStrategy | class | python | `cdp_directclip.py:38` | Yes |
| CDPDirectClipStrategy.name | method | python | `cdp_directclip.py:63` | No (SyntaxError: unexpected indent (line 2)) |
| CDPDirectClipStrategy.setup | method | python | `cdp_directclip.py:67` | Yes |
| CDPDirectClipStrategy.teardown | method | python | `cdp_directclip.py:97` | Yes |
| CDPDirectClipStrategy.capture_articles | method | python | `cdp_directclip.py:102` | Yes |
| CDPDirectClipStrategy._capture_one | method | python | `cdp_directclip.py:121` | Yes |
| CDPDynamicStrategy | class | python | `cdp_dynamic.py:24` | Yes |
| CDPDynamicStrategy.name | method | python | `cdp_dynamic.py:45` | No (SyntaxError: unexpected indent (line 2)) |
| CDPDynamicStrategy.setup | method | python | `cdp_dynamic.py:49` | Yes |
| CDPDynamicStrategy.teardown | method | python | `cdp_dynamic.py:79` | Yes |
| CDPDynamicStrategy.capture_articles | method | python | `cdp_dynamic.py:84` | Yes |
| CDPDynamicStrategy._capture_one | method | python | `cdp_dynamic.py:103` | Yes |
| CDPFullpageStrategy | class | python | `cdp_fullpage.py:28` | Yes |
| CDPFullpageStrategy.name | method | python | `cdp_fullpage.py:50` | No (SyntaxError: unexpected indent (line 2)) |
| CDPFullpageStrategy.setup | method | python | `cdp_fullpage.py:54` | Yes |
| CDPFullpageStrategy.teardown | method | python | `cdp_fullpage.py:72` | Yes |
| CDPFullpageStrategy.capture_articles | method | python | `cdp_fullpage.py:77` | Yes |
| CDPFullpageStrategy._capture_one | method | python | `cdp_fullpage.py:96` | Yes |
| CDPMultiTabStrategy | class | python | `cdp_multitab.py:57` | Yes |
| CDPMultiTabStrategy.n_workers | method | python | `cdp_multitab.py:74` | No (SyntaxError: unexpected indent (line 2)) |
| CDPMultiTabStrategy.name | method | python | `cdp_multitab.py:78` | No (SyntaxError: unexpected indent (line 2)) |
| CDPMultiTabStrategy._pick_base_port | method | python | `cdp_multitab.py:81` | Yes |
| CDPMultiTabStrategy.setup | method | python | `cdp_multitab.py:85` | Yes |
| CDPMultiTabStrategy.teardown | method | python | `cdp_multitab.py:185` | Yes |
| CDPMultiTabStrategy.capture_articles | method | python | `cdp_multitab.py:203` | Yes |
| CDPMultiTabStrategy._capture_one | method | python | `cdp_multitab.py:228` | Yes |
| CDPNoScrollStrategy | class | python | `cdp_noscroll.py:23` | Yes |
| CDPNoScrollStrategy.name | method | python | `cdp_noscroll.py:42` | No (SyntaxError: unexpected indent (line 2)) |
| CDPNoScrollStrategy.setup | method | python | `cdp_noscroll.py:46` | Yes |
| CDPNoScrollStrategy.teardown | method | python | `cdp_noscroll.py:76` | Yes |
| CDPNoScrollStrategy.capture_articles | method | python | `cdp_noscroll.py:81` | Yes |
| CDPNoScrollStrategy._capture_one | method | python | `cdp_noscroll.py:100` | Yes |
| _launch_oneshot | function | python | `cdp_oneshot.py:68` | Yes |
| _kill_proc | function | python | `cdp_oneshot.py:116` | Yes |
| CDPOneShotStrategy | class | python | `cdp_oneshot.py:132` | Yes |
| CDPOneShotStrategy.name | method | python | `cdp_oneshot.py:158` | No (SyntaxError: unexpected indent (line 2)) |
| CDPOneShotStrategy.setup | method | python | `cdp_oneshot.py:163` | Yes |
| CDPOneShotStrategy.teardown | method | python | `cdp_oneshot.py:170` | Yes |
| CDPOneShotStrategy.capture_articles | method | python | `cdp_oneshot.py:178` | Yes |
| CDPOneShotStrategy._capture_one | method | python | `cdp_oneshot.py:195` | Yes |
| CDPOneShotStrategy._capture_article | method | python | `cdp_oneshot.py:232` | Yes |
| _launch_two_tabs | function | python | `cdp_overlap.py:56` | Yes |
| CDPOverlapStrategy | class | python | `cdp_overlap.py:129` | Yes |
| CDPOverlapStrategy.name | method | python | `cdp_overlap.py:147` | No (SyntaxError: unexpected indent (line 2)) |
| CDPOverlapStrategy.setup | method | python | `cdp_overlap.py:151` | Yes |
| CDPOverlapStrategy.teardown | method | python | `cdp_overlap.py:182` | Yes |
| CDPOverlapStrategy.capture_articles | method | python | `cdp_overlap.py:204` | Yes |
| CDPOverlapStrategy._navigate | method | python | `cdp_overlap.py:241` | Yes |
| CDPOverlapStrategy._capture | method | python | `cdp_overlap.py:260` | Yes |
| CDPParallelStrategy | class | python | `cdp_parallel.py:23` | Yes |
| CDPParallelStrategy.name | method | python | `cdp_parallel.py:42` | No (SyntaxError: unexpected indent (line 2)) |
| CDPParallelStrategy.setup | method | python | `cdp_parallel.py:48` | Yes |
| CDPParallelStrategy.teardown | method | python | `cdp_parallel.py:79` | Yes |
| CDPParallelStrategy.capture_articles | method | python | `cdp_parallel.py:85` | Yes |
| CDPParallelStrategy._capture_one_parallel | method | python | `cdp_parallel.py:105` | Yes |
| CDPParallelStrategy._capture_single | method | python | `cdp_parallel.py:228` | Yes |
| CDPParallelStrategy._capture_sequential_fallback | method | python | `cdp_parallel.py:272` | Yes |
| CDPPerTileImgWaitStrategy | class | python | `cdp_pertile_imgwait.py:40` | Yes |
| CDPPerTileImgWaitStrategy.name | method | python | `cdp_pertile_imgwait.py:58` | No (SyntaxError: unexpected indent (line 2)) |
| CDPPerTileImgWaitStrategy.setup | method | python | `cdp_pertile_imgwait.py:62` | Yes |
| CDPPerTileImgWaitStrategy.teardown | method | python | `cdp_pertile_imgwait.py:92` | Yes |
| CDPPerTileImgWaitStrategy.capture_articles | method | python | `cdp_pertile_imgwait.py:97` | Yes |
| CDPPerTileImgWaitStrategy._capture_one | method | python | `cdp_pertile_imgwait.py:116` | Yes |
| CDPPhasedStrategy | class | python | `cdp_phased.py:51` | Yes |
| CDPPhasedStrategy._pick_base_port | method | python | `cdp_phased.py:76` | Yes |
| CDPPhasedStrategy.name | method | python | `cdp_phased.py:82` | No (SyntaxError: unexpected indent (line 2)) |
| CDPPhasedStrategy.setup | method | python | `cdp_phased.py:88` | Yes |
| CDPPhasedStrategy.teardown | method | python | `cdp_phased.py:122` | Yes |
| CDPPhasedStrategy.capture_articles | method | python | `cdp_phased.py:127` | Yes |
| CDPPhasedStrategy._capture_one | method | python | `cdp_phased.py:151` | Yes |
| TwoTabConnection | class | python | `cdp_pipelined_dc.py:55` | Yes |
| TwoTabConnection.__init__ | method | python | `cdp_pipelined_dc.py:58` | Yes |
| TwoTabConnection.close | method | python | `cdp_pipelined_dc.py:63` | Yes |
| launch_two_tab | function | python | `cdp_pipelined_dc.py:74` | Yes |
| CDPPipelinedDCStrategy | class | python | `cdp_pipelined_dc.py:135` | Yes |
| CDPPipelinedDCStrategy.name | method | python | `cdp_pipelined_dc.py:146` | No (SyntaxError: unexpected indent (line 2)) |
| CDPPipelinedDCStrategy.from_surface | method | python | `cdp_pipelined_dc.py:150` | No (SyntaxError: unexpected indent (line 2)) |
| CDPPipelinedDCStrategy.launcher | method | python | `cdp_pipelined_dc.py:154` | No (SyntaxError: unexpected indent (line 2)) |
| CDPPipelinedDCStrategy.setup | method | python | `cdp_pipelined_dc.py:157` | Yes |
| CDPPipelinedDCStrategy.teardown | method | python | `cdp_pipelined_dc.py:183` | Yes |
| CDPPipelinedDCStrategy.capture_articles | method | python | `cdp_pipelined_dc.py:188` | Yes |
| CDPPipelinedDCStrategy._navigate | method | python | `cdp_pipelined_dc.py:235` | Yes |
| CDPPipelinedDCStrategy._capture | method | python | `cdp_pipelined_dc.py:256` | Yes |
| CDPPipelinedTabsStrategy | class | python | `cdp_pipelined_tabs.py:50` | Yes |
| CDPPipelinedTabsStrategy.name | method | python | `cdp_pipelined_tabs.py:68` | No (SyntaxError: unexpected indent (line 2)) |
| CDPPipelinedTabsStrategy.setup | method | python | `cdp_pipelined_tabs.py:72` | Yes |
| CDPPipelinedTabsStrategy.teardown | method | python | `cdp_pipelined_tabs.py:174` | Yes |
| CDPPipelinedTabsStrategy.capture_articles | method | python | `cdp_pipelined_tabs.py:195` | Yes |
| CDPPipelinedTabsStrategy._nav_and_wait | method | python | `cdp_pipelined_tabs.py:238` | Yes |
| CDPPipelinedTabsStrategy._capture_tiles | method | python | `cdp_pipelined_tabs.py:250` | Yes |
| CDPSequentialStrategy | class | python | `cdp_sequential.py:26` | Yes |
| CDPSequentialStrategy.name | method | python | `cdp_sequential.py:53` | No (SyntaxError: unexpected indent (line 2)) |
| CDPSequentialStrategy.setup | method | python | `cdp_sequential.py:60` | Yes |
| CDPSequentialStrategy.teardown | method | python | `cdp_sequential.py:92` | Yes |
| CDPSequentialStrategy.capture_articles | method | python | `cdp_sequential.py:98` | Yes |
| CDPSequentialStrategy._capture_one | method | python | `cdp_sequential.py:118` | Yes |
| pick_page_ws_url | function | python | `connection.py:20` | Yes |
| WebsocketConnection | class | python | `connection.py:34` | Yes |
| WebsocketConnection.__init__ | method | python | `connection.py:37` | Yes |
| WebsocketConnection._ensure_recv_loop | method | python | `connection.py:53` | Yes |
| WebsocketConnection._recv_loop | method | python | `connection.py:58` | Yes |
| WebsocketConnection.cdp | method | python | `connection.py:107` | Yes |
| WebsocketConnection.wait_for_event | method | python | `connection.py:120` | Yes |
| WebsocketConnection.close | method | python | `connection.py:159` | Yes |
| PlaywrightConnection | class | python | `connection.py:171` | Yes |
| PlaywrightConnection.__init__ | method | python | `connection.py:174` | Yes |
| PlaywrightConnection.cdp | method | python | `connection.py:180` | Yes |
| PlaywrightConnection.close | method | python | `connection.py:184` | Yes |
| launch_websocket | function | python | `connection.py:195` | Yes |
| launch_playwright | function | python | `connection.py:248` | Yes |

## Validation

- **name**: SyntaxError: unexpected indent (line 2)
- **fmt**: SyntaxError: unexpected indent (line 2)
- **name**: SyntaxError: unexpected indent (line 2)
- **name**: SyntaxError: unexpected indent (line 2)
- **name**: SyntaxError: unexpected indent (line 2)
- **name**: SyntaxError: unexpected indent (line 2)
- **n_workers**: SyntaxError: unexpected indent (line 2)
- **name**: SyntaxError: unexpected indent (line 2)
- **name**: SyntaxError: unexpected indent (line 2)
- **name**: SyntaxError: unexpected indent (line 2)
- **name**: SyntaxError: unexpected indent (line 2)
- **name**: SyntaxError: unexpected indent (line 2)
- **name**: SyntaxError: unexpected indent (line 2)
- **name**: SyntaxError: unexpected indent (line 2)
- **name**: SyntaxError: unexpected indent (line 2)
- **from_surface**: SyntaxError: unexpected indent (line 2)
- **launcher**: SyntaxError: unexpected indent (line 2)
- **name**: SyntaxError: unexpected indent (line 2)
- **name**: SyntaxError: unexpected indent (line 2)

## Raw Source

All 27 original source files are preserved in the `raw/` directory, 
organized with the same directory structure as the original project. 
This includes both code files and non-code assets (images, configs, binaries) 
that were not extracted as modules.

---
Generated by Cleansed v1.0.0
