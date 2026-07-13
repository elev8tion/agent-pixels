# Cleansed Extracted Modules

**Source:** `/Users/kc/PixelRAG-toolchest/06-web`
**Extracted:** 2026-07-08 04:28
**Extracted items:** 95
**Raw source files preserved:** 48 in `raw/`

## Analysis Summary

- **Health Score:** 54/100
- **Long Functions:** 15
- **Duplication Pairs:** 20
- **High Coupling Items:** 5
- **Potential Dead Code:** 93 items (93 high-confidence)
- **Modules (Directories):** 4
- **Cross-Module Dependencies:** 3

## Languages

- **javascript:** 13 items
- **typescript:** 82 items

## Contents

| Name | Type | Language | Source File | Valid |
|------|------|----------|-------------|-------|
| PORT | component | javascript | `agent-server.mjs:25` | Yes |
| SEARCH_URL | component | javascript | `agent-server.mjs:26` | Yes |
| MAX_BUDGET | component | javascript | `agent-server.mjs:27` | Yes |
| THINKING_TOKENS | component | javascript | `agent-server.mjs:28` | Yes |
| ALLOWED_ORIGIN | component | javascript | `agent-server.mjs:29` | Yes |
| RL_PER_IP | component | javascript | `agent-server.mjs:32` | Yes |
| RL_WINDOW_MS | component | javascript | `agent-server.mjs:33` | Yes |
| RL_GLOBAL_DAILY | component | javascript | `agent-server.mjs:34` | Yes |
| RL_MAX_CONCURRENT | component | javascript | `agent-server.mjs:35` | Yes |
| rateLimit | function | javascript | `agent-server.mjs:42` | Yes |
| log | function | javascript | `agent-server.mjs:72` | Yes |
| createTools | function | javascript | `agent-server.mjs:76` | Yes |
| sse | function | javascript | `agent-server.mjs:159` | Yes |
| sseEvent | function | typescript | `route.ts:40` | Yes |
| createTools | function | typescript | `route.ts:44` | Yes |
| POST | function | typescript | `route.ts:220` | Yes |
| ChatLayout | function | typescript | `layout.tsx:9` | Yes |
| EXAMPLES | component | typescript | `page.tsx:60` | Yes |
| ChatPageInner | function | typescript | `page.tsx:67` | Yes |
| ChatPage | function | typescript | `page.tsx:317` | Yes |
| EmptyState | function | typescript | `page.tsx:327` | Yes |
| UserMessage | function | typescript | `page.tsx:418` | Yes |
| AssistantMessage | function | typescript | `page.tsx:434` | Yes |
| SearchCard | function | typescript | `page.tsx:474` | Yes |
| ThinkingTrace | function | typescript | `page.tsx:524` | Yes |
| READING_VERBS | component | typescript | `page.tsx:588` | Yes |
| TileGallery | function | typescript | `page.tsx:599` | Yes |
| DocsLayout | function | typescript | `layout.tsx:9` | Yes |
| DocsPage | function | typescript | `page.tsx:126` | Yes |
| Code | function | typescript | `page.tsx:247` | Yes |
| ShellBlock | function | typescript | `page.tsx:257` | Yes |
| FlowStep | function | typescript | `page.tsx:291` | Yes |
| OverviewSection | function | typescript | `page.tsx:326` | Yes |
| MethodBadge | function | typescript | `page.tsx:446` | Yes |
| Section | function | typescript | `page.tsx:462` | Yes |
| TypeBadge | function | typescript | `page.tsx:480` | Yes |
| FieldRow | function | typescript | `page.tsx:495` | Yes |
| FieldTable | function | typescript | `page.tsx:522` | Yes |
| RootLayout | function | typescript | `layout.tsx:26` | Yes |
| SearchPageContent | function | typescript | `page.tsx:20` | Yes |
| SearchPage | function | typescript | `page.tsx:342` | Yes |
| PIPELINE | component | typescript | `AboutSection.tsx:5` | Yes |
| STATS | component | typescript | `AboutSection.tsx:12` | Yes |
| AboutSection | function | typescript | `AboutSection.tsx:19` | Yes |
| ApiPlayground | function | typescript | `ApiPlayground.tsx:16` | Yes |
| highlightCurl | function | typescript | `ApiPlayground.tsx:160` | Yes |
| highlightJson | function | typescript | `ApiPlayground.tsx:191` | Yes |
| JsonEditor | function | typescript | `ApiPlayground.tsx:223` | Yes |
| ComparePanel | function | typescript | `ComparePanel.tsx:15` | Yes |
| Lightbox | function | typescript | `Lightbox.tsx:17` | Yes |
| MetaRow | function | typescript | `Lightbox.tsx:211` | Yes |
| MODES | component | typescript | `ModeToggle.tsx:13` | Yes |
| ModeToggle | function | typescript | `ModeToggle.tsx:18` | Yes |
| NavLinks | function | typescript | `NavLinks.tsx:13` | Yes |
| ResultGroup | function | typescript | `ResultGroup.tsx:15` | Yes |
| EXAMPLE_QUERIES | component | typescript | `SearchBar.tsx:14` | Yes |
| ASK_EXAMPLES | component | typescript | `SearchBar.tsx:25` | Yes |
| SearchBar | function | typescript | `SearchBar.tsx:41` | Yes |
| SearchControls | function | typescript | `SearchControls.tsx:24` | Yes |
| Field | function | typescript | `SearchControls.tsx:101` | Yes |
| StatusCard | function | typescript | `StatusCard.tsx:10` | Yes |
| TileCard | function | typescript | `TileCard.tsx:16` | Yes |
| ThemeProvider | function | typescript | `theme-provider.tsx:6` | Yes |
| isTypingTarget | function | typescript | `theme-provider.tsx:24` | Yes |
| ThemeHotkey | function | typescript | `theme-provider.tsx:37` | Yes |
| Badge | function | typescript | `badge.tsx:30` | Yes |
| Button | function | typescript | `button.tsx:43` | Yes |
| Collapsible | function | typescript | `collapsible.tsx:5` | Yes |
| CollapsibleTrigger | function | typescript | `collapsible.tsx:9` | Yes |
| CollapsibleContent | function | typescript | `collapsible.tsx:15` | Yes |
| Dialog | function | typescript | `dialog.tsx:10` | Yes |
| DialogTrigger | function | typescript | `dialog.tsx:14` | Yes |
| DialogPortal | function | typescript | `dialog.tsx:18` | Yes |
| DialogClose | function | typescript | `dialog.tsx:22` | Yes |
| DialogOverlay | function | typescript | `dialog.tsx:26` | Yes |
| DialogContent | function | typescript | `dialog.tsx:42` | Yes |
| DialogHeader | function | typescript | `dialog.tsx:83` | Yes |
| DialogFooter | function | typescript | `dialog.tsx:93` | Yes |
| DialogTitle | function | typescript | `dialog.tsx:120` | Yes |
| DialogDescription | function | typescript | `dialog.tsx:133` | Yes |
| Input | function | typescript | `input.tsx:6` | Yes |
| Slider | function | typescript | `slider.tsx:5` | Yes |
| API_BASE | component | typescript | `api.ts:3` | Yes |
| fetchApi | function | typescript | `api.ts:5` | Yes |
| search | function | typescript | `api.ts:14` | Yes |
| getStatus | function | typescript | `api.ts:26` | Yes |
| getHealth | function | typescript | `api.ts:30` | Yes |
| tileUrl | function | typescript | `api.ts:34` | Yes |
| reconstruct | function | typescript | `api.ts:42` | Yes |
| keyFor | function | typescript | `history.ts:6` | Yes |
| getHistory | function | typescript | `history.ts:8` | Yes |
| addHistory | function | typescript | `history.ts:21` | Yes |
| clearHistory | function | typescript | `history.ts:35` | Yes |
| groupHitsByArticle | function | typescript | `types.ts:56` | Yes |
| cn | function | typescript | `utils.ts:4` | Yes |

## Validation

All blocks pass validation.

## Raw Source

All 48 original source files are preserved in the `raw/` directory, 
organized with the same directory structure as the original project. 
This includes both code files and non-code assets (images, configs, binaries) 
that were not extracted as modules.

---
Generated by Cleansed v1.0.0
