#!/usr/bin/env python3
"""Generate courses/jfr/index.html from content/sre-jfr-training-course.md"""

import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jfr_enrichments import (
    FLOWCHARTS,
    INTERVIEW_QUESTIONS,
    MODULE_ENRICHMENTS,
    WAR_STORY_DETAILS,
)

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "content" / "sre-jfr-training-course.md"
OUT_PATH = ROOT / "courses" / "jfr" / "index.html"

MODULE_TITLES = [
    ("module-1", "Introduction to JFR", "What JFR is, architecture, and how it differs from other JVM tools."),
    ("module-2", "Why Every SRE Should Learn JFR", "Metrics show what; logs show when; JFR shows why inside the JVM."),
    ("module-3", "JVM Internals Required for JFR", "Heap, metaspace, GC, safepoints, JIT, and TLAB fundamentals."),
    ("module-4", "Capturing JFR Recordings", "jcmd, startup flags, emergency capture during incidents."),
    ("module-5", "Understanding JFR Events", "CPU, memory, GC, threads, I/O, and exception event categories."),
    ("module-6", "Using Java Mission Control (JMC)", "Automated analysis, flame graphs, locks, and memory views."),
    ("module-7", "CPU Troubleshooting with JFR", "Hot methods, JIT storms, and CPU spike investigation."),
    ("module-8", "Memory Leak Analysis", "Allocation hotspots, TLAB events, and leak patterns."),
    ("module-9", "Garbage Collection Analysis", "Pause times, promotion failures, and GC tuning signals."),
    ("module-10", "Thread Analysis", "Runnable, blocked, waiting states and pool starvation."),
    ("module-11", "Lock Contention Analysis", "JavaMonitorEnter, ThreadPark, and contended locks."),
    ("module-12", "Database Troubleshooting", "JDBC latency, connection pool exhaustion, HikariCP."),
    ("module-13", "API Latency Investigation", "End-to-end JVM time breakdown for slow requests."),
    ("module-14", "Exception Analysis", "ExceptionThrow storms and hidden retry loops."),
    ("module-15", "Kubernetes and JFR", "kubectl exec, ephemeral containers, OOMKilled pods."),
    ("module-16", "JFR and Spring Boot", "Controllers, Jackson, @Async, and startup bottlenecks."),
    ("module-17", "Kafka Troubleshooting with JFR", "Deserialization, rebalance storms, producer latency."),
    ("module-18", "SRE Incident War Stories", "Real production incidents solved with JFR evidence."),
    ("module-19", "JFR vs Other Tools", "Decision tree: JFR vs async-profiler, jstack, perf, heap dumps."),
    ("module-20", "SRE Production Playbook", "Incident response flow and emergency JFR commands."),
]

BONUS = [
    ("JVM Tuning Using JFR", "Right-size heap, thread pools, and connection pools from real data."),
    ("Continuous Profiling with JFR", "Low-overhead always-on recordings in production."),
    ("AI-Assisted JFR Analysis", "Export recordings and use LLMs for RCA drafts."),
]

LABS = [
    ("Capture JFR from a running Spring Boot app", "Use jcmd to start a 5-minute profile recording."),
    ("Analyze CPU hotspot using JMC Flame Graphs", "Find methods consuming >10% CPU during a spike."),
    ("Find a memory leak before OOM", "Use allocation events to identify growing object types."),
    ("Diagnose lock contention", "Correlate JavaMonitorEnter with Lock Instances view."),
    ("Investigate GC pauses in G1 vs ZGC", "Compare jdk.GCPhasePause across collectors."),
    ("Capture JFR from a Kubernetes pod", "kubectl exec + jcmd + kubectl cp workflow."),
    ("Correlate JFR with Prometheus metrics", "Overlay JVM events with latency spike window."),
]

WAR_STORIES = [
    "eCommerce checkout slowness", "Payment processing timeouts", "Inventory service OOM",
    "Kafka rebalance storms", "MongoDB driver issues", "PostgreSQL connection pool exhaustion",
    "Redis latency spikes", "Kubernetes OOMKilled pods", "API P99 degradation",
    "Spring Boot startup delays",
]

