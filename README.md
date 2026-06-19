# SRE Pages Academy

Hands-on SRE training courses hosted on GitHub Pages.

**Live site:** [manjureddyt.github.io/sre-pages](https://manjureddyt.github.io/sre-pages/)

## Courses

### Course 1 — Master Linux System Call Tracing (strace)

A production-focused strace course for SREs and platform engineers:

- 14 detailed modules (ptrace, syscalls, Kubernetes, Java, futex, war stories)
- Hands-on lab simulations
- Interactive 10-question quiz
- Production cheat sheet

Source: `index.html`

## Local preview

```bash
cd sre-pages
python -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000).

## Deploy

Push to `main` — GitHub Pages serves `index.html` from the repo root.