# Design Lab Extension

A Gemini CLI extension that helps you make confident UI design decisions through rapid iteration.

## What It Does

Design Lab generates **multiple distinct UI variations** for any component or page, lets you compare them side-by-side in your browser, collects your feedback, and synthesizes a refined version—repeating until you're confident in the result.

Instead of guessing at the right design or going back-and-forth on revisions, you see real options, pick what works, and iterate quickly.

## Installation

```bash
gemini extensions install https://github.com/your-username/gemini-design-plugin
```

Or for local development:

```bash
gemini extensions link /path/to/gemini-design-plugin
```

## Usage

### Start a session

```
/design:start
```

Or with a specific target:

```
/design:start ProfileCard
```

### What happens next

1. **Preflight** — Detects your framework (Next.js, Vite, etc.) and styling system (Tailwind, MUI, etc.)
2. **Style inference** — Reads your existing design tokens from Tailwind config, CSS variables, or theme files
3. **Interview** — Asks about:
   - What you're designing (component vs page, new vs redesign)
   - Pain points and what should improve
   - Visual and interaction inspiration
   - Target user and key tasks
4. **Generation** — Creates 5 distinct variations exploring different:
   - Information hierarchy
   - Layout models (cards, lists, tables, split-pane)
   - Density (compact vs spacious)
   - Interaction patterns (modal, inline, drawer)
   - Visual expression
5. **Review** — Open `http://localhost:3000/__design_lab` (or your dev server port) to see all variations
6. **Feedback** — Tell Gemini:
   - If one is already good → select it, make minor tweaks
   - If you like parts of different ones → describe what you like about each, get a synthesized version
7. **Iterate** — Repeat until you're confident
8. **Finalize** — All temp files are deleted, `DESIGN_PLAN.md` is generated with implementation steps

### Clean up manually (if needed)

```
/design:cleanup
```

## Supported Frameworks

- Next.js (App Router & Pages Router)
- Vite (React, Vue)
- Remix
- Astro
- Create React App

## Supported Styling

- Tailwind CSS
- CSS Modules
- Material UI (MUI)
- Chakra UI
- Ant Design
- styled-components
- Emotion

## Tips for Best Results

1. **Be specific in the interview.** The more context about pain points, target users, and inspiration, the more distinct the variations.
2. **Reference products you admire.** "Like Linear's density" or "Stripe's clarity" gives concrete direction.
3. **Don't settle on round one.** The synthesis step is where it gets good—describe what you like about each variant.
4. **Keep your dev server running.** The extension won't start it for you.
5. **Check the DESIGN_PLAN.md.** After finalizing, this contains implementation steps and accessibility checklist.

## What Gets Created (Temporarily)

During the session:
- `.gemini-design/` — variants, previews, design brief
- `app/__design_lab/` or `pages/__design_lab.tsx` — the comparison route

All of this is deleted when you finalize or abort. Nothing is left behind.

## What Gets Created (Permanently)

After finalizing:
- `DESIGN_PLAN.md` — implementation plan for your chosen design
- `DESIGN_MEMORY.md` — captured style decisions (speeds up future sessions)

## Directory Structure

```
gemini-design-plugin/
├── gemini-extension.json    # Extension manifest
├── GEMINI.md                # Context loaded by Gemini CLI
├── commands/
│   └── design/
│       ├── start.toml       # /design:start command
│       └── cleanup.toml     # /design:cleanup command
├── templates/
│   ├── DESIGN_PLAN.md       # Output template
│   └── DESIGN_MEMORY.md     # Memory template
└── README.md
```

## License

MIT
