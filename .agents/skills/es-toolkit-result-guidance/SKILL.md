---
name: es-toolkit-result-guidance
description: Use when refining TypeScript helpers or frontend presentation logic in this repo and you want the source-first, small-surface, low-dependency discipline learned from toss/es-toolkit without adding the package by default.
---

# es-toolkit Result Guidance

This repo-local skill distills the parts of `toss/es-toolkit` that are useful for this project's frontend/result-report work.

Grounding source used on 2026-07-01:
- `https://github.com/toss/es-toolkit`
- `README.md`
- `AGENTS.md`
- `es-toolkit-plugin/skills/recommend/SKILL.md`
- `es-toolkit-plugin/skills/migrate/SKILL.md`

## Apply this skill when

- You are adding or refactoring frontend-only TypeScript helpers.
- A component contains repeated transformation logic for scores, labels, or evidence text.
- You are tempted to add a utility dependency for a small data-shaping task.

## Core rules

1. Be source-first.
   - Verify actual data shape from local types before suggesting a helper.
   - Prefer code grounded in this repo's `AnalysisResponse` and related types over generic utility patterns.

2. Keep the 85% interface.
   - A helper should solve the common case cleanly.
   - Do not add option bags or compat-style branches unless the UI already needs them in multiple places.

3. Default to zero new runtime dependencies.
   - If built-in JavaScript and a small local helper are enough, do not install a package.
   - Only add `es-toolkit` itself when repeated transformations become noisy across multiple files and the benefit is observable.

4. Prefer modern built-ins over decorative abstraction.
   - Use `map`, `filter`, `slice`, `Object.entries`, `Intl`, template literals, and small local functions first.
   - Do not wrap a one-line transformation in a utility just to look reusable.

5. Centralize repeated presentation transforms.
   - If recommendation labels, data-mode labels, score summaries, or evidence strings appear in 2 or more places, move them into one typed helper module.

6. Keep helpers tree-shakeable in spirit.
   - Use named exports.
   - Keep helpers pure and small.
   - Separate presentation formatting from component markup.

7. Prefer straightforward loops when readability wins.
   - es-toolkit favors performance and simplicity over clever chaining.
   - If a `for` loop or one clear intermediate variable reads better than nested array chains, choose clarity.

8. Document intent, not trivia.
   - Add short comments only when a transformation would otherwise be surprising.
   - Explain why a helper exists or what consumer-language decision it protects.

## Result-page specific guidance

- Use Korean consumer language, not operator jargon.
- Keep verdict, reasons, score insight, map evidence, disclosure, and source notice as distinct primitives.
- Helpers should return display-ready values for those primitives: labels, tones, summary sentences, evidence lines, and calm fallback copy.
- Do not let helper growth turn into a mini framework. If a helper file starts carrying unrelated concerns, split by concept.
