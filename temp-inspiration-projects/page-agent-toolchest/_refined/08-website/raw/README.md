# 08-website — Docs & Landing (`@page-agent/website`)

The public marketing site + documentation + live playground at
`alibaba.github.io/page-agent`. React + Vite + Tailwind v4. **Private package**
(not published to npm) — no internal `@page-agent/*` dependencies.

## What's Here

```
src/
├── main.tsx, router.tsx          # App entry + wouter routing
├── pages/
│   ├── home/                     # ⭐ Landing page
│   │   ├── index.tsx, HeroSection, FeaturesSection, ScenariosSection, OneMoreThingSection
│   └── docs/                     # Documentation site
│       ├── index.tsx, Layout.tsx
├── components/
│   ├── APIReference.tsx          # Renders the API reference
│   ├── CodeEditor.tsx            # Live code playground
│   ├── JSConsole.tsx             # In-browser JS console (runs Page Agent live)
│   ├── Header.tsx, Footer.tsx, Heading.tsx, BetaNotice.tsx
│   ├── LanguageSwitcher.tsx, ThemeSwitcher.tsx
│   ├── HighlightSyntax.tsx       # Syntax highlighting
│   └── ui/                       # ~25 animation-heavy primitives (magic-card, aurora-text,
│                                 #   bento-grid, sparkles-text, marquee, neon-gradient-card…)
├── hooks/useGitHubStars.ts       # GitHub star count (Supabase-backed)
├── i18n/context.tsx              # en/zh locale context
├── lib/{utils.ts, useDocumentTitle.ts}
├── constants.ts, index.css, env.d.ts
```

## Purpose

1. **Landing page** — features, scenarios, demo video, install snippets.
2. **Documentation** — overview, features (models, chrome-extension, MCP), API reference.
3. **Live playground** — `CodeEditor` + `JSConsole` let visitors try Page Agent
   right in the browser using the demo LLM.

## Tech Stack

React 19, Vite 8, Tailwind CSS v4, `wouter` (router), `motion` (animations),
Radix UI primitives, `lucide-react` + `simple-icons`, `sonner` (toasts),
`next-themes` (dark mode). Heavy use of `magicui`-style animated components.

## Dependencies

**No internal `@page-agent/*` deps.** Fully standalone. External: React, motion,
Radix, Tailwind, wouter.

## Repurpose Notes

- The `ui/` folder is a grab-bag of polished animated React components
  (magic-card, aurora-text, bento-grid, sparkles-text…) — extractable for any
  marketing site.
- `CodeEditor` + `JSConsole` is a self-contained "try-it-in-browser" pattern.
- Follow `AGENTS.md` (included here) when editing — it has website-specific rules.
