#!/usr/bin/env python3
"""Shared HTML course page builder for SRE Pages Academy."""

import html
import json
from typing import Any, Dict, List, Tuple


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def render_sections(sections: List[Dict[str, Any]], code_class: str) -> str:
    parts = []
    for s in sections:
        t = s["type"]
        if t == "p":
            parts.append(f'<p class="text-slate-300 mb-4">{s["html"]}</p>')
        elif t == "h3":
            parts.append(f'<h3 class="text-xl font-semibold mt-6 mb-3 text-slate-100">{s["html"]}</h3>')
        elif t == "h4":
            parts.append(f'<h4 class="font-semibold {s.get("color", "text-accent")} mt-6 mb-3">{s["html"]}</h4>')
        elif t == "ul":
            items = "".join(f'<li class="mb-1">{i}</li>' for i in s["items"])
            parts.append(f'<ul class="list-disc pl-5 mb-4 text-slate-300">{items}</ul>')
        elif t == "ol":
            items = "".join(f'<li class="mb-1">{i}</li>' for i in s["items"])
            parts.append(f'<ol class="list-decimal pl-5 mb-4 text-slate-300 space-y-1">{items}</ol>')
        elif t == "code":
            parts.append(f'<div class="my-4"><div class="code-header">{esc(s.get("label", "terminal"))}</div><pre class="{code_class}">{esc(s["text"])}</pre></div>')
        elif t == "insight":
            parts.append(f'''<div class="bg-slate-950 border border-slate-700 p-5 rounded-2xl my-6 text-sm">
                <div class="font-semibold mb-2 text-accent">{s["title"]}</div>
                <p class="text-slate-300">{s["html"]}</p></div>''')
        elif t == "tip":
            parts.append(f'''<div class="mt-6 p-4 bg-accent-muted border border-accent-border rounded-2xl text-sm">
                <div class="text-xs uppercase tracking-widest text-accent mb-1">SRE TIP</div>
                <p class="text-slate-300">{s["html"]}</p></div>''')
        elif t == "cards":
            cards = "".join(
                f'<div class="p-4 bg-slate-950 rounded-2xl border border-slate-800">'
                f'<span class="font-mono text-sm {c["color"]}">{c["label"]}</span><br>'
                f'<span class="text-xs text-slate-400 mt-1 block">{c["desc"]}</span></div>'
                for c in s["cards"]
            )
            cols = s.get("cols", 2)
            parts.append(f'<div class="mt-4 grid grid-cols-1 md:grid-cols-{cols} gap-4 text-sm">{cards}</div>')
        elif t == "table":
            hdr = "".join(f'<th class="text-left py-3 px-4 font-semibold">{h}</th>' for h in s["headers"])
            rows = ""
            for row in s["rows"]:
                rows += "<tr>" + "".join(f'<td class="py-3 px-4">{c}</td>' for c in row) + "</tr>"
            parts.append(f'''<div class="my-6 overflow-x-auto"><table class="w-full text-sm">
                <thead><tr class="border-b border-slate-700">{hdr}</tr></thead>
                <tbody class="divide-y divide-slate-700 text-slate-300">{rows}</tbody></table></div>''')
        elif t == "pills":
            pills = "".join(f'<span class="text-xs px-3 py-1 bg-slate-800 rounded-full">{p}</span>' for p in s["items"])
            parts.append(f'<div class="flex flex-wrap gap-2 my-4">{pills}</div>')
        elif t == "war":
            parts.append(f'''<div class="mb-6 p-6 bg-slate-950 border border-slate-700 rounded-2xl">
                <div class="flex flex-wrap items-center gap-3 mb-3">
                    <h4 class="font-semibold text-lg">{esc(s["title"])}</h4>
                    <span class="text-xs px-2 py-0.5 bg-slate-800 {s.get("sev_color","text-amber-400")} rounded">{esc(s["sev"])}</span>
                </div>
                <p class="text-sm text-slate-400 mb-2"><strong>Impact:</strong> {s["impact"]}</p>
                <p class="text-sm text-slate-300 mb-2"><span class="text-accent font-medium">Symptoms:</span> {s["symptoms"]}</p>
                <p class="text-sm text-slate-300 mb-2"><span class="text-accent font-medium">Dump evidence:</span> {s["evidence"]}</p>
                <p class="text-sm text-slate-300 mb-2"><span class="text-red-400 font-medium">Root cause:</span> {s["root"]}</p>
                <p class="text-sm text-slate-300 mb-2"><span class="text-emerald-400 font-medium">Resolution:</span> {s["fix"]}</p>
                <p class="text-xs text-slate-500 mt-3 italic">Lesson: {s["lesson"]}</p></div>''')
    return "\n".join(parts)


