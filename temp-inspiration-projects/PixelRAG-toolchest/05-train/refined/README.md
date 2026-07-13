# Cleansed Extracted Modules

**Source:** `/Users/kc/PixelRAG-toolchest/05-train`
**Extracted:** 2026-07-08 04:28
**Extracted items:** 352
**Raw source files preserved:** 137 in `raw/`

## Analysis Summary

- **Health Score:** 49/100
- **Long Functions:** 30
- **Duplication Pairs:** 20
- **High Coupling Items:** 20
- **Potential Dead Code:** 335 items (240 high-confidence)
- **Modules (Directories):** 4
- **Cross-Module Dependencies:** 15

## Languages

- **python:** 352 items

## Contents

| Name | Type | Language | Source File | Valid |
|------|------|----------|-------------|-------|
| main | function | python | `build_test_miniv8.py:22` | Yes |
| parse_args | function | python | `clean_queries_simpleqa_style.py:46` | Yes |
| init_usage | function | python | `clean_queries_simpleqa_style.py:137` | Yes |
| build_client | function | python | `clean_queries_simpleqa_style.py:145` | Yes |
| update_usage | function | python | `clean_queries_simpleqa_style.py:161` | Yes |
| parse_json_from_text | function | python | `clean_queries_simpleqa_style.py:170` | Yes |
| call_gemini_json | function | python | `clean_queries_simpleqa_style.py:186` | Yes |
| iter_rows | function | python | `clean_queries_simpleqa_style.py:217` | Yes |
| load_input_rows | function | python | `clean_queries_simpleqa_style.py:226` | Yes |
| normalize_query | function | python | `clean_queries_simpleqa_style.py:253` | Yes |
| question_start_bucket | function | python | `clean_queries_simpleqa_style.py:257` | Yes |
| load_simpleqa_references | function | python | `clean_queries_simpleqa_style.py:279` | Yes |
| build_prompt | function | python | `clean_queries_simpleqa_style.py:318` | Yes |
| sanitize_decision | function | python | `clean_queries_simpleqa_style.py:374` | Yes |
| score_batch | function | python | `clean_queries_simpleqa_style.py:400` | Yes |
| load_existing_reviews | function | python | `clean_queries_simpleqa_style.py:432` | Yes |
| review_rows | function | python | `clean_queries_simpleqa_style.py:446` | Yes |
| candidate_priority | function | python | `clean_queries_simpleqa_style.py:514` | Yes |
| select_rows | function | python | `clean_queries_simpleqa_style.py:524` | Yes |
| word_count | function | python | `clean_queries_simpleqa_style.py:559` | Yes |
| compute_query_stats | function | python | `clean_queries_simpleqa_style.py:563` | Yes |
| estimated_cost_usd | function | python | `clean_queries_simpleqa_style.py:591` | Yes |
| write_jsonl | function | python | `clean_queries_simpleqa_style.py:600` | Yes |
| main | function | python | `clean_queries_simpleqa_style.py:607` | Yes |
| convert_line | function | python | `convert_data_for_swift.py:42` | Yes |
| main | function | python | `convert_data_for_swift.py:79` | Yes |
| QueryChunkDataset | class | python | `dataset.py:18` | Yes |
| QueryChunkDataset.__init__ | method | python | `dataset.py:21` | Yes |
| QueryChunkDataset.__len__ | method | python | `dataset.py:29` | Yes |
| QueryChunkDataset.__getitem__ | method | python | `dataset.py:32` | Yes |
| make_collate_fn | function | python | `dataset.py:36` | Yes |
| main | function | python | `eval_checkpoint.py:11` | Yes |
| _chunk | function | python | `evaluate.py:18` | Yes |
| run_eval | function | python | `evaluate.py:23` | Yes |
| parse_args | function | python | `export_natural_filtered_v2.py:12` | Yes |
| main | function | python | `export_natural_filtered_v2.py:34` | Yes |
| parse_args | function | python | `export_natural_filtered_v2_with_answer.py:25` | Yes |
| normalize_source_chunk_path | function | python | `export_natural_filtered_v2_with_answer.py:35` | Yes |
| iter_jsonl | function | python | `export_natural_filtered_v2_with_answer.py:42` | Yes |
| main | function | python | `export_natural_filtered_v2_with_answer.py:50` | Yes |
| parse_args | function | python | `extract_hf_image_shards.py:11` | Yes |
| main | function | python | `extract_hf_image_shards.py:29` | Yes |
| find_chunk_paths | function | python | `fake_data.py:32` | Yes |
| title_from_slug | function | python | `fake_data.py:60` | Yes |
| generate_queries | function | python | `fake_data.py:68` | Yes |
| main | function | python | `fake_data.py:73` | Yes |
| classify_batch | function | python | `filter_entity_queries.py:64` | Yes |
| main | function | python | `filter_entity_queries.py:104` | Yes |
| classify_batch | function | python | `filter_hard.py:78` | Yes |
| parse_pos | function | python | `filter_hard.py:118` | Yes |
| main | function | python | `filter_hard.py:123` | Yes |
| MissingImageError | class | python | `filter_hard_negatives_vqa.py:72` | Yes |
| ApiRequestError | class | python | `filter_hard_negatives_vqa.py:76` | Yes |
| init_token_usage | function | python | `filter_hard_negatives_vqa.py:80` | Yes |
| parse_args | function | python | `filter_hard_negatives_vqa.py:88` | Yes |
| iter_jsonl | function | python | `filter_hard_negatives_vqa.py:144` | Yes |
| encode_image_as_data_url | function | python | `filter_hard_negatives_vqa.py:159` | Yes |
| infer_image_mime | function | python | `filter_hard_negatives_vqa.py:170` | Yes |
| encode_image_base64 | function | python | `filter_hard_negatives_vqa.py:175` | Yes |
| update_usage | function | python | `filter_hard_negatives_vqa.py:183` | Yes |
| build_vlm_client | function | python | `filter_hard_negatives_vqa.py:192` | Yes |
| call_openai_chat_completions | function | python | `filter_hard_negatives_vqa.py:220` | Yes |
| call_gemini_generate_content | function | python | `filter_hard_negatives_vqa.py:264` | Yes |
| call_vlm | function | python | `filter_hard_negatives_vqa.py:323` | Yes |
| answer_question | function | python | `filter_hard_negatives_vqa.py:335` | Yes |
| judge_answer | function | python | `filter_hard_negatives_vqa.py:342` | Yes |
| normalize_answer | function | python | `filter_hard_negatives_vqa.py:382` | Yes |
| init_counts | function | python | `filter_hard_negatives_vqa.py:386` | Yes |
| get_candidates | function | python | `filter_hard_negatives_vqa.py:407` | Yes |
| append_jsonl | function | python | `filter_hard_negatives_vqa.py:419` | Yes |
| write_summary | function | python | `filter_hard_negatives_vqa.py:424` | Yes |
| path_exists | function | python | `filter_hard_negatives_vqa.py:431` | Yes |
| process_example | function | python | `filter_hard_negatives_vqa.py:442` | Yes |
| merge_counts | function | python | `filter_hard_negatives_vqa.py:742` | Yes |
| build_usage_summary | function | python | `filter_hard_negatives_vqa.py:754` | Yes |
| main | function | python | `filter_hard_negatives_vqa.py:771` | Yes |
| classify_batch | function | python | `filter_passage.py:62` | Yes |
| main | function | python | `filter_passage.py:102` | Yes |
| parse_batch_response | function | python | `filter_self_contained.py:81` | Yes |
| classify_batch | function | python | `filter_self_contained.py:98` | Yes |
| main | function | python | `filter_self_contained.py:137` | Yes |
| parse_chunk_position | function | python | `filter_strict.py:46` | Yes |
| rule_filter | function | python | `filter_strict.py:54` | Yes |
| classify_batch | function | python | `filter_strict.py:108` | Yes |
| main | function | python | `filter_strict.py:150` | Yes |
| ApiRequestError | class | python | `filter_text_hard_negatives_llm.py:82` | Yes |
| parse_args | function | python | `filter_text_hard_negatives_llm.py:86` | Yes |
| iter_jsonl | function | python | `filter_text_hard_negatives_llm.py:130` | Yes |
| init_token_usage | function | python | `filter_text_hard_negatives_llm.py:145` | Yes |
| update_usage | function | python | `filter_text_hard_negatives_llm.py:153` | Yes |
| build_text_client | function | python | `filter_text_hard_negatives_llm.py:162` | Yes |
| call_openai_chat_completions | function | python | `filter_text_hard_negatives_llm.py:190` | Yes |
| call_gemini_generate_content | function | python | `filter_text_hard_negatives_llm.py:223` | Yes |
| call_text_llm | function | python | `filter_text_hard_negatives_llm.py:266` | Yes |
| answer_question | function | python | `filter_text_hard_negatives_llm.py:272` | Yes |
| judge_answer | function | python | `filter_text_hard_negatives_llm.py:279` | Yes |
| normalize_answer | function | python | `filter_text_hard_negatives_llm.py:315` | Yes |
| init_counts | function | python | `filter_text_hard_negatives_llm.py:319` | Yes |
| get_candidates | function | python | `filter_text_hard_negatives_llm.py:330` | Yes |
| append_jsonl | function | python | `filter_text_hard_negatives_llm.py:343` | Yes |
| write_summary | function | python | `filter_text_hard_negatives_llm.py:348` | Yes |
| build_usage_summary | function | python | `filter_text_hard_negatives_llm.py:355` | Yes |
| process_example | function | python | `filter_text_hard_negatives_llm.py:372` | Yes |
| merge_counts | function | python | `filter_text_hard_negatives_llm.py:533` | Yes |
| main | function | python | `filter_text_hard_negatives_llm.py:540` | Yes |
| parse_chunk_pos | function | python | `filter_v2.py:26` | Yes |
| has_specific_signal | function | python | `filter_v2.py:80` | Yes |
| has_generic_signal | function | python | `filter_v2.py:84` | Yes |
| gpt41_batch | function | python | `filter_v2.py:111` | Yes |
| main | function | python | `filter_v2.py:151` | Yes |
| get_page_chunk_count | function | python | `generate_query_pairs.py:146` | Yes |
| is_informative_page | function | python | `generate_query_pairs.py:165` | Yes |
| is_natural_question | function | python | `generate_query_pairs.py:187` | Yes |
| load_and_sample_pages | function | python | `generate_query_pairs.py:208` | Yes |
| filter_selected_pages_by_chunk_count | function | python | `generate_query_pairs.py:241` | Yes |
| pick_random_chunk | function | python | `generate_query_pairs.py:261` | Yes |
| encode_image | function | python | `generate_query_pairs.py:285` | Yes |
| generate_qa | function | python | `generate_query_pairs.py:363` | Yes |
| main | function | python | `generate_query_pairs.py:462` | Yes |
| parse_args | function | python | `generate_text_query_pairs.py:153` | Yes |
| normalize_text | function | python | `generate_text_query_pairs.py:184` | Yes |
| infer_title | function | python | `generate_text_query_pairs.py:188` | Yes |
| is_bad_title | function | python | `generate_text_query_pairs.py:196` | Yes |
| is_candidate_passage | function | python | `generate_text_query_pairs.py:209` | Yes |
| split_paragraphs | function | python | `generate_text_query_pairs.py:223` | Yes |
| is_list_like_paragraph | function | python | `generate_text_query_pairs.py:227` | Yes |
| extract_best_long_paragraph | function | python | `generate_text_query_pairs.py:250` | Yes |
| load_fewshot_examples | function | python | `generate_text_query_pairs.py:276` | Yes |
| format_fewshot_block | function | python | `generate_text_query_pairs.py:283` | Yes |
| build_prompt | function | python | `generate_text_query_pairs.py:301` | Yes |
| parse_model_output | function | python | `generate_text_query_pairs.py:353` | Yes |
| call_gemini | function | python | `generate_text_query_pairs.py:382` | Yes |
| call_openai_fallback | function | python | `generate_text_query_pairs.py:414` | Yes |
| is_natural_question | function | python | `generate_text_query_pairs.py:435` | Yes |
| load_candidate_articles | function | python | `generate_text_query_pairs.py:459` | Yes |
| select_chunk_rows | function | python | `generate_text_query_pairs.py:503` | Yes |
| generate_qa | function | python | `generate_text_query_pairs.py:560` | Yes |
| main | function | python | `generate_text_query_pairs.py:648` | Yes |
| search_batch | function | python | `mine_hard_negatives.py:39` | Yes |
| mine_from_search | function | python | `mine_hard_negatives.py:54` | Yes |
| main | function | python | `mine_hard_negatives.py:242` | Yes |
| search_batch | function | python | `mine_text_hard_negatives.py:34` | Yes |
| positive_key | function | python | `mine_text_hard_negatives.py:45` | Yes |
| hit_key | function | python | `mine_text_hard_negatives.py:51` | Yes |
| normalize_hit | function | python | `mine_text_hard_negatives.py:55` | Yes |
| mine_from_search | function | python | `mine_text_hard_negatives.py:69` | Yes |
| parse_args | function | python | `mine_text_hard_negatives.py:199` | Yes |
| main | function | python | `mine_text_hard_negatives.py:221` | Yes |
| load_model_for_training | function | python | `model.py:10` | Yes |
| load_processor | function | python | `model.py:41` | Yes |
| pool_and_normalize | function | python | `model.py:58` | Yes |
| _remap_keys | function | python | `biqwen3.py:24` | Yes |
| BiQwen3 | class | python | `biqwen3.py:40` | Yes |
| BiQwen3.__init__ | method | python | `biqwen3.py:45` | Yes |
| BiQwen3.from_pretrained | method | python | `biqwen3.py:62` | No (SyntaxError: unexpected indent (line 2)) |
| BiQwen3.forward | method | python | `biqwen3.py:130` | Yes |
| BiQwen3.patch_size | method | python | `biqwen3.py:196` | No (SyntaxError: unexpected indent (line 2)) |
| BiQwen3.spatial_merge_size | method | python | `biqwen3.py:200` | No (SyntaxError: unexpected indent (line 2)) |
| parse_args | function | python | `package_hf_image_shards.py:21` | Yes |
| copy_metadata | function | python | `package_hf_image_shards.py:33` | Yes |
| pack_one_shard | function | python | `package_hf_image_shards.py:42` | Yes |
| build_readme | function | python | `package_hf_image_shards.py:55` | Yes |
| main | function | python | `package_hf_image_shards.py:77` | Yes |
| parse_args | function | python | `prepare_hf_dataset.py:40` | Yes |
| read_jsonl | function | python | `prepare_hf_dataset.py:59` | Yes |
| write_jsonl | function | python | `prepare_hf_dataset.py:69` | Yes |
| to_relative_image_path | function | python | `prepare_hf_dataset.py:75` | Yes |
| materialize_image | function | python | `prepare_hf_dataset.py:80` | Yes |
| transform_rows | function | python | `prepare_hf_dataset.py:93` | Yes |
| build_readme | function | python | `prepare_hf_dataset.py:135` | Yes |
| main | function | python | `prepare_hf_dataset.py:186` | Yes |
| parse_args | function | python | `prepare_hf_dataset_single_jsonl.py:34` | Yes |
| read_jsonl | function | python | `prepare_hf_dataset_single_jsonl.py:58` | Yes |
| write_jsonl | function | python | `prepare_hf_dataset_single_jsonl.py:66` | Yes |
| to_relative_image_path | function | python | `prepare_hf_dataset_single_jsonl.py:72` | Yes |
| materialize_image | function | python | `prepare_hf_dataset_single_jsonl.py:77` | Yes |
| build_readme | function | python | `prepare_hf_dataset_single_jsonl.py:90` | Yes |
| main | function | python | `prepare_hf_dataset_single_jsonl.py:141` | Yes |
| parse_args | function | python | `run_filter_hard_negatives_chunks.py:17` | Yes |
| count_lines | function | python | `run_filter_hard_negatives_chunks.py:61` | Yes |
| chunk_dir | function | python | `run_filter_hard_negatives_chunks.py:66` | Yes |
| main | function | python | `run_filter_hard_negatives_chunks.py:70` | Yes |
| parse_args | function | python | `run_filter_text_hard_negatives_chunks.py:17` | Yes |
| count_lines | function | python | `run_filter_text_hard_negatives_chunks.py:55` | Yes |
| chunk_dir | function | python | `run_filter_text_hard_negatives_chunks.py:60` | Yes |
| main | function | python | `run_filter_text_hard_negatives_chunks.py:64` | Yes |
| shard_suffix | function | python | `download_tiles.py:29` | Yes |
| collect_paths | function | python | `download_tiles.py:37` | Yes |
| try_local_link | function | python | `download_tiles.py:66` | Yes |
| fetch_tile | function | python | `download_tiles.py:86` | Yes |
| main | function | python | `download_tiles.py:114` | Yes |
| _resolve_image_path | function | python | `eval_baseline.py:52` | Yes |
| run_inference | function | python | `eval_baseline.py:61` | Yes |
| compute_em_char | function | python | `eval_baseline.py:129` | Yes |
| grade_with_gpt | function | python | `eval_baseline.py:153` | Yes |
| main | function | python | `eval_baseline.py:205` | Yes |
| strip_image_tokens | function | python | `eval_multiimage.py:47` | Yes |
| run_inference | function | python | `eval_multiimage.py:51` | Yes |
| compute_em_char | function | python | `eval_multiimage.py:115` | Yes |
| grade_with_gpt | function | python | `eval_multiimage.py:139` | Yes |
| main | function | python | `eval_multiimage.py:189` | Yes |
| shard_suffix | function | python | `fetch_top6_retrieval.py:33` | Yes |
| search_batch | function | python | `fetch_top6_retrieval.py:41` | Yes |
| process_split | function | python | `fetch_top6_retrieval.py:68` | Yes |
| _collect_stats | function | python | `fetch_top6_retrieval.py:188` | Yes |
| main | function | python | `fetch_top6_retrieval.py:214` | Yes |
| process_one | function | python | `generate_think_traces.py:32` | Yes |
| main | function | python | `generate_think_traces.py:51` | Yes |
| encode_image | function | python | `generate_think_traces_v2.py:31` | Yes |
| process_one | function | python | `generate_think_traces_v2.py:61` | Yes |
| main | function | python | `generate_think_traces_v2.py:95` | Yes |
| encode_image | function | python | `generate_think_traces_v3_highdetail.py:31` | Yes |
| process_one | function | python | `generate_think_traces_v3_highdetail.py:61` | Yes |
| main | function | python | `generate_think_traces_v3_highdetail.py:95` | Yes |
| main | function | python | `prepare_mixed_data.py:23` | Yes |
| compress_image | function | python | `prepare_sft_data.py:31` | Yes |
| main | function | python | `prepare_sft_data.py:48` | Yes |
| shard_suffix | function | python | `prepare_sft_data_multiimage.py:37` | Yes |
| compress_image | function | python | `prepare_sft_data_multiimage.py:45` | Yes |
| build_image_set | function | python | `prepare_sft_data_multiimage.py:61` | Yes |
| main | function | python | `prepare_sft_data_multiimage.py:78` | Yes |
| compress_then_upscale | function | python | `prepare_sft_data_upscale.py:22` | Yes |
| main | function | python | `prepare_sft_data_upscale.py:42` | Yes |
| shard_suffix | function | python | `prepare_sft_data_variable.py:24` | Yes |
| build_variable_image_set | function | python | `prepare_sft_data_variable.py:32` | Yes |
| main | function | python | `prepare_sft_data_variable.py:48` | Yes |
| format_assistant | function | python | `prepare_think_data.py:24` | Yes |
| main | function | python | `prepare_think_data.py:29` | Yes |
| main | function | python | `push_3x_v5_snapshot.py:179` | Yes |
| build_readme | function | python | `push_multi3_to_hf.py:72` | Yes |
| push_one | function | python | `push_multi3_to_hf.py:158` | Yes |
| main | function | python | `push_multi3_to_hf.py:190` | Yes |
| build_readme | function | python | `push_multik_to_hf.py:74` | Yes |
| push_one | function | python | `push_multik_to_hf.py:184` | Yes |
| main | function | python | `push_multik_to_hf.py:216` | Yes |
| build_readme | function | python | `push_to_hf.py:59` | Yes |
| push_one | function | python | `push_to_hf.py:131` | Yes |
| main | function | python | `push_to_hf.py:169` | Yes |
| main | function | python | `push_universal_to_hf.py:120` | Yes |
| parse_args | function | python | `split_first5_chunks.py:31` | Yes |
| read_jsonl | function | python | `split_first5_chunks.py:51` | Yes |
| write_jsonl | function | python | `split_first5_chunks.py:61` | Yes |
| main | function | python | `split_first5_chunks.py:67` | Yes |
| chunked_reference_forward_backward | function | python | `test_grad_equivalence.py:41` | Yes |
| make_fake_inputs | function | python | `test_grad_equivalence.py:71` | Yes |
| collect_grads | function | python | `test_grad_equivalence.py:91` | Yes |
| compare_gradients | function | python | `test_grad_equivalence.py:104` | Yes |
| run_test | function | python | `test_grad_equivalence.py:156` | Yes |
| main | function | python | `test_grad_equivalence.py:231` | Yes |
| multi_gpu_reference | function | python | `test_grad_multi_gpu.py:39` | Yes |
| make_rank_data | function | python | `test_grad_multi_gpu.py:78` | Yes |
| collect_grads | function | python | `test_grad_multi_gpu.py:101` | Yes |
| compare_grads | function | python | `test_grad_multi_gpu.py:113` | Yes |
| main | function | python | `test_grad_multi_gpu.py:136` | Yes |
| find_test_image | function | python | `test_swift_equivalence.py:37` | Yes |
| test_tokenization | function | python | `test_swift_equivalence.py:56` | Yes |
| test_embedding | function | python | `test_swift_equivalence.py:116` | Yes |
| test_loss | function | python | `test_swift_equivalence.py:247` | Yes |
| test_lora_targets | function | python | `test_swift_equivalence.py:292` | Yes |
| test_hard_negative_labels | function | python | `test_swift_equivalence.py:383` | Yes |
| test_data_pipeline | function | python | `test_swift_equivalence.py:460` | Yes |
| test_training_step | function | python | `test_swift_equivalence.py:593` | Yes |
| test_gather_semantics | function | python | `test_swift_equivalence.py:726` | Yes |
| test_multi_gpu_gather | function | python | `test_swift_equivalence.py:795` | Yes |
| main | function | python | `test_swift_equivalence.py:917` | Yes |
| _log | function | python | `train.py:39` | Yes |
| info_nce_loss | function | python | `train.py:57` | Yes |
| save_checkpoint | function | python | `train.py:71` | Yes |
| train | function | python | `train.py:93` | Yes |
| main | function | python | `train.py:304` | Yes |
| RandContext | class | python | `train_contrastors.py:72` | Yes |
| RandContext.__init__ | method | python | `train_contrastors.py:75` | Yes |
| RandContext.__enter__ | method | python | `train_contrastors.py:81` | Yes |
| RandContext.__exit__ | method | python | `train_contrastors.py:87` | Yes |
| gather_with_grad | function | python | `train_contrastors.py:92` | Yes |
| LogitScale | class | python | `train_contrastors.py:101` | Yes |
| LogitScale.__init__ | method | python | `train_contrastors.py:110` | Yes |
| LogitScale.forward | method | python | `train_contrastors.py:115` | Yes |
| LogitScale.clamp_ | method | python | `train_contrastors.py:119` | No (SyntaxError: unexpected indent (line 2)) |
| EMAModel | class | python | `train_contrastors.py:124` | Yes |
| EMAModel.__init__ | method | python | `train_contrastors.py:127` | Yes |
| EMAModel.update | method | python | `train_contrastors.py:134` | No (SyntaxError: unexpected indent (line 2)) |
| EMAModel.apply | method | python | `train_contrastors.py:139` | Yes |
| EMAModel.restore | method | python | `train_contrastors.py:147` | Yes |
| siglip_loss | function | python | `train_contrastors.py:155` | Yes |
| clip_loss | function | python | `train_contrastors.py:206` | Yes |
| get_chunked_embeddings | function | python | `train_contrastors.py:274` | Yes |
| grad_cache_loss | function | python | `train_contrastors.py:289` | Yes |
| manual_all_reduce_grads | function | python | `train_contrastors.py:380` | Yes |
| debug_trace | function | python | `train_contrastors.py:391` | Yes |
| build_openai_client | function | python | `train_contrastors.py:399` | Yes |
| preflight_simpleqa_client | function | python | `train_contrastors.py:417` | Yes |
| grad_cache_loss_query_side | function | python | `train_contrastors.py:431` | Yes |
| direct_loss_query_side | function | python | `train_contrastors.py:504` | Yes |
| QueryImageDataset | class | python | `train_contrastors.py:549` | Yes |
| QueryImageDataset.__init__ | method | python | `train_contrastors.py:561` | Yes |
| QueryImageDataset.__len__ | method | python | `train_contrastors.py:627` | Yes |
| QueryImageDataset.__getitem__ | method | python | `train_contrastors.py:630` | Yes |
| MixedBatchSampler | class | python | `train_contrastors.py:634` | Yes |
| MixedBatchSampler.__init__ | method | python | `train_contrastors.py:648` | Yes |
| MixedBatchSampler.set_epoch | method | python | `train_contrastors.py:661` | Yes |
| MixedBatchSampler.__iter__ | method | python | `train_contrastors.py:664` | Yes |
| MixedBatchSampler.__len__ | method | python | `train_contrastors.py:688` | Yes |
| TextQueryDataset | class | python | `train_contrastors.py:692` | Yes |
| TextQueryDataset.__init__ | method | python | `train_contrastors.py:698` | Yes |
| TextQueryDataset.__len__ | method | python | `train_contrastors.py:732` | Yes |
| TextQueryDataset.__getitem__ | method | python | `train_contrastors.py:735` | Yes |
| init_chat_templates | function | python | `train_contrastors.py:751` | Yes |
| process_queries | function | python | `train_contrastors.py:794` | Yes |
| process_doc_texts | function | python | `train_contrastors.py:800` | Yes |
| process_doc_images | function | python | `train_contrastors.py:806` | Yes |
| make_text_collate_fn | function | python | `train_contrastors.py:828` | Yes |
| make_collate_fn | function | python | `train_contrastors.py:847` | Yes |
| _clear_rope_deltas | function | python | `train_contrastors.py:896` | Yes |
| forward_query | function | python | `train_contrastors.py:912` | Yes |
| forward_doc | function | python | `train_contrastors.py:918` | Yes |
| chunk_inputs | function | python | `train_contrastors.py:924` | Yes |
| compute_retrieval_metrics | function | python | `train_contrastors.py:957` | Yes |
| resolve_jsonl_path | function | python | `train_contrastors.py:985` | Yes |
| wikipedia_url_to_slug | function | python | `train_contrastors.py:993` | Yes |
| load_slug_to_article_id | function | python | `train_contrastors.py:1003` | Yes |
| load_retrieval_queries | function | python | `train_contrastors.py:1010` | Yes |
| load_simpleqa_queryset | function | python | `train_contrastors.py:1029` | Yes |
| embed_query_texts | function | python | `train_contrastors.py:1066` | Yes |
| fetch_tile_image | function | python | `train_contrastors.py:1083` | Yes |
| search_api_by_embeddings | function | python | `train_contrastors.py:1110` | Yes |
| run_search_api_retrieval_eval | function | python | `train_contrastors.py:1137` | Yes |
| run_simpleqa_search_api_eval | function | python | `train_contrastors.py:1207` | Yes |
| run_miniv6_eval | function | python | `train_contrastors.py:1479` | Yes |
| main | function | python | `train_contrastors.py:1762` | Yes |
| main | function | python | `train_swift.py:45` | Yes |
| parse_args | function | python | `upload_hf_dataset.py:19` | Yes |
| retry_on_429 | function | python | `upload_hf_dataset.py:33` | Yes |
| main | function | python | `upload_hf_dataset.py:49` | Yes |
| parse_args | function | python | `upload_test_miniv6.py:21` | Yes |
| retry_on_429 | function | python | `upload_test_miniv6.py:30` | Yes |
| main | function | python | `upload_test_miniv6.py:45` | Yes |
| parse_args | function | python | `upload_test_miniv7.py:21` | Yes |
| retry_on_429 | function | python | `upload_test_miniv7.py:30` | Yes |
| main | function | python | `upload_test_miniv7.py:45` | Yes |
| parse_args | function | python | `upload_test_miniv8.py:21` | Yes |
| retry_on_429 | function | python | `upload_test_miniv8.py:30` | Yes |
| main | function | python | `upload_test_miniv8.py:45` | Yes |
| validate_row | function | python | `validate_images.py:22` | Yes |
| main | function | python | `validate_images.py:56` | Yes |
| load_model_and_processor | function | python | `verify_embeddings.py:31` | Yes |
| _process_queries | function | python | `verify_embeddings.py:62` | Yes |
| _process_doc_images | function | python | `verify_embeddings.py:80` | Yes |
| embed_queries | function | python | `verify_embeddings.py:95` | Yes |
| embed_images | function | python | `verify_embeddings.py:107` | Yes |
| compute_metrics | function | python | `verify_embeddings.py:119` | Yes |
| main | function | python | `verify_embeddings.py:155` | Yes |

## Validation

- **from_pretrained**: SyntaxError: unexpected indent (line 2)
- **patch_size**: SyntaxError: unexpected indent (line 2)
- **spatial_merge_size**: SyntaxError: unexpected indent (line 2)
- **clamp_**: SyntaxError: unexpected indent (line 2)
- **update**: SyntaxError: unexpected indent (line 2)

## Raw Source

All 137 original source files are preserved in the `raw/` directory, 
organized with the same directory structure as the original project. 
This includes both code files and non-code assets (images, configs, binaries) 
that were not extracted as modules.

---
Generated by Cleansed v1.0.0
