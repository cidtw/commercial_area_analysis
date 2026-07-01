#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def render_metric(item: dict[str, str]) -> str:
    return (
        '              <article class="metric-card">\n'
        f'                <span>{esc(item["label"])}</span>\n'
        f'                <strong>{esc(item["title"])}</strong>\n'
        f'                <p>{esc(item["body"])}</p>\n'
        '              </article>'
    )


def render_step(item: dict[str, str]) -> str:
    return (
        '              <div class="flow-step">\n'
        f'                <span>{esc(item["number"])}</span>\n'
        f'                <strong>{esc(item["title"])}</strong>\n'
        f'                <p>{esc(item["body"])}</p>\n'
        '              </div>'
    )


def render_note(item: str) -> str:
    return (
        '                <div class="note-item">\n'
        '                  <span class="dot"></span>\n'
        f'                  <span>{esc(item)}</span>\n'
        '                </div>'
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--html-out", required=True)
    args = parser.parse_args()

    spec_path = Path(args.spec)
    out_path = Path(args.html_out)
    template_path = Path(__file__).resolve().parent.parent / "references" / "poster-template.html"

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    template = template_path.read_text(encoding="utf-8")

    replacements = {
        "__TITLE__": esc(spec["eyebrow"]) + " Poster",
        "__EYEBROW__": esc(spec["eyebrow"]),
        "__TITLE_LINES__": "<br />".join(esc(line) for line in spec["title_lines"]),
        "__LEAD__": esc(spec["lead"]),
        "__CHIPS__": "\n".join(
            f'              <span class="chip">{esc(chip)}</span>' for chip in spec["chips"]
        ),
        "__METRICS__": "\n".join(render_metric(item) for item in spec["metrics"]),
        "__STEPS__": "\n".join(render_step(item) for item in spec["steps"]),
        "__NOTE_TITLE__": esc(spec["note_title"]),
        "__NOTES__": "\n".join(render_note(item) for item in spec["notes"]),
    }

    for key, value in replacements.items():
        template = template.replace(key, value)

    out_path.write_text(template, encoding="utf-8")


if __name__ == "__main__":
    main()