QUIZ = [
    ("What does JFR stand for?", ["Java Fast Recorder", "Java Flight Recorder", "JVM Fault Reporter", "Java Frame Recorder"], 1, "JFR is Java Flight Recorder — built into the JVM."),
    ("Typical production overhead of JFR?", ["10-20%", "Less than 1%", "5-8%", "25%+"], 1, "JFR is designed for <1% overhead in production."),
    ("Best command to start a JFR recording on a running JVM?", ["jstack", "jcmd <PID> JFR.start", "jmap -heap", "jconsole"], 1, "jcmd is the recommended way to control JFR on live processes."),
    ("Which tool is best for analyzing .jfr files?", ["VisualVM", "Java Mission Control (JMC)", "JConsole", "jhat"], 1, "JMC is the official analyzer with automated rules."),
    ("Which JFR event indicates lock contention?", ["jdk.SocketRead", "jdk.JavaMonitorEnter", "jdk.GarbageCollection", "jdk.ClassLoad"], 1, "JavaMonitorEnter shows threads waiting for monitors."),
    ("First view to check in JMC during incident analysis?", ["Event Browser", "Automated Analysis", "Threads only", "I/O view"], 1, "Automated Analysis often highlights problems immediately."),
    ("What does jdk.GCPhasePause help diagnose?", ["Network latency", "GC pause times and causes", "Thread deadlocks", "Class loading"], 1, "GCPhasePause shows individual GC pause durations."),
    ("Safest way to capture JFR in a Kubernetes distroless pod?", ["Install JDK in app image", "Ephemeral debug container", "Restart pod with debug flags", "SSH to node only"], 1, "Ephemeral containers avoid modifying production images."),
    ("JFR allocation events useful for finding?", ["DNS issues", "Memory leaks and hotspots", "Port conflicts", "Disk full errors"], 1, "ObjectAllocation events reveal what's being allocated most."),
    ("When should you use heap dump instead of JFR first?", ["CPU spike", "Post-mortem after OOM with object graph needed", "Lock contention", "Kafka lag"], 1, "Heap dumps give full object graphs for post-mortem leak analysis."),
]


def md_to_html_block(text: str) -> str:
    lines = text.strip().splitlines()
    out = []
    in_code = False
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal table_rows, in_table
        if not table_rows:
            return ""
        html_rows = []
        for i, row in enumerate(table_rows):
            cells = [c.strip() for c in row.strip("|").split("|")]
            if all(re.match(r"^[-:]+$", c) or c == "" for c in cells):
                continue
            tag = "th" if i == 0 else "td"
            cls = "text-left py-3 px-4 font-semibold" if tag == "th" else "py-3 px-4"
            html_rows.append("<tr>" + "".join(f"<{tag} class=\"{cls}\">{inline(c)}</{tag}>" for c in cells) + "</tr>")
        table_rows = []
        in_table = False
        return '<div class="my-6 overflow-x-auto"><table class="w-full text-sm"><tbody class="divide-y divide-slate-700 text-slate-300">' + "".join(html_rows) + "</tbody></table></div>"

    def inline(s: str) -> str:
        s = html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"`([^`]+)`", r'<code class="jfr-code">\1</code>', s)
        s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
        return s

    for line in lines:
        if line.startswith("```"):
            if in_code:
                out.append("</pre></div>")
                in_code = False
            else:
                out.append('<div class="my-4"><div class="code-header">terminal</div><pre class="jfr-output">')
                in_code = True
            continue
        if in_code:
            out.append(html.escape(line) + "\n")
            continue
        if "|" in line and line.strip().startswith("|"):
            if not in_table and table_rows:
                pass
            in_table = True
            table_rows.append(line)
            continue
        elif in_table:
            out.append(flush_table())

        if line.startswith("### "):
            out.append(f'<h4 class="font-semibold text-amber-400 mt-6 mb-3">{inline(line[4:])}</h4>')
        elif line.startswith("## "):
            out.append(f'<h3 class="text-xl font-semibold mt-6 mb-3 text-slate-100">{inline(line[3:])}</h3>')
        elif line.startswith("- "):
            out.append(f'<li class="mb-1">{inline(line[2:])}</li>')
        elif re.match(r"^\d+\.\s", line):
            item = re.sub(r"^\d+\.\s", "", line)
            out.append(f'<li class="mb-1">{inline(item)}</li>')
        elif line.strip() == "":
            out.append("")
        elif line.strip() == "---":
            out.append('<hr class="border-slate-700 my-8">')
        else:
            out.append(f'<p class="text-slate-300 mb-4">{inline(line)}</p>')

    if in_table:
        out.append(flush_table())
    if in_code:
        out.append("</pre></div>")

    body = "\n".join(out)
    body = re.sub(r"(<li[^>]*>.*?</li>\s*)+", lambda m: '<ul class="list-disc pl-5 mb-4 text-slate-300">' + m.group(0) + "</ul>", body, flags=re.DOTALL)
    return body


def extract_module(num: int, md: str) -> str:
    pattern = rf"# Module {num}:.*?(?=\n# Module {num + 1}:|\n# Bonus|\n## Bonus|\n## Hands-on|\Z)"
    m = re.search(pattern, md, re.DOTALL)
    if not m:
        pattern = rf"# Module {num}:.*?(?=\n# |\Z)"
        m = re.search(pattern, md, re.DOTALL)
    if not m:
        return "<p class=\"text-slate-400\">Content coming soon.</p>"
    content = m.group(0)
    content = re.sub(r"^# Module \d+:.*\n", "", content, count=1)
    return md_to_html_block(content)


