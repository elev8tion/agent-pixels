# Pi Everywhere Implementation Checklist

Source plan: `docs/PI-EVERYWHERE-GAP-PLAN.md`

## Confirmed task
Make Agent-Pixel's active extension runtime and docs Pi Everywhere-first: remove primary local-server assumptions, route primary actions through a single Pi Everywhere dispatch contract, and clearly mark legacy behavior as archived/fallback only.

## Scope

### In scope
- `extension/background.js`
- `extension/sidepanel.js`
- `extension/sidepanel.html`
- `extension/content.js` verification only unless legacy coupling is found
- `README.md`
- `docs/PI-EVERYWHERE-MIGRATION.md`
- `docs/EXTENSION-UI-DATA-MAP.md`
- `docs/STRATEGY.md`
- `docs/UX-ROADMAP.md`

### Out of scope
- Building a native Pi runtime API that Chrome can invoke directly without user/host support.
- Modifying archived docs.
- Adding new extension permissions unless required by implementation.

## Team decomposition

### Phase A — Runtime code cleanup
- [x] Remove `DEFAULT_SERVER` as the primary background runtime default.
- [x] Stop `AGENT_PIXEL_CAPTURE_ACTIVE_TAB` from posting to `/api/captures`; capture should return browser data directly for Pi Everywhere consumers.
- [x] Stop `AGENT_PIXEL_CHAT` from posting to `/api/chat`; route through a Pi Everywhere dispatch response contract instead.
- [x] Replace `AGENT_PIXEL_EXECUTE_DIRECT` with the same browser-action dispatch path used by Pi Everywhere messages.
- [x] Keep any legacy server behavior behind explicitly named legacy-only message paths if needed.
- [x] Add storage-backed `piEverywhereMode` as the single active runtime switch.
- [x] Verify `grep -R "http://127.0.0.1:4317\|/api/chat\|/api/captures" extension` has no primary-path hits.

### Phase B — Side panel state/action cleanup
- [x] Remove primary `serverUrl` state and provider/model polling assumptions.
- [x] Remove automatic fetches to `/api/providers` and `localhost:17321/pi-models` from the primary init/settings path.
- [x] Load model choices from imported `~/.pi/agent/models.json` only, or show a clear Pi Everywhere activation/import instruction.
- [x] Convert mock action success cards into dispatch attempts through one Pi Everywhere action function.
- [x] Ensure each action reports real success/failure, with non-implemented host integration called out as pending rather than fake success.
- [x] Update quick click/scroll to use the shared dispatch path.
- [x] Verify `grep -n "fetch(\|localhost:17321\|/api/providers\|AGENT_PIXEL_CHAT\|AGENT_PIXEL_CAPTURE_ACTIVE_TAB" extension/sidepanel.js` shows no primary-path dependency.

### Phase C — UI copy alignment
- [x] Make start panel and output copy unambiguously Pi Everywhere-first.
- [x] Rename legacy refresh/settings labels so fallback cannot be mistaken for the primary flow.
- [x] Remove labels that imply implemented provider/server sync where it is not implemented.
- [x] Verify text scan for `Legacy refresh`, `server`, and `localhost` in `extension/sidepanel.html` only finds clearly labeled fallback/archive language or no hits.

### Phase D — Active docs contract
- [ ] Add README runtime contract, legacy paths, and validation checklist.
- [x] Convert `docs/PI-EVERYWHERE-MIGRATION.md` into an implementation contract with done-when criteria.
- [x] Split `docs/EXTENSION-UI-DATA-MAP.md` into active and archived flows with runtime source per surface.
- [x] Add runtime ownership and cleanup priorities to `docs/STRATEGY.md`.
- [x] Convert `docs/UX-ROADMAP.md` remaining work into file-targeted runtime vs UX checklists.
- [x] Verify active docs consistently say local server/provider/model polling is fallback/archived only.

### Phase E — End-to-end verification
- [x] Run syntax check for extension JS.
- [x] Run grep checks for forbidden primary endpoints.
- [x] Inspect git diff for scope drift.
- [x] Record residual risks and unimplemented host integration boundaries.

## Acceptance criteria
- [x] No primary UI path assumes a local server is required.
- [x] No primary code path depends on `http://127.0.0.1:4317`.
- [x] No primary code path depends on legacy provider/model polling.
- [x] `PI_EVERYWHERE_ACTIVATE` is the clear runtime switch.
- [x] Legacy behavior is either removed or explicitly archived/fallback-only.
