#!/usr/bin/env python3
from pathlib import Path

FILES = [
    Path("courses/strace/index.html"),
    Path("courses/heapdump/index.html"),
    Path("courses/jfr/index.html"),
    Path("courses/threaddump/index.html"),
]

REPLACEMENTS = [
    ("SRE strace Academy • Master Linux System Call Tracing", "strace notes · Linux system call tracing"),
    ("Heap Dump SRE Academy • Master Java Memory Analysis", "Heap dump notes · Java memory analysis"),
    ("JFR SRE Academy • Master Java Flight Recorder", "JFR notes · Java Flight Recorder"),
    ("Thread Dump SRE Academy • Master Java Concurrency Diagnostics", "Thread dump notes · Java concurrency diagnostics"),
    ("SRE strace Academy", "strace notes"),
    ("Heap Dump SRE Academy", "Heap dump notes"),
    ("JFR SRE Academy", "JFR notes"),
    ("Thread Dump SRE Academy", "Thread dump notes"),
    ("SRE Academy", "Guides"),
    ("Academy Home", "Guides"),
    ("← Academy", "← Guides"),
    (">Academy</a>", ">Guides</a>"),
    ("Official Training", "Field notes"),
    ("COURSE 3 · JAVA HEAP DUMP ANALYSIS", "HANDBOOK · JAVA HEAP DUMP ANALYSIS"),
    ("COURSE 4 · JAVA THREAD DUMP ANALYSIS", "HANDBOOK · JAVA THREAD DUMP ANALYSIS"),
    ("Master <span class=\"text-emerald-500\">strace</span><br>\n                    like a production SRE",
     "Notes on <span class=\"text-emerald-500\">strace</span><br>\n                    for production debugging"),
    ("Master <span class=\"text-violet-400\">Heap Dump</span> Analysis", "Notes on <span class=\"text-violet-400\">Heap Dump</span> analysis"),
    ("Master <span class=\"text-amber-500\">Java Flight Recorder</span>", "Notes on <span class=\"text-amber-500\">Java Flight Recorder</span>"),
    ("Master <span class=\"text-sky-400\">Thread Dump</span> Analysis", "Notes on <span class=\"text-sky-400\">Thread Dump</span> analysis"),
    ("The definitive hands-on course for diagnosing Linux applications, \n                    containers, and performance issues using the most powerful low-level debugging tool.",
     "Field notes for diagnosing Linux applications, containers, and performance issues with system call tracing."),
    ("Begin the Course", "Open the guide"),
    ("Start Learning", "Open the guide"),
    ("Browse Curriculum", "Browse sections"),
    ("Interview prep + certification", "Cheatsheet and quiz"),
    ("Complete Curriculum", "Guide sections"),
    ("19 MODULES • SELF-PACED", "19 SECTIONS"),
    ("All 6 labs from the course are available in the full training materials. These simulations demonstrate core techniques.",
     "These simulations show the core techniques."),
    ("[Website] SRE strace Training Course website initialized successfully.", "[sreroot] strace notes ready."),
    ('href="../../index.html"', 'href="../../guides.html"'),
    ("strace at kernel boundary (Course 1)", "strace at kernel boundary"),
]

SOCIAL = '''                <div class=\"flex items-center gap-x-8 mt-10\">
                    <div class=\"flex -space-x-2\">
                        <div class=\"w-8 h-8 bg-slate-700 rounded-full border border-slate-800 overflow-hidden\"><img src=\"https://i.pravatar.cc/32?img=28\" class=\"w-full h-full object-cover\"></div>
                        <div class=\"w-8 h-8 bg-slate-700 rounded-full border border-slate-800 overflow-hidden\"><img src=\"https://i.pravatar.cc/32?img=47\" class=\"w-full h-full object-cover\"></div>
                        <div class=\"w-8 h-8 bg-slate-700 rounded-full border border-slate-800 overflow-hidden\"><img src=\"https://i.pravatar.cc/32?img=12\" class=\"w-full h-full object-cover\"></div>
                    </div>
                    <div class=\"text-sm\">
                        <span class=\"font-semibold text-emerald-400\">4,872</span> SREs trained<br>
                        <span class=\"text-slate-500 text-xs\">from FAANG, fintech &amp; startups</span>
                    </div>
                </div>'''

SOCIAL_NEW = '''                <div class=\"mt-10 text-sm text-slate-500\">
                    A handbook. Not a training programme.
                </div>'''


def patch(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    if SOCIAL in text:
        text = text.replace(SOCIAL, SOCIAL_NEW)
    return text


def main() -> None:
    changed = False
    for path in FILES:
        original = path.read_text(encoding="utf-8")
        updated = patch(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            print(f"updated {path}")
            changed = True
        else:
            print(f"unchanged {path}")
    if not changed:
        print("no copy changes needed")


if __name__ == "__main__":
    main()