def render_cheat_body(content: str, code_class: str) -> str:
    if "\n" in content or content.startswith("j"):
        return f'<pre class="{code_class} rounded-2xl">{esc(content)}</pre>'
    items = "".join(f"<li>{esc(line)}</li>" for line in content.split("|"))
    return f'<ul class="text-sm text-slate-300 space-y-2">{items}</ul>'


def render_course(cfg: Dict[str, Any]) -> str:
    accent = cfg["accent"]
    accent_hover = cfg["accent_hover"]
    accent_muted = cfg.get("accent_muted", "bg-accent-muted")
    badge_bg = cfg["badge_bg"]
    badge_text = cfg["badge_text"]
    code_class = cfg["code_class"]
    icon = cfg["icon"]
    brand = cfg["brand"]
    course_num = cfg["course_num"]
    course_label = cfg["course_label"]
    title_html = cfg["title_html"]
    subtitle = cfg["subtitle"]
    hero_checks = cfg["hero_checks"]
    stats = cfg["stats"]
    why_cards = cfg["why_cards"]
    modules = cfg["modules"]
    labs = cfg["labs"]
    quiz = cfg["quiz"]
    interview = cfg["interview"]
    flowcharts = cfg["flowcharts"]
    cheatsheet = cfg["cheatsheet"]
    lab_sims_js = cfg.get("lab_sims_js", "{}")

    curriculum_cards = []
    for i, m in enumerate(modules, 1):
        curriculum_cards.append(f'''
            <div onclick="document.getElementById('module-{i}').scrollIntoView({{behavior:'smooth'}})" class="module-card cursor-pointer bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-3xl p-5 group">
                <span class="course-badge">Module {i}</span>
                <h4 class="font-semibold mt-3 text-lg group-hover:text-accent transition">{esc(m["title"])}</h4>
                <p class="text-xs text-slate-500 mt-2 line-clamp-2">{esc(m["summary"])}</p>
            </div>''')

    module_sections = []
    for i, m in enumerate(modules, 1):
        body = render_sections(m["sections"], code_class)
        module_sections.append(f'''
            <div id="module-{i}" class="module-section mb-16 bg-slate-900 border border-slate-700 rounded-3xl p-8">
                <div class="flex items-center gap-x-4 mb-6">
                    <span class="px-4 py-1.5 text-sm font-bold {badge_bg} {badge_text} rounded-2xl">MODULE {i}</span>
                    <h3 class="text-3xl font-bold tracking-tight">{esc(m["title"])}</h3>
                </div>
                <div class="lesson-content">{body}</div>
            </div>''')

    lab_html = []
    for i, (ltitle, ldesc) in enumerate(labs, 1):
        sim = ""
        if i <= 3:
            sim = f'<button onclick="simulateLab({i})" class="self-start px-5 py-2 text-sm font-medium bg-{accent}-600 hover:bg-{accent_hover} rounded-2xl flex items-center gap-x-2"><i class="fa-solid fa-play"></i><span>Simulate</span></button>'
        lab_html.append(f'''
            <div class="border border-slate-700 bg-slate-900 rounded-3xl p-6">
                <div class="flex justify-between gap-4">
                    <div>
                        <span class="font-mono text-xs {badge_bg} {badge_text} px-2.5 py-px rounded">LAB {i}</span>
                        <h4 class="font-semibold text-xl mt-2">{esc(ltitle)}</h4>
                        <p class="text-sm text-slate-400 mt-1">{esc(ldesc)}</p>
                    </div>{sim}
                </div>
            </div>''')

    interview_html = "".join(f'''
        <div class="p-5 bg-slate-950 border border-slate-700 rounded-2xl">
            <div class="text-accent text-xs font-mono mb-2">Q{j}</div>
            <p class="font-medium mb-2">{esc(q)}</p>
            <p class="text-sm text-slate-400">{esc(a)}</p>
        </div>''' for j, (q, a) in enumerate(interview, 1))

    flow_html = "".join(f'''
        <div class="p-5 bg-slate-900 border border-slate-700 rounded-2xl">
            <h4 class="font-semibold text-accent mb-3">{esc(ft)}</h4>
            <p class="text-sm text-slate-300">{" → ".join(esc(s) for s in steps)}</p>
        </div>''' for ft, steps in flowcharts)

    cheat_html = "".join(f'''
        <div class="bg-slate-900 border border-slate-700 rounded-3xl p-6">
            <h4 class="font-semibold text-accent mb-4">{esc(ct)}</h4>
            {render_cheat_body(content, code_class)}
        </div>''' for ct, content in cheatsheet)

    hero_check_html = "".join(f'<div class="flex gap-2"><i class="fa-solid fa-check text-accent"></i><span>{c}</span></div>' for c in hero_checks)
    stats_html = "".join(f'<div><div class="text-3xl font-bold text-accent">{v}</div><div class="text-xs text-slate-500 mt-1">{l}</div></div>' for v, l in stats)
    why_html = "".join(f'''<div class="bg-slate-900 border border-slate-800 rounded-3xl p-6">
        <i class="fa-solid {ic} text-accent text-2xl mb-3"></i>
        <h3 class="font-semibold text-lg mb-2">{t}</h3><p class="text-sm text-slate-400">{d}</p></div>''' for ic, t, d in why_cards)

    quiz_json = json.dumps([{"q": q, "options": o, "answer": a, "explanation": e} for q, o, a, e in quiz])

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(cfg["page_title"])}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Space+Grotesk:wght@500;600&display=swap');
        :root {{ --accent: {cfg["accent_hex"]}; }}
        body {{ font-family: 'Inter', system-ui, sans-serif; }}
        .font-display {{ font-family: 'Space Grotesk', 'Inter', sans-serif; font-weight: 600; }}
        .section-header {{ font-size: 2.25rem; line-height: 2.5rem; font-weight: 700; letter-spacing: -0.025em; }}
        .module-card {{ transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }}
        .module-card:hover {{ transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1); }}
        .text-accent {{ color: {cfg["accent_hex"]}; }}
        .text-accent-muted, .bg-accent-muted {{ }}
        .course-badge {{ background: {cfg["badge_bg_hex"]}; color: {cfg["badge_text_hex"]}; font-size: 0.75rem; padding: 0.125rem 0.5rem; border-radius: 9999px; font-weight: 500; }}
        .{code_class} {{ background: #020617; color: #e0e7ff; padding: 1rem; border-radius: 0 0 0.5rem 0.5rem; overflow-x: auto; font-size: 0.875rem; border: 1px solid #334155; white-space: pre-wrap; font-family: ui-monospace, Consolas, monospace; }}
        .code-header {{ background: #1e2937; padding: 0.5rem 1rem; border-radius: 0.5rem 0.5rem 0 0; font-size: 0.75rem; color: #64748b; }}
        .dump-code, .thread-code {{ background: #0f172a; padding: 2px 6px; border-radius: 4px; font-size: 0.875rem; font-family: ui-monospace, Consolas, monospace; }}
        .module-section {{ scroll-margin-top: 80px; }}
        .nav-link:hover {{ color: {cfg["accent_hex"]}; }}
        .bg-accent-muted {{ background: {cfg.get("accent_muted_hex", "rgba(0,0,0,0.2)")}; }}
        .border-accent-border {{ border-color: {cfg.get("accent_border_hex", "#334155")}; }}
    </style>
</head>
<body class="bg-slate-950 text-slate-200">
    <nav class="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
        <div class="max-w-screen-2xl mx-auto px-8 py-4 flex items-center justify-between">
            <a href="../../index.html" class="flex items-center gap-3">
                <div class="w-10 h-10 bg-{accent}-600 rounded-xl flex items-center justify-center"><i class="{icon} text-white text-2xl"></i></div>
                <span class="font-display text-2xl font-semibold">{brand}</span>
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
                <div class="inline-flex items-center gap-2 px-3 py-1 bg-slate-800 text-accent rounded-full text-xs font-medium mb-6">
                    <i class="fa-solid fa-shield-halved"></i> {course_label}
                </div>
                <h1 class="text-5xl md:text-6xl font-display font-bold tracking-tight mb-4">{title_html}</h1>
                <p class="text-xl text-slate-400 mb-8 max-w-lg">{subtitle}</p>
                <div class="flex flex-wrap gap-4">
                    <button onclick="startCourse()" class="px-8 py-3.5 bg-{accent}-600 hover:bg-{accent_hover} text-white font-semibold rounded-3xl flex items-center gap-2"><i class="fa-solid fa-play"></i> Start Learning</button>
                    <button onclick="document.getElementById('curriculum').scrollIntoView({{behavior:'smooth'}})" class="px-6 py-3.5 border border-slate-700 rounded-3xl">Browse Curriculum</button>
                </div>
            </div>
            <div class="md:col-span-5">
                <div class="bg-slate-900 border border-slate-800 rounded-3xl p-8">
                    <div class="grid grid-cols-3 gap-4 text-center mb-6">{stats_html}</div>
                    <div class="border-t border-slate-800 pt-4 space-y-3 text-sm">{hero_check_html}</div>
                </div>
            </div>
        </div>
    </div>

    <div class="max-w-screen-2xl mx-auto px-8 py-12 border-t border-slate-800">
        <h2 class="section-header mb-8">When you need a snapshot of JVM state</h2>
        <div class="grid md:grid-cols-3 gap-6">{why_html}</div>
    </div>

    <div id="curriculum" class="max-w-screen-2xl mx-auto px-8 py-16 border-t border-slate-800">
        <span class="text-accent text-sm font-semibold">{len(modules)} MODULES</span>
        <h2 class="section-header mt-2 mb-8">Complete Curriculum</h2>
        <div class="relative hidden md:block mb-6 w-64">
            <input type="text" id="search-input" placeholder="Search modules..." class="w-full bg-slate-900 border border-slate-700 rounded-2xl py-2.5 pl-10 pr-4 text-sm focus:outline-none">
            <i class="fa-solid fa-search absolute left-4 top-3 text-slate-500"></i>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">{"".join(curriculum_cards)}</div>
    </div>

    <div id="modules-detail" class="max-w-screen-2xl mx-auto px-8 py-12 border-t border-slate-800 bg-slate-900/30">
        <div class="max-w-4xl mx-auto">
            <h2 class="text-3xl font-bold mb-2">Detailed Module Content</h2>
            <p class="text-slate-400 mb-10">Production SRE playbooks, examples, and incident patterns</p>
            {"".join(module_sections)}
        </div>
    </div>

    <div id="labs" class="max-w-screen-2xl mx-auto px-8 py-16 border-t border-slate-800">
        <span class="text-accent font-semibold text-sm">PRACTICAL EXPERIENCE</span>
        <h2 class="section-header mt-2 mb-8">Hands-on Labs</h2>
        <div class="max-w-4xl mx-auto space-y-4">{"".join(lab_html)}</div>
    </div>

    <div id="quiz" class="max-w-screen-2xl mx-auto px-8 py-16 border-t border-slate-800 bg-slate-900">
        <div class="max-w-3xl mx-auto text-center">
            <span class="text-accent font-semibold">TEST YOUR KNOWLEDGE</span>
            <h2 class="section-header mt-2 mb-8">Interactive Quiz</h2>
            <div id="quiz-container" class="bg-slate-950 border border-slate-700 rounded-3xl p-8">
                <div id="quiz-start">
                    <i class="fa-solid fa-question-circle text-6xl text-accent mb-6"></i>
                    <p class="text-slate-400 mb-8">10 questions · Instant feedback</p>
                    <button onclick="startQuiz()" class="px-10 py-3.5 bg-{accent}-600 hover:bg-{accent_hover} text-white font-semibold rounded-3xl text-lg">Start Quiz</button>
                </div>
                <div id="quiz-questions" class="hidden text-left"></div>
                <div id="quiz-results" class="hidden py-6">
                    <div id="quiz-score" class="text-6xl font-bold text-accent mb-2"></div>
                    <p id="quiz-feedback" class="max-w-md mx-auto text-slate-300 mb-8"></p>
                    <button onclick="restartQuiz()" class="px-8 py-2.5 border border-slate-600 rounded-2xl text-sm">Try Again</button>
                </div>
            </div>
        </div>
    </div>

    <div id="interview" class="max-w-screen-2xl mx-auto px-8 py-16 border-t border-slate-800">
        <span class="text-accent font-semibold text-sm">INTERVIEW PREP</span>
        <h2 class="section-header mt-2 mb-8">Common Interview Questions</h2>
        <div class="max-w-3xl mx-auto grid gap-4">{interview_html}</div>
    </div>

    <div id="flowcharts" class="max-w-screen-2xl mx-auto px-8 py-16 border-t border-slate-800 bg-slate-900/30">
        <span class="text-accent font-semibold text-sm">TROUBLESHOOTING</span>
        <h2 class="section-header mt-2 mb-8">Investigation Flowcharts</h2>
        <div class="max-w-4xl mx-auto grid md:grid-cols-2 gap-4">{flow_html}</div>
    </div>

    <div id="cheatsheet" class="max-w-screen-2xl mx-auto px-8 py-16 border-t border-slate-800">
        <h2 class="section-header mb-8">Production Cheat Sheet</h2>
        <div class="grid lg:grid-cols-2 gap-6 max-w-5xl">{cheat_html}</div>
    </div>

    <footer class="border-t border-slate-800 bg-slate-900 py-12">
        <div class="max-w-screen-2xl mx-auto px-8 text-sm text-slate-500 flex flex-col md:flex-row justify-between gap-4">
            <span>© 2026 {esc(cfg["footer_name"])}</span>
            <div class="flex flex-wrap gap-5">
                <a href="../../index.html" class="hover:text-slate-300">SRE Academy</a>
                <a href="../strace/index.html" class="hover:text-slate-300">strace</a>
                <a href="../jfr/index.html" class="hover:text-slate-300">JFR</a>
                <a href="../heapdump/index.html" class="hover:text-slate-300">Heap Dump</a>
                <a href="../threaddump/index.html" class="hover:text-slate-300">Thread Dump</a>
                <a href="https://github.com/ManjuReddyT/sre-pages" target="_blank" rel="noopener" class="hover:text-slate-300">GitHub</a>
            </div>
        </div>
    </footer>

    <script>
        const quizData = {quiz_json};
        const labSims = {lab_sims_js};

        function startCourse() {{
            document.getElementById('curriculum').scrollIntoView({{ behavior: 'smooth' }});
        }}
        function toggleMobileMenu() {{
            const m = document.createElement('div');
            m.className = 'md:hidden fixed inset-0 bg-slate-950/95 z-[60] p-8';
            m.innerHTML = '<button onclick="this.parentElement.remove()" class="text-3xl mb-8">×</button><div class="flex flex-col gap-4 text-xl"><a href="#curriculum">Curriculum</a><a href="#labs">Labs</a><a href="#quiz">Quiz</a><a href="#cheatsheet">Cheat Sheet</a><a href="../../index.html">Academy</a></div>';
            document.body.appendChild(m);
        }}
        function simulateLab(n) {{
            const lab = labSims[n];
            if (!lab) return;
            const modal = document.createElement('div');
            modal.className = 'fixed inset-0 bg-black/70 flex items-center justify-center z-[80] p-6';
            modal.innerHTML = `<div class="bg-slate-900 border border-slate-700 w-full max-w-2xl rounded-3xl overflow-hidden">
                <div class="px-6 py-4 border-b border-slate-700 flex justify-between bg-slate-950"><span class="font-semibold">${{lab.title}}</span>
                <button onclick="this.closest('.fixed').remove()" class="text-xl">×</button></div>
                <div class="p-6 text-sm"><pre class="{code_class} rounded-2xl mb-4 text-xs">${{lab.output}}</pre>
                <div class="bg-accent-muted border border-accent-border p-4 rounded-2xl text-xs"><strong class="text-accent">SRE insight:</strong> ${{lab.insight}}</div>
                <button onclick="this.closest('.fixed').remove()" class="mt-5 w-full py-2.5 bg-{accent}-600 rounded-2xl font-medium">Close</button></div></div>`;
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
                <div class="mb-6"><div class="flex justify-between text-xs mb-1.5"><span class="text-accent font-medium">Q ${{cq+1}} / ${{quizData.length}}</span><span>${{pct}}%</span></div>
                <div class="h-1.5 bg-slate-800 rounded-full"><div class="h-1.5 bg-{accent}-500 rounded-full" style="width:${{pct}}%"></div></div></div>
                <div class="text-xl font-semibold mb-6">${{q.q}}</div>
                <div class="space-y-3">${{q.options.map((o,i) => `<button onclick="answer(${{i}})" class="quiz-option w-full text-left px-5 py-3.5 border border-slate-700 hover:border-{accent}-600 rounded-2xl">${{String.fromCharCode(65+i)}}. ${{o}}</button>`).join('')}}</div>`;
        }}
        function answer(i) {{
            if (i === quizData[cq].answer) score++;
            document.querySelectorAll('.quiz-option').forEach((btn, idx) => {{
                btn.disabled = true;
                if (idx === quizData[cq].answer) btn.classList.add('!border-{accent}-500', 'bg-{accent}-900/30');
            }});
            setTimeout(() => {{ cq++; if (cq < quizData.length) showQ(); else {{
                document.getElementById('quiz-questions').classList.add('hidden');
                document.getElementById('quiz-results').classList.remove('hidden');
                const pct = Math.round(score/quizData.length*100);
                document.getElementById('quiz-score').innerHTML = pct + '<span class="text-3xl">%</span>';
                document.getElementById('quiz-feedback').textContent = pct >= 80 ? 'Excellent — production-ready!' : pct >= 60 ? 'Good foundation — review war stories.' : 'Review modules 1–6 and cheat sheet.';
            }}; }}, 1100);
        }}
        function restartQuiz() {{
            document.getElementById('quiz-results').classList.add('hidden');
            document.getElementById('quiz-start').classList.remove('hidden');
        }}
    </script>
</body>
</html>'''