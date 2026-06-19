# SRE Pages Academy

Hands-on SRE training courses hosted on GitHub Pages.

**Live site:** [manjureddyt.github.io/sre-pages](https://manjureddyt.github.io/sre-pages/)

## Courses

| # | Course | Path | Topics |
|---|--------|------|--------|
| 1 | **strace Academy** | [courses/strace/](courses/strace/index.html) | Linux syscall tracing, Kubernetes, futex, war stories |
| 2 | **Java Flight Recorder (JFR)** | [courses/jfr/](courses/jfr/index.html) | JVM profiling, GC, memory leaks, Spring Boot, Kafka |

## Source content

- JFR course markdown: [content/sre-jfr-training-course.md](content/sre-jfr-training-course.md)
- JFR HTML generator: `python scripts/build_jfr_course.py`

## Local preview

```bash
cd sre-pages
python -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000) for the academy hub.

## Deploy

Push to `main` — GitHub Pages serves from the repo root.