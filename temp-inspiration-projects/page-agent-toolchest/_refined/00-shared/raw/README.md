# 00-shared — Monorepo Foundation

The build tooling, root configs, and cross-cutting interface contracts that hold
the `page-agent` monorepo together. Every other module assumes these conventions.

## What's Here

```
00-shared/
├── scripts/                  ← Build/CI/version orchestration (457 LOC of real code)
│   ├── build.js              # Orchestrates the full monorepo build (parallel via parallel-task.js)
│   ├── build-libs.js         # Builds only the publishable libraries
│   ├── ci.js                 # CI entrypoint: typecheck + lint + test across workspaces
│   ├── parallel-task.js      # Runs npm scripts across workspaces in topological order w/ concurrency
│   ├── sync-version.js       # npm version hook — keeps all 8 package versions in lockstep
│   ├── pre-publish.js        # Promotes publishConfig (src/ → dist/) before npm publish
│   └── post-publish.js       # Restores the source-first exports after publish
├── root-package.json         # The monorepo root manifest (workspaces, devDeps, lint-staged, commitlint)
├── tsconfig.base.json        # Shared TS compiler options + path aliases for all packages
├── tsconfig.typecheck.json   # Root project-references typecheck config
├── eslint.config.js          # Flat ESLint config (eslint v10 + typescript-eslint + eslint-react)
├── .prettierignore
└── contracts.md              ← ⭐ The 4 interface contracts that decouple the 8 packages
```

## The Key Idea: Source-First Monorepo

Library `package.json` `exports` point at **`src/*.ts` during development**.
At publish time, `pre-publish.js` promotes `publishConfig` fields to top-level
(swapping to `dist/*.js`), and `post-publish.js` restores the originals. This
means:

- Dev: hot source, no build step, TypeScript paths resolve directly.
- Publish: consumers get compiled `dist/`.

**To replicate this pattern in a new project**, copy `pre-publish.js` +
`post-publish.js` + the `publishConfig` blocks from any library package.json.

## Why This Is a Module (not just config)

Per extraction rules, a module must contain real code. `scripts/` is 457 lines of
non-trivial orchestration logic — parallel build scheduling with topological
ordering, version synchronization across 8 packages, and the publish/restore
state machine. This is the load-bearing infrastructure every package depends on.

## Cross-Cutting Contracts

See **[contracts.md](./contracts.md)** for the 4 interface boundaries that make
the packages composable:

1. `Tool` / `Message` / `InvokeResult` / `LLMConfig` — the LLM client contract
2. `PageController` / `BrowserState` — the DOM-ops contract
3. `MacroTool` / reflection-before-action — the agent mental model
4. `PanelAgentAdapter` — the UI decoupling contract

## Dependencies

None runtime. Dev-time: vite v8, vitest v4, eslint v10, typescript v6,
`@microsoft/api-extractor`, prettier, husky, commitlint.
