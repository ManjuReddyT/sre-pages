#!/usr/bin/env python3
from pathlib import Path
import html, re

ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    ("high-cpu", "High CPU", "Kubernetes · Java", "Sustained or sudden CPU, HPA thrash, throttling, and hot threads."),
    ("high-memory", "High memory", "Kubernetes · Java", "OOMKills, heap vs native pressure, and what to capture before a dump."),
    ("high-error-rate", "High error rate", "Kubernetes · Java", "4xx/5xx spikes, bad rollouts, missing endpoints, and failed dependencies."),
    ("latency", "High latency", "Kubernetes · Java", "p95/p99 regressions, pool waits, GC pauses, and slow dependencies."),
]

CSS = """
    :root { --bg:#f4f6fb; --card:#fff; --line:#e2e8f0; --text:#0f172a; --muted:#64748b; --accent:#5b5ce6; --navy:#1e1b4b; }
    [data-theme="dark"] { --bg:#0f1220; --card:#171a2b; --line:#2a3048; --text:#e8eaf4; --muted:#94a3b8; --accent:#818cf8; --navy:#e8eaf4; }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--bg); color:var(--text); font-family:"IBM Plex Sans",system-ui,sans-serif; }
    a { color:inherit; text-decoration:none; }
    header { background:var(--card); border-bottom:1px solid var(--line); }
    .bar { max-width:1040px; margin:0 auto; padding:0 24px; height:60px; display:flex; align-items:center; justify-content:space-between; }
    .brand { display:flex; align-items:center; gap:10px; font-weight:700; }
    .brand img { width:28px; height:28px; }
    .word i { color:var(--accent); font-style:normal; }
    nav { display:flex; gap:20px; font-size:14px; color:var(--muted); }
    nav a:hover, nav a.active { color:var(--accent); }
    .icon-btn { width:36px; height:36px; border-radius:10px; border:1px solid var(--line); background:var(--card); cursor:pointer; color:var(--text); }
    main { max-width:760px; margin:0 auto; padding:48px 24px 80px; }
    .crumb { color:var(--muted); font-size:13px; margin:0 0 16px; }
    .crumb a { color:var(--accent); }
    h1 { margin:0 0 6px; font-size:clamp(28px,4vw,40px); letter-spacing:-.03em; color:var(--navy); }
    .meta { color:var(--muted); margin:0 0 28px; }
    article h2 { margin:28px 0 10px; font-size:20px; }
    article h3 { margin:18px 0 8px; font-size:16px; }
    article p, article li { line-height:1.65; }
    article ul, article ol { margin:0 0 14px; padding-left:20px; color:var(--muted); }
    article li { margin:0 0 6px; }
    article p { margin:0 0 12px; color:var(--muted); }
    code { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.9em; background:color-mix(in srgb,var(--accent) 8%, transparent); padding:1px 5px; border-radius:4px; }
    pre { background:#0f172a; color:#e2e8f0; padding:14px 16px; border-radius:12px; overflow-x:auto; font-size:13px; line-height:1.5; }
    pre code { background:none; color:inherit; padding:0; }
    [data-theme="dark"] pre { background:#0b0e18; border:1px solid var(--line); }
    @media (max-width:800px) { nav { display:none; } main { padding:28px 16px 56px; } }
"""

SCRIPT = """
    const root = document.documentElement;
    if (localStorage.getItem('theme') === 'dark') root.setAttribute('data-theme','dark');
    document.getElementById('theme').onclick = () => {
      const dark = root.getAttribute('data-theme') === 'dark';
      if (dark) { root.removeAttribute('data-theme'); localStorage.setItem('theme','light'); }
      else { root.setAttribute('data-theme','dark'); localStorage.setItem('theme','dark'); }
    };
"""


def inline(text):
    text = html.escape(text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def md_to_html(text):
    lines = text.splitlines()
    if lines and lines[0].startswith('# '):
        lines = lines[1:]
    parts, i, in_code, buf, in_ul, in_ol = [], 0, False, [], False, False
    def close():
        nonlocal in_ul, in_ol
        if in_ul:
            parts.append('</ul>'); in_ul = False
        if in_ol:
            parts.append('</ol>'); in_ol = False
    while i < len(lines):
        line = lines[i]
        if line.startswith('```'):
            if not in_code:
                close(); in_code = True; buf = []
            else:
                parts.append('<pre><code>' + html.escape('\n'.join(buf)) + '</code></pre>')
                in_code = False
            i += 1; continue
        if in_code:
            buf.append(line); i += 1; continue
        if not line.strip():
            close(); i += 1; continue
        if line.startswith('### '):
            close(); parts.append('<h3>' + html.escape(line[4:]) + '</h3>')
        elif line.startswith('## '):
            close(); parts.append('<h2>' + html.escape(line[3:]) + '</h2>')
        elif re.match(r'^\d+\. ', line):
            if in_ul:
                parts.append('</ul>'); in_ul = False
            if not in_ol:
                parts.append('<ol>'); in_ol = True
            parts.append('<li>' + inline(re.sub(r'^\d+\. ', '', line)) + '</li>')
        elif line.startswith('- '):
            if in_ol:
                parts.append('</ol>'); in_ol = False
            if not in_ul:
                parts.append('<ul>'); in_ul = True
            parts.append('<li>' + inline(line[2:]) + '</li>')
        else:
            close(); parts.append('<p>' + inline(line) + '</p>')
        i += 1
    close()
    return '\n'.join(parts)


def page(title, inner):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)} · sreroot</title>
  <link rel="icon" href="../favicon.svg" type="image/svg+xml" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>{CSS}</style>
</head>
<body>
  <header>
    <div class="bar">
      <a class="brand" href="/"><img src="../assets/favicon.svg" alt="" /><span class="word">sre<i>root</i></span></a>
      <nav>
        <a href="/">Home</a>
        <a href="../guides.html">Guides</a>
        <a class="active" href="../runbooks.html">Runbooks</a>
        <a href="../about.html">About</a>
      </nav>
      <button class="icon-btn" id="theme" aria-label="Toggle theme">☼</button>
    </div>
  </header>
  <main>
{inner}
  </main>
  <script>{SCRIPT}</script>
</body>
</html>
"""


def main():
    for slug, title, subtitle, _blurb in DOCS:
        md = (ROOT / 'runbooks' / f'{slug}.md').read_text(encoding='utf-8')
        inner = f'    <p class="crumb"><a href="../runbooks.html">Runbooks</a> / {html.escape(title)}</p>\n    <h1>{html.escape(title)}</h1>\n    <p class="meta">{html.escape(subtitle)} · incident notes</p>\n    <article>\n{md_to_html(md)}\n    </article>'
        dest = ROOT / 'runbooks' / f'{slug}.html'
        dest.write_text(page(title + ' runbook', inner), encoding='utf-8')
        print('wrote', dest.relative_to(ROOT))


if __name__ == '__main__':
    main()
