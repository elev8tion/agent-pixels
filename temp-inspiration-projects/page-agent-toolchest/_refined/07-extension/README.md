# Cleansed Extracted Modules

**Source:** `/Users/kc/page-agent-toolchest/07-extension`
**Extracted:** 2026-07-08 04:30
**Extracted items:** 116
**Raw source files preserved:** 59 in `raw/`

## Analysis Summary

- **Health Score:** 54/100
- **Long Functions:** 19
- **Duplication Pairs:** 20
- **High Coupling Items:** 9
- **Potential Dead Code:** 112 items (109 high-confidence)
- **Modules (Directories):** 1
- **Cross-Module Dependencies:** 0

## Languages

- **typescript:** 116 items

## Contents

| Name | Type | Language | Source File | Valid |
|------|------|----------|-------------|-------|
| detectLanguage | function | typescript | `MultiPageAgent.ts:9` | Yes |
| MultiPageAgent | class | typescript | `MultiPageAgent.ts:24` | Yes |
| handlePageControlMessage | function | typescript | `RemotePageController.background.ts:6` | Yes |
| initPageController | function | typescript | `RemotePageController.content.ts:6` | Yes |
| getMethodName | function | typescript | `RemotePageController.content.ts:106` | Yes |
| PREFIX | component | typescript | `RemotePageController.ts:5` | Yes |
| sendMessage | function | typescript | `RemotePageController.ts:9` | Yes |
| RemotePageController | class | typescript | `RemotePageController.ts:26` | Yes |
| isContentScriptAllowed | function | typescript | `RemotePageController.ts:175` | Yes |
| PREFIX | component | typescript | `TabsController.background.ts:10` | Yes |
| resolveActiveTab | function | typescript | `TabsController.background.ts:24` | Yes |
| handleTabControlMessage | function | typescript | `TabsController.background.ts:47` | Yes |
| PREFIX | component | typescript | `TabsController.ts:3` | Yes |
| sendMessage | function | typescript | `TabsController.ts:7` | Yes |
| getOwnWindowId | function | typescript | `TabsController.ts:26` | Yes |
| TabsController | class | typescript | `TabsController.ts:38` | Yes |
| TAB_GROUP_COLORS | component | typescript | `TabsController.ts:413` | Yes |
| randomColor | function | typescript | `TabsController.ts:417` | Yes |
| waitUntil | function | typescript | `TabsController.ts:427` | Yes |
| isTestingEndpoint | function | typescript | `constants.ts:19` | Yes |
| migrateLegacyEndpoint | function | typescript | `constants.ts:24` | Yes |
| createTabTools | function | typescript | `tabTools.ts:24` | Yes |
| useAgent | function | typescript | `useAgent.ts:43` | Yes |
| ConfigPanel | function | typescript | `ConfigPanel.tsx:29` | Yes |
| ErrorBoundary | class | typescript | `ErrorBoundary.tsx:15` | Yes |
| HistoryDetail | function | typescript | `HistoryDetail.tsx:9` | Yes |
| timeAgo | function | typescript | `HistoryList.tsx:16` | Yes |
| HistoryList | function | typescript | `HistoryList.tsx:27` | Yes |
| ResultCard | function | typescript | `cards.tsx:26` | Yes |
| ReflectionItem | function | typescript | `cards.tsx:64` | Yes |
| ReflectionSection | function | typescript | `cards.tsx:84` | Yes |
| ActionIcon | function | typescript | `cards.tsx:116` | Yes |
| CopyButton | function | typescript | `cards.tsx:127` | Yes |
| extractPrompt | function | typescript | `cards.tsx:146` | Yes |
| RawSection | function | typescript | `cards.tsx:159` | Yes |
| StepCard | function | typescript | `cards.tsx:222` | Yes |
| ObservationCard | function | typescript | `cards.tsx:269` | Yes |
| RetryCard | function | typescript | `cards.tsx:283` | Yes |
| ErrorCard | function | typescript | `cards.tsx:296` | Yes |
| EventCard | function | typescript | `cards.tsx:309` | Yes |
| ActivityCard | function | typescript | `cards.tsx:344` | Yes |
| StatusDot | function | typescript | `misc.tsx:11` | Yes |
| Logo | function | typescript | `misc.tsx:38` | Yes |
| MotionOverlay | function | typescript | `misc.tsx:43` | Yes |
| EmptyState | function | typescript | `misc.tsx:96` | Yes |
| Button | function | typescript | `button.tsx:37` | Yes |
| Card | function | typescript | `card.tsx:5` | Yes |
| CardHeader | function | typescript | `card.tsx:18` | Yes |
| CardTitle | function | typescript | `card.tsx:31` | Yes |
| CardDescription | function | typescript | `card.tsx:41` | Yes |
| CardAction | function | typescript | `card.tsx:51` | Yes |
| CardContent | function | typescript | `card.tsx:61` | Yes |
| CardFooter | function | typescript | `card.tsx:65` | Yes |
| FieldSet | function | typescript | `field.tsx:8` | Yes |
| FieldLegend | function | typescript | `field.tsx:22` | Yes |
| FieldGroup | function | typescript | `field.tsx:42` | Yes |
| Field | function | typescript | `field.tsx:76` | Yes |
| FieldContent | function | typescript | `field.tsx:92` | Yes |
| FieldLabel | function | typescript | `field.tsx:102` | Yes |
| FieldTitle | function | typescript | `field.tsx:117` | Yes |
| FieldDescription | function | typescript | `field.tsx:130` | Yes |
| FieldSeparator | function | typescript | `field.tsx:145` | Yes |
| FieldError | function | typescript | `field.tsx:175` | Yes |
| HoverCard | function | typescript | `hover-card.tsx:6` | Yes |
| HoverCardTrigger | function | typescript | `hover-card.tsx:10` | Yes |
| HoverCardContent | function | typescript | `hover-card.tsx:14` | Yes |
| InputGroup | function | typescript | `input-group.tsx:9` | Yes |
| InputGroupAddon | function | typescript | `input-group.tsx:57` | Yes |
| InputGroupButton | function | typescript | `input-group.tsx:93` | Yes |
| InputGroupText | function | typescript | `input-group.tsx:112` | Yes |
| InputGroupInput | function | typescript | `input-group.tsx:124` | Yes |
| InputGroupTextarea | function | typescript | `input-group.tsx:137` | Yes |
| Input | function | typescript | `input.tsx:5` | Yes |
| ItemGroup | function | typescript | `item.tsx:8` | Yes |
| ItemSeparator | function | typescript | `item.tsx:19` | Yes |
| Item | function | typescript | `item.tsx:51` | Yes |
| ItemMedia | function | typescript | `item.tsx:86` | Yes |
| ItemContent | function | typescript | `item.tsx:101` | Yes |
| ItemTitle | function | typescript | `item.tsx:111` | Yes |
| ItemDescription | function | typescript | `item.tsx:121` | Yes |
| ItemActions | function | typescript | `item.tsx:135` | Yes |
| ItemHeader | function | typescript | `item.tsx:141` | Yes |
| ItemFooter | function | typescript | `item.tsx:151` | Yes |
| Label | function | typescript | `label.tsx:6` | Yes |
| Separator | function | typescript | `separator.tsx:6` | Yes |
| Toaster | component | typescript | `sonner.tsx:11` | Yes |
| Spinner | function | typescript | `spinner.tsx:5` | Yes |
| Switch | function | typescript | `switch.tsx:6` | Yes |
| Textarea | function | typescript | `textarea.tsx:5` | Yes |
| TypingAnimation | function | typescript | `typing-animation.tsx:23` | Yes |
| openOrFocusHubTab | function | typescript | `background.ts:46` | Yes |
| DEBUG_PREFIX | component | typescript | `content.ts:5` | Yes |
| exposeAgentToPage | function | typescript | `content.ts:39` | Yes |
| App | function | typescript | `App.tsx:12` | Yes |
| HubConfig | function | typescript | `App.tsx:146` | Yes |
| ProtocolDocsCollapsible | function | typescript | `App.tsx:192` | Yes |
| HubWs | class | typescript | `hub-ws.ts:69` | Yes |
| useHubWs | function | typescript | `hub-ws.ts:199` | Yes |
| syncDarkMode | function | typescript | `main.tsx:10` | Yes |
| App | function | typescript | `App.tsx:26` | Yes |
| syncDarkMode | function | typescript | `main.tsx:11` | Yes |
| DB_NAME | component | typescript | `db.ts:4` | Yes |
| DB_VERSION | component | typescript | `db.ts:5` | Yes |
| getDB | function | typescript | `db.ts:25` | Yes |
| saveSession | function | typescript | `db.ts:37` | Yes |
| listSessions | function | typescript | `db.ts:51` | Yes |
| getSession | function | typescript | `db.ts:57` | Yes |
| deleteSession | function | typescript | `db.ts:62` | Yes |
| clearSessions | function | typescript | `db.ts:67` | Yes |
| serializeHistoryExport | function | typescript | `history-export.ts:6` | Yes |
| buildHistoryExportFilename | function | typescript | `history-export.ts:10` | Yes |
| downloadHistoryExport | function | typescript | `history-export.ts:19` | Yes |
| sanitizeTaskForFilename | function | typescript | `history-export.ts:37` | Yes |
| formatTimestampForFilename | function | typescript | `history-export.ts:46` | Yes |
| pad | function | typescript | `history-export.ts:58` | Yes |
| cn | function | typescript | `utils.ts:4` | Yes |

## Validation

All blocks pass validation.

## Raw Source

All 59 original source files are preserved in the `raw/` directory, 
organized with the same directory structure as the original project. 
This includes both code files and non-code assets (images, configs, binaries) 
that were not extracted as modules.

---
Generated by Cleansed v1.0.0
