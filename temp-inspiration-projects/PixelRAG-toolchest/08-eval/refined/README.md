# Cleansed Extracted Modules

**Source:** `/Users/kc/PixelRAG-toolchest/08-eval`
**Extracted:** 2026-07-08 04:29
**Extracted items:** 270
**Raw source files preserved:** 24 in `raw/`

## Analysis Summary

- **Health Score:** 60/100
- **Long Functions:** 30
- **Duplication Pairs:** 19
- **High Coupling Items:** 20
- **Potential Dead Code:** 235 items (127 high-confidence)
- **Modules (Directories):** 2
- **Cross-Module Dependencies:** 48

## Languages

- **python:** 270 items

## Contents

| Name | Type | Language | Source File | Valid |
|------|------|----------|-------------|-------|
| get_cache_dir | function | python | `benchmarks.py:51` | Yes |
| download_file | function | python | `benchmarks.py:58` | Yes |
| _bytes_to_pil | function | python | `benchmarks.py:66` | Yes |
| load_encyclopedic_vqa_data | function | python | `benchmarks.py:92` | Yes |
| load_shortformqa_data | function | python | `benchmarks.py:207` | Yes |
| load_worldvqa_data | function | python | `benchmarks.py:247` | Yes |
| load_simplevqa_data | function | python | `benchmarks.py:300` | Yes |
| load_factualvqa_data | function | python | `benchmarks.py:357` | Yes |
| load_mmsearch_data | function | python | `benchmarks.py:427` | Yes |
| load_webqa_data | function | python | `benchmarks.py:491` | Yes |
| load_multimodalqa_data | function | python | `benchmarks.py:580` | Yes |
| strip_think | function | python | `grader.py:55` | Yes |
| build_ground_truth | function | python | `grader.py:66` | Yes |
| parse_label | function | python | `grader.py:77` | Yes |
| _normalize_text | function | python | `grader.py:96` | Yes |
| is_exact_match | function | python | `grader.py:105` | Yes |
| _golds_for | function | python | `grader.py:111` | Yes |
| grade_exact_match | function | python | `grader.py:123` | Yes |
| grade_file | function | python | `grader.py:143` | Yes |
| main | function | python | `grader.py:220` | Yes |
| _build_fewshot_turns | function | python | `llm.py:125` | Yes |
| build_messages | function | python | `llm.py:156` | Yes |
| _encode_images_to_content | function | python | `llm.py:350` | Yes |
| build_react_messages | function | python | `llm.py:371` | Yes |
| LLMClient | class | python | `llm.py:453` | Yes |
| LLMClient.__init__ | method | python | `llm.py:456` | Yes |
| LLMClient.generate | method | python | `llm.py:524` | Yes |
| LLMClient._generate_gemini | method | python | `llm.py:604` | Yes |
| LLMClient._generate_openai | method | python | `llm.py:700` | Yes |
| LLMClient._estimate_tokens | method | python | `llm.py:734` | Yes |
| LLMClient._truncate_messages | method | python | `llm.py:751` | Yes |
| get_model_config | function | python | `model_config.py:10` | Yes |
| get_output_filename | function | python | `model_config.py:59` | Yes |
| _find_font | function | python | `pixel_query.py:26` | Yes |
| _wrap_text_by_pixel_width | function | python | `pixel_query.py:39` | Yes |
| PixelQueryRenderer | class | python | `pixel_query.py:63` | Yes |
| PixelQueryRenderer.__init__ | method | python | `pixel_query.py:69` | Yes |
| PixelQueryRenderer._render_image | method | python | `pixel_query.py:94` | Yes |
| PixelQueryRenderer.render | method | python | `pixel_query.py:116` | Yes |
| PixelQueryRenderer.render_all | method | python | `pixel_query.py:130` | Yes |
| QueryImageTextRenderer | class | python | `pixel_query.py:159` | Yes |
| QueryImageTextRenderer.__init__ | method | python | `pixel_query.py:171` | Yes |
| QueryImageTextRenderer._render_query_text_centered | method | python | `pixel_query.py:206` | Yes |
| QueryImageTextRenderer.render | method | python | `pixel_query.py:252` | Yes |
| RetrievalResult | class | python | `retrieval.py:22` | Yes |
| RetrievalResult.has_content | method | python | `retrieval.py:51` | No (SyntaxError: unexpected indent (line 2)) |
| BaseRetriever | class | python | `retrieval.py:56` | Yes |
| BaseRetriever.retrieve | method | python | `retrieval.py:60` | No (SyntaxError: unexpected indent (line 2)) |
| _lookup_and_copy_local_wiki_tiles | function | python | `retrieval.py:92` | Yes |
| _get_inat_image_path_for_example | function | python | `retrieval.py:184` | Yes |
| _get_landmark_image_path_for_example | function | python | `retrieval.py:214` | Yes |
| _try_download_landmark_from_url | function | python | `retrieval.py:256` | Yes |
| _get_query_image_path_for_example | function | python | `retrieval.py:293` | Yes |
| _get_all_inat_image_paths | function | python | `retrieval.py:306` | Yes |
| _load_landmark_url_map | function | python | `retrieval.py:340` | Yes |
| _download_landmark_image_by_id | function | python | `retrieval.py:363` | Yes |
| _get_all_landmark_image_paths | function | python | `retrieval.py:384` | Yes |
| _get_all_query_image_paths | function | python | `retrieval.py:418` | Yes |
| NaiveRetriever | class | python | `retrieval.py:451` | Yes |
| NaiveRetriever.retrieve | method | python | `retrieval.py:454` | Yes |
| EVQANoRetrievalRetriever | class | python | `retrieval.py:458` | Yes |
| EVQANoRetrievalRetriever.__init__ | method | python | `retrieval.py:464` | Yes |
| EVQANoRetrievalRetriever.retrieve | method | python | `retrieval.py:467` | Yes |
| _save_task_query_image | function | python | `retrieval.py:477` | Yes |
| _save_worldvqa_query_image | function | python | `retrieval.py:516` | Yes |
| _worldvqa_image_to_base64 | function | python | `retrieval.py:555` | Yes |
| WorldVQANoRetrievalRetriever | class | python | `retrieval.py:574` | Yes |
| WorldVQANoRetrievalRetriever.retrieve | method | python | `retrieval.py:580` | Yes |
| ScreenshotRetriever | class | python | `retrieval.py:589` | Yes |
| ScreenshotRetriever.__init__ | method | python | `retrieval.py:609` | Yes |
| ScreenshotRetriever.retrieve | method | python | `retrieval.py:615` | Yes |
| TiledScreenshotRetriever | class | python | `retrieval.py:643` | Yes |
| TiledScreenshotRetriever.__init__ | method | python | `retrieval.py:656` | Yes |
| TiledScreenshotRetriever.retrieve | method | python | `retrieval.py:671` | Yes |
| LocalWikiTiledScreenshotRetriever | class | python | `retrieval.py:722` | Yes |
| LocalWikiTiledScreenshotRetriever.__init__ | method | python | `retrieval.py:736` | Yes |
| LocalWikiTiledScreenshotRetriever.retrieve | method | python | `retrieval.py:750` | Yes |
| TextRetriever | class | python | `retrieval.py:779` | Yes |
| TextRetriever.__init__ | method | python | `retrieval.py:785` | Yes |
| TextRetriever._save_to_cache | method | python | `retrieval.py:796` | Yes |
| TextRetriever.retrieve | method | python | `retrieval.py:810` | Yes |
| JinaReaderRetriever | class | python | `retrieval.py:829` | Yes |
| JinaReaderRetriever.__init__ | method | python | `retrieval.py:835` | Yes |
| JinaReaderRetriever._save_to_cache | method | python | `retrieval.py:848` | Yes |
| JinaReaderRetriever.retrieve | method | python | `retrieval.py:862` | Yes |
| WikipediaAPIRetriever | class | python | `retrieval.py:1010` | Yes |
| WikipediaAPIRetriever.__init__ | method | python | `retrieval.py:1017` | Yes |
| WikipediaAPIRetriever._save_to_cache | method | python | `retrieval.py:1028` | Yes |
| WikipediaAPIRetriever._extract_wiki_title | method | python | `retrieval.py:1042` | Yes |
| WikipediaAPIRetriever._get_wiki_lang | method | python | `retrieval.py:1059` | Yes |
| WikipediaAPIRetriever._html_to_text | method | python | `retrieval.py:1066` | Yes |
| WikipediaAPIRetriever._parse_infobox | method | python | `retrieval.py:1093` | Yes |
| WikipediaAPIRetriever.retrieve | method | python | `retrieval.py:1155` | Yes |
| VectorRetriever | class | python | `retrieval.py:1265` | Yes |
| VectorRetriever.__init__ | method | python | `retrieval.py:1271` | Yes |
| VectorRetriever._prepare_screenshots | method | python | `retrieval.py:1313` | Yes |
| VectorRetriever.retrieve | method | python | `retrieval.py:1360` | Yes |
| ColQwenVectorRetriever | class | python | `retrieval.py:1376` | Yes |
| ColQwenVectorRetriever.__init__ | method | python | `retrieval.py:1379` | Yes |
| ColQwenVectorRetriever._get_example_image_paths | method | python | `retrieval.py:1453` | Yes |
| ColQwenVectorRetriever.retrieve | method | python | `retrieval.py:1465` | Yes |
| _filter_tiles_by_aspect_ratio | function | python | `retrieval.py:1481` | Yes |
| TiledVectorRetriever | class | python | `retrieval.py:1514` | Yes |
| TiledVectorRetriever.__init__ | method | python | `retrieval.py:1521` | Yes |
| TiledVectorRetriever._prepare_screenshots_and_tiles | method | python | `retrieval.py:1578` | Yes |
| TiledVectorRetriever._extract_urls_from_results | method | python | `retrieval.py:1624` | Yes |
| TiledVectorRetriever.retrieve | method | python | `retrieval.py:1646` | Yes |
| TiledColQwenVectorRetriever | class | python | `retrieval.py:1666` | Yes |
| TiledColQwenVectorRetriever.__init__ | method | python | `retrieval.py:1673` | Yes |
| TiledColQwenVectorRetriever._prepare_screenshots_and_tiles | method | python | `retrieval.py:1741` | Yes |
| TiledColQwenVectorRetriever._extract_urls_from_results | method | python | `retrieval.py:1787` | Yes |
| TiledColQwenVectorRetriever.retrieve | method | python | `retrieval.py:1807` | Yes |
| TextVectorRetriever | class | python | `retrieval.py:1829` | Yes |
| TextVectorRetriever.__init__ | method | python | `retrieval.py:1836` | Yes |
| TextVectorRetriever._build_index | method | python | `retrieval.py:1903` | Yes |
| TextVectorRetriever.retrieve | method | python | `retrieval.py:2004` | Yes |
| DsServeRetriever | class | python | `retrieval.py:2041` | Yes |
| DsServeRetriever.__init__ | method | python | `retrieval.py:2047` | Yes |
| DsServeRetriever.retrieve | method | python | `retrieval.py:2053` | Yes |
| LocalAPIRetriever | class | python | `retrieval.py:2157` | Yes |
| LocalAPIRetriever.__init__ | method | python | `retrieval.py:2185` | Yes |
| LocalAPIRetriever._rewrite_queries | method | python | `retrieval.py:2221` | Yes |
| LocalAPIRetriever._lookup_reference_tiles | method | python | `retrieval.py:2253` | Yes |
| LocalAPIRetriever.prefetch | method | python | `retrieval.py:2339` | Yes |
| LocalAPIRetriever._resolve_tile_path | method | python | `retrieval.py:2593` | No (SyntaxError: unexpected indent (line 2)) |
| LocalAPIRetriever._hits_to_result | method | python | `retrieval.py:2623` | No (SyntaxError: unexpected indent (line 2)) |
| LocalAPIRetriever.retrieve | method | python | `retrieval.py:2655` | Yes |
| LocalAPIRetriever.get_hits | method | python | `retrieval.py:2696` | Yes |
| TiledQwen3VLEmbeddingRetriever | class | python | `retrieval.py:2706` | Yes |
| TiledQwen3VLEmbeddingRetriever.__init__ | method | python | `retrieval.py:2716` | Yes |
| TiledQwen3VLEmbeddingRetriever._load_prebuilt_tiles | method | python | `retrieval.py:2832` | Yes |
| TiledQwen3VLEmbeddingRetriever._prepare_local_wiki_tiles | method | python | `retrieval.py:2848` | Yes |
| TiledQwen3VLEmbeddingRetriever._prepare_screenshots_and_tiles | method | python | `retrieval.py:2995` | Yes |
| TiledQwen3VLEmbeddingRetriever._extract_urls_from_results | method | python | `retrieval.py:3047` | Yes |
| TiledQwen3VLEmbeddingRetriever._load_inat2021_mapping | method | python | `retrieval.py:3072` | No (SyntaxError: unexpected indent (line 2)) |
| TiledQwen3VLEmbeddingRetriever._get_inat_image_path | method | python | `retrieval.py:3108` | Yes |
| TiledQwen3VLEmbeddingRetriever.retrieve | method | python | `retrieval.py:3112` | Yes |
| TiledQwen3VLEmbeddingRetriever._retrieve_single | method | python | `retrieval.py:3118` | Yes |
| TiledQwen3VLEmbeddingRetriever.retrieve_multi_image | method | python | `retrieval.py:3190` | Yes |
| TextAPIRetriever | class | python | `retrieval.py:3259` | Yes |
| TextAPIRetriever.__init__ | method | python | `retrieval.py:3271` | Yes |
| TextAPIRetriever.prefetch | method | python | `retrieval.py:3293` | Yes |
| TextAPIRetriever._hits_to_result | method | python | `retrieval.py:3372` | No (SyntaxError: unexpected indent (line 2)) |
| TextAPIRetriever.retrieve | method | python | `retrieval.py:3410` | Yes |
| TextAPIRetriever.get_hits | method | python | `retrieval.py:3444` | Yes |
| OCRWrappedRetriever | class | python | `retrieval.py:3454` | Yes |
| OCRWrappedRetriever.__init__ | method | python | `retrieval.py:3465` | Yes |
| OCRWrappedRetriever._load_cache | method | python | `retrieval.py:3492` | Yes |
| OCRWrappedRetriever._append_cache | method | python | `retrieval.py:3515` | Yes |
| OCRWrappedRetriever._ocr_one | method | python | `retrieval.py:3523` | Yes |
| OCRWrappedRetriever._batch_ocr | method | python | `retrieval.py:3575` | Yes |
| OCRWrappedRetriever.prefetch | method | python | `retrieval.py:3591` | Yes |
| OCRWrappedRetriever.retrieve | method | python | `retrieval.py:3613` | Yes |
| RenderedTextWrapper | class | python | `retrieval.py:3645` | Yes |
| RenderedTextWrapper.__init__ | method | python | `retrieval.py:3657` | Yes |
| RenderedTextWrapper.prefetch | method | python | `retrieval.py:3674` | Yes |
| RenderedTextWrapper._render | method | python | `retrieval.py:3678` | Yes |
| RenderedTextWrapper.retrieve | method | python | `retrieval.py:3698` | Yes |
| HybridRetriever | class | python | `retrieval.py:3723` | Yes |
| HybridRetriever.__init__ | method | python | `retrieval.py:3736` | Yes |
| HybridRetriever.prefetch | method | python | `retrieval.py:3757` | Yes |
| HybridRetriever.retrieve | method | python | `retrieval.py:3763` | Yes |
| HTMLDOMLookupRetriever | class | python | `retrieval.py:3809` | Yes |
| HTMLDOMLookupRetriever.__init__ | method | python | `retrieval.py:3824` | Yes |
| HTMLDOMLookupRetriever.prefetch | method | python | `retrieval.py:3861` | Yes |
| HTMLDOMLookupRetriever._fetch_html | method | python | `retrieval.py:3864` | Yes |
| HTMLDOMLookupRetriever._normalize | method | python | `retrieval.py:3888` | No (SyntaxError: unexpected indent (line 2)) |
| HTMLDOMLookupRetriever._dom_lookup | method | python | `retrieval.py:3900` | Yes |
| HTMLDOMLookupRetriever._find_semantic_container | method | python | `retrieval.py:4024` | Yes |
| HTMLDOMLookupRetriever._gather_section_context | method | python | `retrieval.py:4089` | Yes |
| HTMLDOMLookupRetriever._extract_search_keys | method | python | `retrieval.py:4144` | No (SyntaxError: unexpected indent (line 2)) |
| HTMLDOMLookupRetriever._llm_dom_closure | method | python | `retrieval.py:4242` | Yes |
| HTMLDOMLookupRetriever.retrieve | method | python | `retrieval.py:4288` | Yes |
| build_retriever | function | python | `retrievers.py:42` | Yes |
| setup_driver | function | python | `screenshot.py:18` | Yes |
| _capture_with_scroll | function | python | `screenshot.py:77` | Yes |
| _eager_load_images | function | python | `screenshot.py:193` | Yes |
| _wait_for_images | function | python | `screenshot.py:212` | Yes |
| _scroll_to_trigger_lazy_load | function | python | `screenshot.py:225` | Yes |
| capture_screenshot | function | python | `screenshot.py:241` | Yes |
| encode_image | function | python | `screenshot.py:309` | Yes |
| encode_image_for_vlm | function | python | `screenshot.py:365` | Yes |
| load_simpleqa_data | function | python | `simpleqa_data.py:30` | Yes |
| load_simpleqa_verified_data | function | python | `simpleqa_data.py:71` | Yes |
| load_text_cache | function | python | `simpleqa_data.py:191` | Yes |
| extract_url_from_metadata | function | python | `simpleqa_data.py:215` | Yes |
| _init_screenshot_utils | function | python | `simpleqa_data.py:296` | Yes |
| capture_screenshot_for_example | function | python | `simpleqa_data.py:314` | Yes |
| capture_screenshot_async | function | python | `simpleqa_data.py:365` | Yes |
| encode_screenshot | function | python | `simpleqa_data.py:375` | Yes |
| encode_screenshot_async | function | python | `simpleqa_data.py:404` | Yes |
| encode_screenshot_for_vlm | function | python | `simpleqa_data.py:410` | Yes |
| encode_screenshot_for_vlm_async | function | python | `simpleqa_data.py:447` | Yes |
| make_compressed_encoder | function | python | `simpleqa_data.py:462` | Yes |
| fetch_webpage_text | function | python | `simpleqa_data.py:561` | Yes |
| fetch_text_for_example | function | python | `simpleqa_data.py:601` | Yes |
| fetch_text_async | function | python | `simpleqa_data.py:633` | Yes |
| split_image_to_tiles | function | python | `simpleqa_data.py:648` | Yes |
| prepare_tiles_for_screenshots | function | python | `simpleqa_data.py:753` | Yes |
| load_nq_data | function | python | `simpleqa_data.py:792` | Yes |
| load_triviaqa_data | function | python | `simpleqa_data.py:887` | Yes |
| load_nq_tables_data | function | python | `simpleqa_data.py:978` | Yes |
| _format_mc_options | function | python | `simpleqa_data.py:1067` | Yes |
| load_piqa_data | function | python | `simpleqa_data.py:1075` | Yes |
| load_hellaswag_data | function | python | `simpleqa_data.py:1112` | Yes |
| load_commonsenseqa_data | function | python | `simpleqa_data.py:1152` | Yes |
| load_openbookqa_data | function | python | `simpleqa_data.py:1190` | Yes |
| load_arc_data | function | python | `simpleqa_data.py:1228` | Yes |
| _get_urls_from_metadata | function | python | `simpleqa_filter.py:12` | Yes |
| load_simpleqa_wikipedia | function | python | `simpleqa_filter.py:43` | Yes |
| load_simpleqa_by_domain | function | python | `simpleqa_filter.py:90` | Yes |
| _fetch_status | function | python | `run_bench.py:98` | Yes |
| _build_run_metadata | function | python | `run_bench.py:119` | Yes |
| process_example | function | python | `run_bench.py:176` | Yes |
| _local_api_search | function | python | `run_bench.py:449` | Yes |
| _hits_to_retrieval_result | function | python | `run_bench.py:475` | Yes |
| process_example_react | function | python | `run_bench.py:503` | Yes |
| print_statistics | function | python | `run_bench.py:709` | Yes |
| run_async | function | python | `run_bench.py:840` | Yes |
| main | function | python | `run_bench.py:1205` | Yes |
| load_livevqa_dataset | function | python | `run_livevqa.py:99` | Yes |
| shuffle_options | function | python | `run_livevqa.py:121` | Yes |
| extract_letter | function | python | `run_livevqa.py:140` | Yes |
| image_to_base64_url | function | python | `run_livevqa.py:156` | Yes |
| encode_image_base64 | function | python | `run_livevqa.py:166` | Yes |
| build_naive_prompt | function | python | `run_livevqa.py:177` | Yes |
| build_pixel_prompt | function | python | `run_livevqa.py:191` | Yes |
| build_text_prompt | function | python | `run_livevqa.py:204` | Yes |
| build_hybrid_prompt | function | python | `run_livevqa.py:223` | Yes |
| build_messages_for_livevqa | function | python | `run_livevqa.py:251` | Yes |
| batch_retrieve_pixel | function | python | `run_livevqa.py:281` | Yes |
| batch_retrieve_text | function | python | `run_livevqa.py:360` | Yes |
| resolve_strip_path | function | python | `run_livevqa.py:431` | Yes |
| resolve_editorial_photo | function | python | `run_livevqa.py:440` | Yes |
| resolve_pixel_context | function | python | `run_livevqa.py:456` | Yes |
| resolve_text_context | function | python | `run_livevqa.py:480` | Yes |
| _get_chunks_conn | function | python | `run_livevqa.py:527` | Yes |
| _fetch_chunk_text | function | python | `run_livevqa.py:534` | Yes |
| load_url_to_hex | function | python | `run_livevqa.py:549` | Yes |
| load_hex_to_int | function | python | `run_livevqa.py:558` | Yes |
| evaluate_one | function | python | `run_livevqa.py:568` | Yes |
| run_evaluation | function | python | `run_livevqa.py:731` | Yes |
| main | function | python | `run_livevqa.py:1049` | Yes |
| _setup_logging | function | python | `run_monaco.py:105` | Yes |
| _build_system_prompt | function | python | `run_monaco.py:161` | Yes |
| _search_text | function | python | `run_monaco.py:225` | Yes |
| _search_pixel | function | python | `run_monaco.py:256` | Yes |
| _supports_temperature | function | python | `run_monaco.py:300` | Yes |
| _is_local_model | function | python | `run_monaco.py:304` | Yes |
| _is_claude_model | function | python | `run_monaco.py:308` | Yes |
| _call_llm_openai | function | python | `run_monaco.py:312` | Yes |
| _openai_tool_to_claude | function | python | `run_monaco.py:361` | Yes |
| _openai_msgs_to_claude | function | python | `run_monaco.py:370` | Yes |
| _claude_response_to_openai | function | python | `run_monaco.py:481` | Yes |
| _call_llm_claude | function | python | `run_monaco.py:504` | Yes |
| _call_llm_forced_openai | function | python | `run_monaco.py:542` | Yes |
| _call_llm_forced_claude | function | python | `run_monaco.py:569` | Yes |
| react_loop | function | python | `run_monaco.py:599` | Yes |
| parse_answer | function | python | `run_monaco.py:718` | Yes |
| normalize_answer | function | python | `run_monaco.py:731` | Yes |
| token_f1 | function | python | `run_monaco.py:748` | Yes |
| exact_match | function | python | `run_monaco.py:763` | Yes |
| grade_monaco | function | python | `run_monaco.py:767` | Yes |
| process_one | function | python | `run_monaco.py:807` | Yes |
| load_monaco | function | python | `run_monaco.py:875` | Yes |
| _gold_length | function | python | `run_monaco.py:921` | Yes |
| _parse_judge_response | function | python | `run_monaco.py:930` | Yes |
| _judge_f1 | function | python | `run_monaco.py:943` | Yes |
| judge_one | function | python | `run_monaco.py:958` | Yes |
| main | function | python | `run_monaco.py:1013` | Yes |

## Validation

- **has_content**: SyntaxError: unexpected indent (line 2)
- **retrieve**: SyntaxError: unexpected indent (line 2)
- **_resolve_tile_path**: SyntaxError: unexpected indent (line 2)
- **_hits_to_result**: SyntaxError: unexpected indent (line 2)
- **_load_inat2021_mapping**: SyntaxError: unexpected indent (line 2)
- **_hits_to_result**: SyntaxError: unexpected indent (line 2)
- **_normalize**: SyntaxError: unexpected indent (line 2)
- **_extract_search_keys**: SyntaxError: unexpected indent (line 2)

## Raw Source

All 24 original source files are preserved in the `raw/` directory, 
organized with the same directory structure as the original project. 
This includes both code files and non-code assets (images, configs, binaries) 
that were not extracted as modules.

---
Generated by Cleansed v1.0.0
