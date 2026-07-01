---
name: report-poster-maker
description: Use when creating or updating a repo-style day report poster image from structured content, then linking that PNG into a markdown report.
---

# Report Poster Maker

Use this repo-local skill when you need a summary poster like `docs/assets/day-01-scope-freeze-poster.png` or the day2 delivery poster.

This skill is for:
- day-style project report posters
- markdown report cover images
- regenerating the same poster layout with different content

## Files

- Script: `scripts/render_report_poster.py`
- Example spec: `references/example-spec.json`

## Workflow

1. Prepare a JSON spec with:
   - `eyebrow`
   - `title_lines`
   - `lead`
   - `chips`
   - `metrics`
   - `steps`
   - `note_title`
   - `notes`

2. Render the HTML source:

```bash
python3 .agents/skills/report-poster-maker/scripts/render_report_poster.py \
  --spec docs/assets/day-02-delivery-report-poster.json \
  --html-out docs/assets/day-02-delivery-report-poster.html
```

3. Render PNG from the HTML with bundled Playwright.
   - Prefer the bundled Node + Playwright runtime already used in this repo.
   - Screenshot the local `file://...html` at `1600x947`.

4. Verify the PNG visually.
   - Check headline wrapping
   - Check chip overflow
   - Check metric card wrapping
   - Check right-side flow steps
   - Check markdown image link

5. In markdown reports under `docs/`, use a relative image path:

```md
![Poster](./assets/file-name.png)
```

## Layout contract

- Match the day1/day2 poster family:
  - soft blue atmospheric background
  - rounded white frame
  - left hero message
  - chip row
  - 2x2 metric grid
  - right flow card
  - right bottom note card
- Keep copy concise enough to fit the fixed layout.
- If text feels tight, shorten the copy before changing the layout.

## Notes

- The generated HTML uses the same font stack as the day1 poster:
  - `"Pretendard Variable", Pretendard, "Segoe UI", system-ui, sans-serif`
- The script only generates HTML from structured content.
- PNG rendering and visual QA are required before shipping.
