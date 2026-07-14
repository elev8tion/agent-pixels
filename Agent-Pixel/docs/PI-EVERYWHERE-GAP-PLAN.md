# Agent-Pixel — Pi Everywhere Gap List & Cleanup Plan

## Goal
Make `/pi-everywhere` the **real** runtime path everywhere in Agent-Pixel, so the repo no longer depends on local project Pi/server behavior for normal operation.

## Current state
The repo is **described** as Pi Everywhere-first, but several code paths still behave like the old local-server app:

- UI text says `/pi-everywhere` is primary.
- `background.js` still uses `http://127.0.0.1:4317` and legacy message flows.
- `sidepanel.js` still fetches legacy endpoints and model lists.
- Most action buttons are still mock/placeholder feedback rather than real Pi orchestration.

## File-by-file gaps

### 1) `README.md`
**Status:** Mostly correct, but still documentation-only.

**Gaps:**
- No explicit matrix showing what is legacy vs active.
- No operator steps for validating the Pi Everywhere flow end-to-end.
- No cleanup note telling maintainers what should never be reintroduced.

**Needed:**
- Add a short “runtime contract” section.
- Add a “legacy paths” section with direct file references.
- Add a verification checklist for `/pi-everywhere`.

---

### 2) `docs/PI-EVERYWHERE-MIGRATION.md`
**Status:** Good migration note, but incomplete as an implementation contract.

**Gaps:**
- Describes the decision, but not the actual app wiring changes.
- No “done when” criteria.
- No file-level mapping of what still needs to change.

**Needed:**
- Convert into an implementation checklist.
- Add explicit acceptance criteria for runtime behavior.

---

### 3) `docs/EXTENSION-UI-DATA-MAP.md`
**Status:** Mostly accurate conceptually, but still mentions legacy surfaces without fully separating them.

**Gaps:**
- Active vs legacy responsibilities are not sharply divided.
- Lacks a hard statement that local-server behavior is fallback-only.
- Does not say which UI elements must stop depending on legacy data.

**Needed:**
- Split into `active flow` and `archived flow` sections.
- Mark each active surface with its runtime source.
- Add explicit “do not wire new features to legacy endpoints” guidance.

---

### 4) `docs/STRATEGY.md`
**Status:** Good direction, but still high-level.

**Gaps:**
- Refers to toolchest workflow without a concrete runtime map.
- Doesn’t define the implementation boundary between Pi Everywhere and archived fallback.

**Needed:**
- Add a “runtime ownership” section.
- Add a “cleanup priorities” section tied to files.

---

### 5) `docs/UX-ROADMAP.md`
**Status:** Honest about remaining work, but still product-centric.

**Gaps:**
- Several items are still phrased as future work without being tied to exact files.
- No sequencing for cleanup of legacy code paths.

**Needed:**
- Convert the remaining work into a file-targeted checklist.
- Separate “UX gap” from “runtime gap.”

---

### 6) `extension/background.js`
**Status:** Major runtime gap.

**Gaps:**
- Still defines `DEFAULT_SERVER = 'http://127.0.0.1:4317'`.
- Still loads settings from legacy `serverUrl` / `provider` / `model` storage.
- Still uses `fetch()` against local `/api/captures` and `/api/chat`.
- Still has legacy `AGENT_PIXEL_EXECUTE_DIRECT` and local tab messaging behavior.
- Pi Everywhere mode is advertised, but not actually connected to a global agent runtime.

**Needed:**
- Remove default dependency on local server.
- Replace legacy fetch-based paths with Pi Everywhere dispatch semantics.
- Make `PI_EVERYWHERE_ACTIVATE` the real mode switch.
- Separate “browser capture” from “agent orchestration” clearly.
- Add a compatibility layer only if needed, and keep it explicit.

---

### 7) `extension/sidepanel.js`
**Status:** Major runtime gap.