def extract_section(name: str, md: str) -> str:
    patterns = {
        "cheat": r"## JFR Production Cheat Sheet(.*?)(?=## Troubleshooting|\Z)",
        "playbook": r"# Module 20:.*?(?=## Bonus|\Z)",
        "bonus": r"## Bonus Modules.*?(?=## Hands-on|\Z)",
        "labs_md": r"## Hands-on Labs(.*?)(?=## Interview|\Z)",
    }
    m = re.search(patterns.get(name, ""), md, re.DOTALL)
    return md_to_html_block(m.group(1) if m and name != "playbook" else (m.group(0) if m else ""))


def build_curriculum_cards() -> str:
    cards = []
    for i, (_, title, desc) in enumerate(MODULE_TITLES, 1):
        cards.append(f'''
            <div onclick="document.getElementById('module-{i}').scrollIntoView({{behavior:'smooth'}})" class="module-card cursor-pointer bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-3xl p-5 group">
                <span class="jfr-badge">Module {i}</span>
                <h4 class="font-semibold mt-3 text-lg group-hover:text-amber-400 transition">{html.escape(title)}</h4>
                <p class="text-xs text-slate-500 mt-2 line-clamp-2">{html.escape(desc)}</p>
            </div>''')
    return "\n".join(cards)


def build_war_stories_html() -> str:
    cards = []
    for title, sev, impact, metrics, jfr, root, fix, lesson in WAR_STORY_DETAILS:
        sev_color = "text-red-400" if sev == "SEV1" else "text-amber-400"
        cards.append(f'''
            <div class="mb-6 p-6 bg-slate-950 border border-slate-700 rounded-2xl">
                <div class="flex flex-wrap items-center gap-3 mb-3">
                    <h4 class="font-semibold text-lg">{html.escape(title)}</h4>
                    <span class="text-xs px-2 py-0.5 bg-slate-800 {sev_color} rounded">{html.escape(sev)}</span>
                </div>
                <p class="text-sm text-slate-400 mb-3"><strong>Impact:</strong> {html.escape(impact)}</p>
                <p class="text-sm text-slate-300 mb-2"><span class="text-amber-400 font-medium">Metrics/Logs:</span> {html.escape(metrics)}</p>
                <p class="text-sm text-slate-300 mb-2"><span class="text-amber-400 font-medium">JFR evidence:</span> {html.escape(jfr)}</p>
                <p class="text-sm text-slate-300 mb-2"><span class="text-red-400 font-medium">Root cause:</span> {html.escape(root)}</p>
                <p class="text-sm text-slate-300 mb-2"><span class="text-emerald-400 font-medium">Resolution:</span> {html.escape(fix)}</p>
                <p class="text-xs text-slate-500 mt-3 italic">Lesson: {html.escape(lesson)}</p>
            </div>''')
    return "\n".join(cards)


def build_detailed_modules(md: str) -> str:
    sections = []
    for i, (_, title, _) in enumerate(MODULE_TITLES, 1):
        content = extract_module(i, md)
        content = re.sub(r'<hr class="border-slate-700 my-8">', "", content)
        if i == 18:
            content = re.sub(
                r"<p class=\"text-slate-300 mb-4\">\(20 detailed.*?</ul>",
                "",
                content,
                flags=re.DOTALL,
            )
            content += build_war_stories_html()
        enrich = MODULE_ENRICHMENTS.get(i, "")
        sections.append(f'''
            <div id="module-{i}" class="module-section mb-16 bg-slate-900 border border-slate-700 rounded-3xl p-8">
                <div class="flex items-center gap-x-4 mb-6">
                    <span class="px-4 py-1.5 text-sm font-bold bg-amber-900 text-amber-300 rounded-2xl">MODULE {i}</span>
                    <h3 class="text-3xl font-bold tracking-tight">{html.escape(title)}</h3>
                </div>
                <div class="lesson-content">{content}{enrich}</div>
            </div>''')
    bonus_html = ""
    bonus_details = [
        ("Tune -Xmx from allocation rate trends in JFR", "Size thread pools from actual Runnable vs Waiting ratio", "Set HikariCP maxPoolSize from connection wait events"),
        ("Run settings=default continuously with maxage=1h", "Dump on alert via webhook + jcmd sidecar", "Store .jfr in object storage for trend analysis"),
        ("Export event summary to JSON for LLM input", "Prompt: summarize hot methods, GC, and lock contention", "Generate draft RCA for human review — never auto-close incidents"),
    ]
    for (title, desc), details in zip(BONUS, bonus_details):
        items = "".join(f"<li class=\"mb-1\">{html.escape(d)}</li>" for d in details)
        bonus_html += f'''<div class="p-5 bg-slate-950 border border-slate-700 rounded-2xl mb-4">
            <h4 class="font-semibold text-amber-400">{html.escape(title)}</h4>
            <p class="text-sm text-slate-400 mt-2 mb-3">{html.escape(desc)}</p>
            <ul class="list-disc pl-5 text-sm text-slate-300">{items}</ul>
        </div>'''
    sections.append(f'''
        <div id="bonus-modules" class="module-section mb-16 bg-slate-900 border border-slate-700 rounded-3xl p-8">
            <div class="flex items-center gap-x-4 mb-6">
                <span class="px-4 py-1.5 text-sm font-bold bg-amber-900 text-amber-300 rounded-2xl">BONUS</span>
                <h3 class="text-3xl font-bold tracking-tight">Bonus Modules</h3>
            </div>
            {bonus_html}
        </div>''')
    return "\n".join(sections)


