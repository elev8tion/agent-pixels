# 05-page-agent — Main Entry (`page-agent`)

The public npm package. A thin composition layer: `PageAgent = PageAgentCore +
PageController + Panel`. This is what `npm install page-agent` gives you, and
what the one-line CDN `<script>` loads.

## What's Here

```
src/
├── PageAgent.ts    ← ⭐ PageAgent extends PageAgentCore, wires PageController + Panel (84 LOC)
├── demo.ts         # The IIFE demo entry (auto-inits with the free testing LLM API)
└── env.d.ts

package.json, tsconfig.json, vite.config.js, vite.iife.config.js
```

## The Whole Class

```ts
export type PageAgentConfig = AgentConfig & PageControllerConfig & Omit<PanelConfig, 'language'>

export class PageAgent extends PageAgentCore {
    panel: Panel
    constructor(config: PageAgentConfig) {
        const pageController = new PageController({ ...config, enableMask: config.enableMask ?? true })
        super({ ...config, pageController })
        this.panel = new Panel(this, { language: config.language, promptForNextTask: config.promptForNextTask })
    }
}
```

That's the entire public class — everything heavy lives in `03-core`,
`02-page-controller`, and `04-ui`.

## Two Build Outputs

| Output | Config | Purpose |
|--------|--------|---------|
| `dist/esm/page-agent.js` | `vite.config.js` | The npm ESM bundle |
| `dist/iife/page-agent.demo.js` | `vite.iife.config.js` | The one-line CDN script (auto-init with demo LLM) |

## Usage

```ts
import { PageAgent } from 'page-agent'
const agent = new PageAgent({
    model: 'qwen3.5-plus',
    baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    apiKey: 'YOUR_API_KEY',
    language: 'en-US',
})
await agent.execute('Click the login button')
```

## Dependencies

`@page-agent/core`, `@page-agent/llms`, `@page-agent/page-controller`,
`@page-agent/ui`, `chalk`, `zod` (peer).

## Repurpose Notes

- To build a *headless* agent (no Panel), use `PageAgentCore` from `03-core`
  directly instead of this package.
- The `demo.ts` IIFE entry is a template for any auto-init browser script.
