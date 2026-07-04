#!/usr/bin/env python3
"""Generate heap dump and thread dump course HTML pages."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from course_builder import render_course
from dump_courses_data import HEAP_COURSE, THREAD_COURSE

ROOT = Path(__file__).resolve().parents[1]

COURSES = [
    (HEAP_COURSE, ROOT / "courses" / "heapdump" / "index.html"),
    (THREAD_COURSE, ROOT / "courses" / "threaddump" / "index.html"),
]


def main() -> None:
    for cfg, out_path in COURSES:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        html = render_course(cfg)
        out_path.write_text(html, encoding="utf-8")
        lines = html.count("\n") + 1
        print(f"Wrote {out_path.relative_to(ROOT)} ({lines} lines)")


if __name__ == "__main__":
    main()