def build_labs() -> str:
    items = []
    for i, (title, desc) in enumerate(LABS, 1):
        sim = ""
        if i <= 3:
            sim = f'''<button onclick="simulateLab({i})" class="self-start px-5 py-2 text-sm font-medium bg-amber-600 hover:bg-amber-500 rounded-2xl flex items-center gap-x-2">
                <i class="fa-solid fa-play"></i><span>Simulate</span></button>'''
        items.append(f'''
            <div class="border border-slate-700 bg-slate-900 rounded-3xl p-6">
                <div class="flex justify-between gap-4">
                    <div>
                        <span class="font-mono text-xs bg-amber-900 text-amber-300 px-2.5 py-px rounded">LAB {i}</span>
                        <h4 class="font-semibold text-xl mt-2">{html.escape(title)}</h4>
                        <p class="text-sm text-slate-400 mt-1">{html.escape(desc)}</p>
                    </div>
                    {sim}
                </div>
            </div>''')
    return "\n".join(items)


def build_interview_section() -> str:
    items = []
    for i, (q, a) in enumerate(INTERVIEW_QUESTIONS, 1):
        items.append(f'''
            <div class="p-5 bg-slate-950 border border-slate-700 rounded-2xl">
                <div class="text-amber-400 text-xs font-mono mb-2">Q{i}</div>
                <p class="font-medium mb-2">{html.escape(q)}</p>
                <p class="text-sm text-slate-400">{html.escape(a)}</p>
            </div>''')
    return "\n".join(items)


def build_flowcharts_section() -> str:
    items = []
    for title, steps in FLOWCHARTS:
        flow = " → ".join(html.escape(s) for s in steps)
        items.append(f'''
            <div class="p-5 bg-slate-900 border border-slate-700 rounded-2xl">
                <h4 class="font-semibold text-amber-400 mb-3">{html.escape(title)}</h4>
                <p class="text-sm text-slate-300 leading-relaxed">{flow}</p>
            </div>''')
    return "\n".join(items)


def build_war_stories() -> str:
    return "".join(f'<span class="text-xs px-3 py-1.5 bg-slate-800 rounded-full border border-slate-700">{html.escape(s)}</span>' for s in WAR_STORIES)


def build_quiz_js() -> str:
    return json.dumps([{"q": q, "options": o, "answer": a, "explanation": e} for q, o, a, e in QUIZ])