**Gaps:**
- Still fetches legacy provider data from `/api/providers`.
- Still fetches model list from `http://localhost:17321/pi-models`.
- Still emits mock success cards for many actions.
- Buttons update UI state, but do not consistently trigger a real Pi Everywhere execution path.
- Legacy fallback text is still mixed into the primary path.

**Needed:**
- Replace mock action handling with real action dispatch.
- Remove local-server assumptions from model/provider loading.
- Add a single source of truth for “Pi Everywhere enabled” state.
- Ensure every action either:
  - invokes real agent execution, or
  - is clearly labeled legacy-only.

---

### 8) `extension/sidepanel.html`
**Status:** UI is aligned in spirit, but some wording still reads like an archived hybrid.

**Gaps:**
- Some UI copy still suggests local-server fallback as normal.
- Several labels describe capabilities that may not be real yet.
- The start panel and action cards need wording aligned with actual runtime.

**Needed:**
- Make primary copy unambiguous: Pi Everywhere first.
- Mark anything not implemented as fallback/archived.
- Ensure button labels match actual behavior.

---

### 9) `extension/content.js`
**Status:** Likely browser-action support only, but should be checked for legacy coupling.

**Gaps to verify:**
- Any direct dependency on legacy server endpoints.
- Any message types that expect old polling behavior.

**Needed:**
- Keep only browser-page interaction concerns here.
- Remove any legacy orchestration assumptions.

---

### 10) `extension/manifest.json`
**Status:** Fine structurally.

**Gaps:**
- None obvious from current scan.

**Needed:**
- Only update if runtime permissions change.

---

### 11) `package.json`
**Status:** Documentation-level only.

**Gaps:**
- Scripts are placeholders and do not verify Pi Everywhere readiness.

**Needed:**
- Add a validation script if a real local check exists.
- Otherwise keep as-is and avoid implying local runtime ownership.

---

### 12) `docs/archive/*`
**Status:** Historical record.

**Gaps:**
- Contains old local Pi/server assumptions.

**Needed:**
- Leave archived unless you intentionally want a cleanup pass.
- Do not let archived docs leak into active runtime guidance.

## Cleanup plan

### Phase 1 — Lock the runtime contract
- Define `/pi-everywhere` as the only active entrypoint.
- Mark local server/provider/model fetches as legacy.
- Decide whether any fallback must remain at all.

### Phase 2 — Remove legacy defaults from code
- Strip `DEFAULT_SERVER`-style assumptions from `background.js`.
- Replace `sidepanel.js` provider/model loading with Pi Everywhere-aware state.
- Make UI actions call one real dispatch path.

### Phase 3 — Separate active vs archived surfaces
- Keep active docs focused on current runtime only.
- Move all fallback language to a clearly labeled legacy section.
- Ensure archived docs remain historical and non-normative.

### Phase 4 — Normalize UI messaging
- Make every button, card, and status label reflect real behavior.
- Remove “mock success” language from the primary flow.
- Show real success/failure and next-step summaries.

### Phase 5 — Verify end-to-end
- Confirm activating `/pi-everywhere` changes UI state.
- Confirm agent actions route through the intended global path.
- Confirm no primary path depends on `localhost` services.

## Acceptance criteria

- No primary UI path assumes the local server is required.
- No primary code path depends on `http://127.0.0.1:4317`.
- No primary code path depends on legacy provider/model polling.
- Pi Everywhere activation is the clear runtime switch.
- Legacy behavior is either removed or explicitly archived.

## Suggested next edit order
1. `extension/background.js`
2. `extension/sidepanel.js`
3. `extension/sidepanel.html`
4. `docs/EXTENSION-UI-DATA-MAP.md`
5. `docs/STRATEGY.md`
6. `docs/UX-ROADMAP.md`
7. `README.md`

## Final note
The repo is already **conceptually** Pi Everywhere-first. The remaining work is mostly about making the runtime and UI **stop pretending** the old local server is still the real center of the product.
