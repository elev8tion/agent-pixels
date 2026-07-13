# Cleansed Extracted Modules

**Source:** `/Users/kc/PixelRAG-toolchest/03-index`
**Extracted:** 2026-07-08 04:28
**Extracted items:** 80
**Raw source files preserved:** 12 in `raw/`

## Analysis Summary

- **Health Score:** 56/100
- **Long Functions:** 30
- **Duplication Pairs:** 6
- **High Coupling Items:** 20
- **Potential Dead Code:** 70 items (15 high-confidence)
- **Modules (Directories):** 1
- **Cross-Module Dependencies:** 0

## Languages

- **python:** 80 items

## Contents

| Name | Type | Language | Source File | Valid |
|------|------|----------|-------------|-------|
| load_config | function | python | `config.py:17` | Yes |
| make_source | function | python | `config.py:31` | Yes |
| S3ShardCoordinator | class | python | `distributed.py:29` | Yes |
| S3ShardCoordinator.__init__ | method | python | `distributed.py:40` | Yes |
| S3ShardCoordinator.load_manifest | method | python | `distributed.py:68` | Yes |
| S3ShardCoordinator.claim_next | method | python | `distributed.py:85` | Yes |
| S3ShardCoordinator.heartbeat | method | python | `distributed.py:200` | Yes |
| S3ShardCoordinator.mark_done | method | python | `distributed.py:239` | Yes |
| S3ShardCoordinator.mark_partial | method | python | `distributed.py:296` | Yes |
| S3ShardCoordinator.get_all_claims | method | python | `distributed.py:333` | Yes |
| S3ShardCoordinator.get_status | method | python | `distributed.py:356` | Yes |
| _no_color | function | python | `monitor.py:40` | Yes |
| _progress_bar | function | python | `monitor.py:45` | Yes |
| _format_duration | function | python | `monitor.py:50` | Yes |
| _format_rate | function | python | `monitor.py:60` | Yes |
| _shorten_machine | function | python | `monitor.py:68` | Yes |
| _extract_host | function | python | `monitor.py:74` | Yes |
| _validate_env | function | python | `monitor.py:109` | Yes |
| _parse_new_jsonl | function | python | `monitor.py:116` | Yes |
| _count_lines | function | python | `monitor.py:145` | Yes |
| _run_validate_tiles | function | python | `monitor.py:152` | Yes |
| _run_validate_tiles_s3 | function | python | `monitor.py:199` | Yes |
| _parse_ssh_spec | function | python | `monitor.py:245` | Yes |
| _run_validate_tiles_ssh | function | python | `monitor.py:256` | Yes |
| render | function | python | `monitor.py:328` | Yes |
| main | function | python | `monitor.py:697` | Yes |
| build | function | python | `pipelines.py:14` | Yes |
| main | function | python | `pipelines.py:286` | Yes |
| Document | class | python | `base.py:8` | Yes |
| Source | class | python | `base.py:15` | Yes |
| Source.__iter__ | method | python | `base.py:16` | Yes |
| Source.__len__ | method | python | `base.py:19` | Yes |
| KiwixServeManager | class | python | `kiwix.py:22` | Yes |
| KiwixServeManager.__init__ | method | python | `kiwix.py:41` | Yes |
| KiwixServeManager.ports | method | python | `kiwix.py:59` | No (SyntaxError: unexpected indent (line 2)) |
| KiwixServeManager.next_url | method | python | `kiwix.py:62` | Yes |
| KiwixServeManager._find_binary | method | python | `kiwix.py:86` | Yes |
| KiwixServeManager._install_kiwix_tools | method | python | `kiwix.py:95` | Yes |
| KiwixServeManager._health_check | method | python | `kiwix.py:133` | Yes |
| KiwixServeManager._start_instance | method | python | `kiwix.py:144` | Yes |
| KiwixServeManager._start_ttl_watcher | method | python | `kiwix.py:193` | Yes |
| KiwixServeManager.touch | method | python | `kiwix.py:213` | Yes |
| KiwixServeManager.ensure_running | method | python | `kiwix.py:217` | Yes |
| KiwixServeManager._kill_proc | method | python | `kiwix.py:235` | Yes |
| KiwixServeManager.stop | method | python | `kiwix.py:248` | Yes |
| KiwixServeManager.__del__ | method | python | `kiwix.py:254` | Yes |
| KiwixSource | class | python | `kiwix.py:263` | Yes |
| KiwixSource.__init__ | method | python | `kiwix.py:280` | Yes |
| KiwixSource._resolve_zim | method | python | `kiwix.py:305` | No (SyntaxError: unexpected indent (line 2)) |
| KiwixSource._download_zim | method | python | `kiwix.py:337` | No (SyntaxError: unexpected indent (line 2)) |
| KiwixSource._get_zim | method | python | `kiwix.py:371` | Yes |
| KiwixSource.book_name | method | python | `kiwix.py:379` | No (SyntaxError: unexpected indent (line 2)) |
| KiwixSource._is_article_path | method | python | `kiwix.py:384` | Yes |
| KiwixSource._cache_path | method | python | `kiwix.py:425` | Yes |
| KiwixSource._load_article_cache | method | python | `kiwix.py:428` | Yes |
| KiwixSource._save_article_cache | method | python | `kiwix.py:441` | Yes |
| KiwixSource._redirects_cache_path | method | python | `kiwix.py:452` | Yes |
| KiwixSource._build_redirect_map | method | python | `kiwix.py:455` | Yes |
| KiwixSource._load_redirect_set | method | python | `kiwix.py:523` | Yes |
| KiwixSource._build_article_list | method | python | `kiwix.py:530` | Yes |
| KiwixSource._path_to_url | method | python | `kiwix.py:561` | Yes |
| KiwixSource.__iter__ | method | python | `kiwix.py:566` | Yes |
| KiwixSource.__len__ | method | python | `kiwix.py:586` | Yes |
| KiwixSource.close | method | python | `kiwix.py:589` | Yes |
| KiwixSource.__del__ | method | python | `kiwix.py:594` | Yes |
| KiwixSource.__enter__ | method | python | `kiwix.py:597` | Yes |
| KiwixSource.__exit__ | method | python | `kiwix.py:600` | Yes |
| _cleanup_sources | function | python | `kiwix.py:605` | Yes |
| LocalSource | class | python | `local.py:20` | Yes |
| LocalSource.__init__ | method | python | `local.py:21` | Yes |
| LocalSource.__iter__ | method | python | `local.py:29` | Yes |
| LocalSource.__len__ | method | python | `local.py:51` | Yes |
| PDFSource | class | python | `pdf.py:9` | Yes |
| PDFSource.__init__ | method | python | `pdf.py:10` | Yes |
| PDFSource.__iter__ | method | python | `pdf.py:14` | Yes |
| PDFSource.__len__ | method | python | `pdf.py:18` | Yes |
| WebSource | class | python | `web.py:49` | Yes |
| WebSource.__init__ | method | python | `web.py:58` | Yes |
| WebSource.__iter__ | method | python | `web.py:79` | Yes |
| WebSource.__len__ | method | python | `web.py:87` | Yes |

## Validation

- **ports**: SyntaxError: unexpected indent (line 2)
- **_resolve_zim**: SyntaxError: unexpected indent (line 2)
- **_download_zim**: SyntaxError: unexpected indent (line 2)
- **book_name**: SyntaxError: unexpected indent (line 2)

## Raw Source

All 12 original source files are preserved in the `raw/` directory, 
organized with the same directory structure as the original project. 
This includes both code files and non-code assets (images, configs, binaries) 
that were not extracted as modules.

---
Generated by Cleansed v1.0.0