def main():
    md = MD_PATH.read_text(encoding="utf-8")
    quiz_data = build_quiz_js()

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JFR SRE Academy • Master Java Flight Recorder</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Space+Grotesk:wght@500;600&display=swap');
        :root {{ --primary: #f59e0b; }}
        body {{ font-family: 'Inter', system-ui, sans-serif; }}
        .font-display {{ font-family: 'Space Grotesk', 'Inter', sans-serif; font-weight: 600; }}
        .section-header {{ font-size: 2.25rem; line-height: 2.5rem; font-weight: 700; letter-spacing: -0.025em; }}
        .module-card {{ transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }}
        .module-card:hover {{ transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1); }}
        .jfr-code, .jfr-output code {{ font-family: ui-monospace, Consolas, monospace; }}
        .jfr-code {{ background: #0f172a; padding: 2px 6px; border-radius: 4px; font-size: 0.875rem; }}
        .jfr-output {{ background: #020617; color: #e0e7ff; padding: 1rem; border-radius: 0 0 0.5rem 0.5rem; overflow-x: auto; font-size: 0.875rem; border: 1px solid #334155; white-space: pre-wrap; }}
        .code-header {{ background: #1e2937; padding: 0.5rem 1rem; border-radius: 0.5rem 0.5rem 0 0; font-size: 0.75rem; color: #64748b; }}
        .jfr-badge {{ background: #78350f; color: #fcd34d; font-size: 0.75rem; padding: 0.125rem 0.5rem; border-radius: 9999px; font-weight: 500; }}
        .module-section {{ scroll-margin-top: 80px; }}
        .lesson-content h3 {{ font-size: 1.25rem; font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.75rem; }}
        .nav-link:hover {{ color: #f59e0b; }}
    </style>
</head>
<body class="bg-slate-950 text-slate-200">
    <nav class="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
        <div class="max-w-screen-2xl mx-auto px-8 py-4 flex items-center justify-between">
            <a href="../../index.html" class="flex items-center gap-3">
                <div class="w-10 h-10 bg-amber-600 rounded-xl flex items-center justify-center"><i class="fa-brands fa-java text-white text-2xl"></i></div>
                <div><span class="font-display text-2xl font-semibold">JFR</span><span class="font-display text-2xl text-amber-500">SRE</span></div>
            </a>
            <div class="hidden md:flex items-center gap-8 text-sm">
                <a href="#curriculum" class="nav-link text-slate-300">Curriculum</a>
                <a href="#labs" class="nav-link text-slate-300">Labs</a>
                <a href="#quiz" class="nav-link text-slate-300">Quiz</a>
                <a href="#cheatsheet" class="nav-link text-slate-300">Cheat Sheet</a>
                <a href="#interview" class="nav-link text-slate-300">Interview</a>
                <a href="../../index.html" class="text-slate-500 hover:text-white text-xs">← Academy</a>
            </div>
            <button class="md:hidden text-slate-400" onclick="toggleMobileMenu()"><i class="fa-solid fa-bars text-xl"></i></button>
        </div>
    </nav>

    <div class="max-w-screen-2xl mx-auto pt-16 pb-20 px-8">
        <div class="grid md:grid-cols-12 gap-12 items-center">
            <div class="md:col-span-7">
                <div class="inline-flex items-center gap-2 px-3 py-1 bg-slate-800 text-amber-400 rounded-full text-xs font-medium mb-6">
                    <i class="fa-solid fa-shield-halved"></i> FOR SREs &amp; PLATFORM ENGINEERS
                </div>
                <h1 class="text-5xl md:text-6xl font-display font-bold tracking-tight mb-4">Master <span class="text-amber-500">Java Flight Recorder</span></h1>
                <p class="text-xl text-slate-400 mb-8 max-w-lg">Production-grade JVM diagnostics — CPU, memory, GC, locks, JDBC, Kafka, and Kubernetes. The definitive low-overhead profiler built into the JDK.</p>
                <div class="flex flex-wrap gap-4 mb-8">
                    <button onclick="startCourse()" class="px-8 py-3.5 bg-amber-600 hover:bg-amber-500 text-slate-950 font-semibold rounded-3xl flex items-center gap-2">
                        <i class="fa-solid fa-play"></i> Start Learning
                    </button>
                    <button onclick="document.getElementById('curriculum').scrollIntoView({{behavior:'smooth'}})" class="px-6 py-3.5 border border-slate-700 rounded-3xl">Browse Curriculum</button>
                </div>
            </div>
            <div class="md:col-span-5">
                <div class="bg-slate-900 border border-slate-800 rounded-3xl p-8">
                    <div class="grid grid-cols-3 gap-4 text-center mb-6">
                        <div><div class="text-3xl font-bold text-amber-400">20</div><div class="text-xs text-slate-500 mt-1">Modules</div></div>
                        <div><div class="text-3xl font-bold text-amber-400">8</div><div class="text-xs text-slate-500 mt-1">War Stories</div></div>
                        <div><div class="text-3xl font-bold text-amber-400">7</div><div class="text-xs text-slate-500 mt-1">Labs</div></div>
                    </div>
                    <div class="border-t border-slate-800 pt-4 space-y-3 text-sm">
                        <div class="flex gap-2"><i class="fa-solid fa-check text-amber-400"></i><span>jcmd + JMC production playbooks</span></div>
                        <div class="flex gap-2"><i class="fa-solid fa-check text-amber-400"></i><span>Spring Boot, Kafka, K8s workflows</span></div>
                        <div class="flex gap-2"><i class="fa-solid fa-check text-amber-400"></i><span>8 detailed incident war stories</span></div>
                        <div class="flex gap-2"><i class="fa-solid fa-check text-amber-400"></i><span>Interview prep + troubleshooting flows</span></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="max-w-screen-2xl mx-auto px-8 py-12 border-t border-slate-800">
        <h2 class="section-header mb-4">When metrics and logs aren't enough</h2>
        <p class="text-slate-400 max-w-2xl mb-8">Metrics tell you <strong class="text-white">what</strong>. Logs tell you <strong class="text-white">when</strong>. JFR tells you <strong class="text-amber-400">why</strong> — inside the JVM at the moment of the incident.</p>
        <div class="grid md:grid-cols-3 gap-6">
            <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6"><i class="fa-solid fa-microchip text-amber-400 text-2xl mb-3"></i><h3 class="font-semibold text-lg mb-2">CPU Spikes</h3><p class="text-sm text-slate-400">Hot methods, JIT storms, infinite loops — flame graphs from production.</p></div>
            <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6"><i class="fa-solid fa-memory text-amber-400 text-2xl mb-3"></i><h3 class="font-semibold text-lg mb-2">Memory Leaks</h3><p class="text-sm text-slate-400">Allocation hotspots before OOMKill — find leaking classes early.</p></div>
            <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6"><i class="fa-brands fa-docker text-amber-400 text-2xl mb-3"></i><h3 class="font-semibold text-lg mb-2">Kubernetes</h3><p class="text-sm text-slate-400">Capture JFR from pods with ephemeral containers and kubectl workflows.</p></div>
        </div>
    </div>

    <div id="curriculum" class="max-w-screen-2xl mx-auto px-8 py-16 border-t border-slate-800">
        <span class="text-amber-400 text-sm font-semibold">20 MODULES + 3 BONUS</span>
        <h2 class="section-header mt-2 mb-8">Complete Curriculum</h2>
        <div class="relative hidden md:block mb-6 w-64">
            <input type="text" id="search-input" placeholder="Search modules..." class="w-full bg-slate-900 border border-slate-700 rounded-2xl py-2.5 pl-10 pr-4 text-sm focus:border-amber-600 focus:outline-none">
            <i class="fa-solid fa-search absolute left-4 top-3 text-slate-500"></i>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">{build_curriculum_cards()}</div>
    </div>

    <div id="modules-detail" class="max-w-screen-2xl mx-auto px-8 py-12 border-t border-slate-800 bg-slate-900/30">
        <div class="max-w-4xl mx-auto">
            <h2 class="text-3xl font-bold mb-2">Detailed Module Content</h2>
            <p class="text-slate-400 mb-10">Full explanations from the SRE JFR training course</p>
            {build_detailed_modules(md)}
        </div>
    </div>

    <div id="labs" class="max-w-screen-2xl mx-auto px-8 py-16 border-t border-slate-800">
        <span class="text-amber-400 font-semibold text-sm">PRACTICAL EXPERIENCE</span>
        <h2 class="section-header mt-2 mb-8">Hands-on Labs</h2>
        <div class="max-w-4xl mx-auto space-y-4">{build_labs()}</div>
        <p class="text-center text-xs text-slate-500 mt-6 max-w-2xl mx-auto">Labs 1–3 include interactive simulations. Labs 4–7 are designed for hands-on practice in your own JVM or Kubernetes environment.</p>
    </div>

    <div id="quiz" class="max-w-screen-2xl mx-auto px-8 py-16 border-t border-slate-800 bg-slate-900">
        <div class="max-w-3xl mx-auto text-center">
            <span class="text-amber-400 font-semibold">TEST YOUR KNOWLEDGE</span>
            <h2 class="section-header mt-2 mb-2">Interactive JFR Quiz</h2>
            <p class="text-slate-400 mb-8">10 questions · Instant feedback</p>
            <div id="quiz-container" class="bg-slate-950 border border-slate-700 rounded-3xl p-8">
                <div id="quiz-start">
                    <i class="fa-solid fa-question-circle text-6xl text-amber-600 mb-6"></i>
                    <h3 class="text-2xl font-semibold mb-2">Ready to test your JFR expertise?</h3>
                    <p class="text-slate-400 mb-8 max-w-md mx-auto">Covers jcmd, JMC, GC, locks, Kubernetes capture, and tool selection.</p>
                    <button onclick="startQuiz()" class="px-10 py-3.5 bg-amber-600 hover:bg-amber-500 text-slate-950 font-semibold rounded-3xl text-lg">Start Quiz</button>
                </div>
                <div id="quiz-questions" class="hidden text-left"></div>
                <div id="quiz-results" class="hidden py-6">
                    <div id="quiz-score" class="text-6xl font-bold text-amber-400 mb-2"></div>
                    <div class="text-xl font-semibold mb-6">Your Score</div>
                    <p id="quiz-feedback" class="max-w-md mx-auto text-slate-300 mb-8"></p>
                    <button onclick="restartQuiz()" class="px-8 py-2.5 border border-slate-600 hover:bg-slate-800 rounded-2xl text-sm">Try Again</button>
                </div>
            </div>
        </div>
    </div>

    <div id="interview" class="max-w-screen-2xl mx-auto px-8 py-16 border-t border-slate-800">
        <span class="text-amber-400 font-semibold text-sm">INTERVIEW PREP</span>
        <h2 class="section-header mt-2 mb-8">Common Interview Questions</h2>
        <div class="max-w-3xl mx-auto grid gap-4">{build_interview_section()}</div>
    </div>

    <div id="flowcharts" class="max-w-screen-2xl mx-auto px-8 py-16 border-t border-slate-800 bg-slate-900/30">
        <span class="text-amber-400 font-semibold text-sm">TROUBLESHOOTING</span>
        <h2 class="section-header mt-2 mb-8">Investigation Flowcharts</h2>
        <div class="max-w-4xl mx-auto grid md:grid-cols-2 gap-4">{build_flowcharts_section()}</div>
    </div>

    <div id="cheatsheet" class="max-w-screen-2xl mx-auto px-8 py-16 border-t border-slate-800">
        <h2 class="section-header mb-8">JFR Production Cheat Sheet</h2>
        <div class="grid lg:grid-cols-2 gap-6 max-w-5xl">
            <div class="bg-slate-900 border border-slate-700 rounded-3xl p-6">
                <h4 class="font-semibold text-amber-400 mb-4">Start Recording</h4>
                <pre class="jfr-output rounded-2xl">jcmd &lt;PID&gt; JFR.start name=Prod duration=300s filename=/tmp/recording.jfr settings=profile</pre>
            </div>
            <div class="bg-slate-900 border border-slate-700 rounded-3xl p-6">
                <h4 class="font-semibold text-amber-400 mb-4">Emergency Dump</h4>
                <pre class="jfr-output rounded-2xl">jcmd &lt;PID&gt; JFR.dump filename=/tmp/emergency.jfr</pre>
            </div>
            <div class="bg-slate-900 border border-slate-700 rounded-3xl p-6">
                <h4 class="font-semibold text-amber-400 mb-4">Key JMC Views</h4>
                <ul class="text-sm text-slate-300 space-y-2">
                    <li>Automated Analysis (start here)</li>
                    <li>Method Profiling / Flame Graph</li>
                    <li>Memory → Allocations</li>
                    <li>Threads · Lock Instances</li>
                </ul>
            </div>
            <div class="bg-slate-900 border border-slate-700 rounded-3xl p-6">
                <h4 class="font-semibold text-amber-400 mb-4">Events to Watch</h4>
                <ul class="text-sm font-mono text-slate-300 space-y-1">
                    <li>jdk.ObjectAllocation*</li>
                    <li>jdk.GCPhasePause</li>
                    <li>jdk.JavaMonitorEnter</li>
                    <li>jdk.ThreadPark</li>
                    <li>jdk.ExceptionThrow</li>
                </ul>
            </div>
        </div>
        <div class="max-w-5xl mt-8 bg-slate-900 border border-slate-700 rounded-3xl p-8">
            <h4 class="font-semibold text-lg mb-4">SRE Production Playbook</h4>
            <pre class="jfr-output rounded-2xl text-sm">Alert triggered → Metrics (Prometheus) → Logs (ELK/Loki) → Capture JFR → Analyze in JMC → Correlate (strace/top) → Root cause → Fix → Postmortem</pre>
        </div>
    </div>

    <footer class="border-t border-slate-800 bg-slate-900 py-12">
        <div class="max-w-screen-2xl mx-auto px-8 text-sm text-slate-500 flex flex-col md:flex-row justify-between gap-4">
            <span>© 2026 JFR SRE Academy</span>
            <div class="flex gap-5">
                <a href="../../index.html" class="hover:text-slate-300">SRE Academy</a>
                <a href="../strace/index.html" class="hover:text-slate-300">Course 1: strace</a>
                <a href="https://github.com/ManjuReddyT/sre-pages" target="_blank" rel="noopener" class="hover:text-slate-300">GitHub</a>
            </div>
        </div>
    </footer>

    <script>
        const quizData = {quiz_data};

        function startCourse() {{
            document.getElementById('curriculum').scrollIntoView({{ behavior: 'smooth' }});
            showToast('Welcome! Explore 20 modules, 8 war stories, labs, and the production cheat sheet.');
        }}

        function showToast(message) {{
            const toast = document.createElement('div');
            toast.className = 'fixed bottom-6 left-1/2 -translate-x-1/2 bg-slate-800 border border-slate-700 px-6 py-3.5 rounded-3xl flex items-center gap-3 shadow-2xl z-[70]';
            toast.innerHTML = '<i class="fa-solid fa-check-circle text-amber-400"></i><span class="text-sm">' + message + '</span>';
            document.body.appendChild(toast);
            setTimeout(() => {{ toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }}, 4000);
        }}

        function toggleMobileMenu() {{
            const m = document.createElement('div');
            m.className = 'md:hidden fixed inset-0 bg-slate-950/95 z-[60] p-8';
            m.innerHTML = '<button onclick="this.parentElement.remove()" class="text-3xl mb-8">×</button><div class="flex flex-col gap-4 text-xl"><a href="#curriculum">Curriculum</a><a href="#labs">Labs</a><a href="#quiz">Quiz</a><a href="#cheatsheet">Cheat Sheet</a><a href="#interview">Interview</a><a href="../../index.html">Academy Home</a></div>';
            document.body.appendChild(m);
        }}

        function simulateLab(n) {{
            const labs = {{
                1: {{ title: 'Lab 1: Capture JFR from Spring Boot', output: 'jcmd 18472 JFR.start name=SpringBoot duration=300s filename=/tmp/checkout.jfr settings=profile\\nStarted recording 1. No events currently enabled.', insight: 'Recording started on PID 18472. After 5 minutes, open /tmp/checkout.jfr in JMC.' }},
                2: {{ title: 'Lab 2: CPU Flame Graph', output: 'JMC Automated Analysis:\\n  Problem: Method com.acme.JsonUtil.serialize consumes 38.2% of CPU\\n  Recommendation: Review hot path allocation and caching', insight: 'Flame graph shows serialization dominating CPU — typical during traffic spikes.' }},
                3: {{ title: 'Lab 3: Memory Leak Before OOM', output: 'Top allocations (60s window):\\n  java.util.concurrent.ConcurrentHashMap$Node  1.8 GB\\n  com.acme.cache.SessionEntry                   1.2 GB', insight: 'Growing SessionEntry count in ConcurrentHashMap — leak before heap exhaustion.' }}
            }};
            const lab = labs[n];
            const modal = document.createElement('div');
            modal.className = 'fixed inset-0 bg-black/70 flex items-center justify-center z-[80] p-6';
            modal.innerHTML = `<div class="bg-slate-900 border border-slate-700 w-full max-w-2xl rounded-3xl overflow-hidden">
                <div class="px-6 py-4 border-b border-slate-700 flex justify-between bg-slate-950">
                    <span class="font-semibold">${{lab.title}}</span>
                    <button onclick="this.closest('.fixed').remove()" class="text-xl">×</button>
                </div>
                <div class="p-6 text-sm">
                    <pre class="jfr-output rounded-2xl mb-4 text-xs">${{lab.output}}</pre>
                    <div class="bg-amber-950/30 border border-amber-900 p-4 rounded-2xl text-xs"><strong class="text-amber-400">SRE insight:</strong> ${{lab.insight}}</div>
                    <button onclick="this.closest('.fixed').remove()" class="mt-5 w-full py-2.5 bg-amber-600 rounded-2xl font-medium">Close</button>
                </div></div>`;
            document.body.appendChild(modal);
        }}

        document.getElementById('search-input')?.addEventListener('input', function() {{
            const t = this.value.toLowerCase();
            document.querySelectorAll('.module-card, .module-section').forEach(el => {{
                el.style.display = !t || el.textContent.toLowerCase().includes(t) ? '' : 'none';
            }});
        }});

        let cq = 0, score = 0;
        function startQuiz() {{
            cq = 0; score = 0;
            document.getElementById('quiz-start').classList.add('hidden');
            document.getElementById('quiz-results').classList.add('hidden');
            document.getElementById('quiz-questions').classList.remove('hidden');
            showQ();
        }}
        function showQ() {{
            const q = quizData[cq];
            const pct = Math.round((cq / quizData.length) * 100);
            document.getElementById('quiz-questions').innerHTML = `
                <div class="mb-6">
                    <div class="flex justify-between text-xs mb-1.5"><span class="text-amber-400 font-medium">QUESTION ${{cq+1}} / ${{quizData.length}}</span><span class="text-slate-400">${{pct}}% complete</span></div>
                    <div class="h-1.5 bg-slate-800 rounded-full"><div class="h-1.5 bg-amber-500 rounded-full" style="width:${{pct}}%"></div></div>
                </div>
                <div class="text-xl font-semibold mb-6">${{q.q}}</div>
                <div class="space-y-3" id="quiz-options">${{q.options.map((o,i) => `<button onclick="answer(${{i}})" class="quiz-option w-full text-left px-5 py-3.5 border border-slate-700 hover:border-amber-600 rounded-2xl flex gap-3"><span class="w-6 h-6 rounded-full border border-slate-600 flex items-center justify-center text-xs">${{String.fromCharCode(65+i)}}</span>${{o}}</button>`).join('')}}</div>`;
        }}
        function answer(i) {{
            const q = quizData[cq];
            const correct = i === q.answer;
            if (correct) score++;
            document.querySelectorAll('.quiz-option').forEach((btn, idx) => {{
                btn.disabled = true;
                if (idx === q.answer) btn.classList.add('!border-amber-500', 'bg-amber-900/30');
                else if (idx === i && !correct) btn.classList.add('!border-red-500', 'bg-red-900/20');
            }});
            setTimeout(() => {{ cq++; if (cq < quizData.length) showQ(); else showResults(); }}, 1200);
        }}
        function showResults() {{
            document.getElementById('quiz-questions').classList.add('hidden');
            document.getElementById('quiz-results').classList.remove('hidden');
            const pct = Math.round(score / quizData.length * 100);
            document.getElementById('quiz-score').innerHTML = pct + '<span class="text-3xl">%</span>';
            let fb = pct >= 90 ? 'Excellent! You are ready for production JFR incidents.' : pct >= 70 ? 'Strong foundation. Review war stories and Kubernetes module.' : pct >= 50 ? 'Review Modules 4–11 and practice jcmd commands.' : 'Start with Modules 1–6 and the cheat sheet.';
            document.getElementById('quiz-feedback').textContent = fb;
        }}
        function restartQuiz() {{
            document.getElementById('quiz-results').classList.add('hidden');
            document.getElementById('quiz-start').classList.remove('hidden');
        }}
    </script>
</body>
</html>'''

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(page, encoding="utf-8")
    line_count = len(page.splitlines())
    print(f"Wrote {OUT_PATH} ({line_count} lines)")


if __name__ == "__main__":
    main()