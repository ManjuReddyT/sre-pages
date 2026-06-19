# SRE Training Course on Java Flight Recorder (JFR)

**Master JVM Observability for Production Reliability**

---

## Table of Contents

1. [Module 1: Introduction to JFR](#module-1-introduction-to-jfr)
2. [Module 2: Why Every SRE Should Learn JFR](#module-2-why-every-sre-should-learn-jfr)
3. [Module 3: JVM Internals Required for JFR](#module-3-jvm-internals-required-for-jfr)
4. [Module 4: Capturing JFR Recordings](#module-4-capturing-jfr-recordings)
5. [Module 5: Understanding JFR Events](#module-5-understanding-jfr-events)
6. [Module 6: Using Java Mission Control (JMC)](#module-6-using-java-mission-control-jmc)
7. [Module 7: CPU Troubleshooting with JFR](#module-7-cpu-troubleshooting-with-jfr)
8. [Module 8: Memory Leak Analysis](#module-8-memory-leak-analysis)
9. [Module 9: Garbage Collection Analysis](#module-9-garbage-collection-analysis)
10. [Module 10: Thread Analysis](#module-10-thread-analysis)
11. [Module 11: Lock Contention Analysis](#module-11-lock-contention-analysis)
12. [Module 12: Database Troubleshooting](#module-12-database-troubleshooting)
13. [Module 13: API Latency Investigation](#module-13-api-latency-investigation)
14. [Module 14: Exception Analysis](#module-14-exception-analysis)
15. [Module 15: Kubernetes and JFR](#module-15-kubernetes-and-jfr)
16. [Module 16: JFR and Spring Boot](#module-16-jfr-and-spring-boot)
17. [Module 17: Kafka Troubleshooting with JFR](#module-17-kafka-troubleshooting-with-jfr)
18. [Module 18: SRE Incident War Stories](#module-18-sre-incident-war-stories)
19. [Module 19: JFR vs Other Tools](#module-19-jfr-vs-other-tools)
20. [Module 20: SRE Production Playbook](#module-20-sre-production-playbook)
21. [Bonus Module: JVM Tuning Using JFR](#bonus-module-jvm-tuning-using-jfr)
22. [Bonus Module: Continuous Profiling with JFR](#bonus-module-continuous-profiling-with-jfr)
23. [Bonus Module: AI-Assisted JFR Analysis](#bonus-module-ai-assisted-jfr-analysis)
24. [Hands-on Labs](#hands-on-labs)
25. [Interview Questions](#interview-questions)
26. [JFR Production Cheat Sheet](#jfr-production-cheat-sheet)
27. [Troubleshooting Flowcharts](#troubleshooting-flowcharts)

---

# Module 1: Introduction to JFR

## What is JFR?

**Java Flight Recorder (JFR)** is a low-overhead, production-grade profiling and diagnostics tool built into the JVM. It continuously records detailed events about the JVM's internal behavior — CPU usage, memory allocations, garbage collection, thread activity, locks, I/O, exceptions, and more — with **minimal performance impact** (typically < 1% overhead).

JFR was originally developed by Oracle for JRockit and later integrated into HotSpot/OpenJDK. It is now a standard part of the JDK.

## Why Oracle Created It

Traditional profiling tools (VisualVM, JProfiler, YourKit) often introduce high overhead, making them unsuitable for production. JFR was designed from the ground up for **always-on, low-overhead observability** in mission-critical systems.

## History & Evolution

- **JRockit Mission Control** (original commercial tool)
- 2018: Open-sourced and integrated into OpenJDK 11+
- Today: Available in all modern JDKs (OpenJDK, Oracle JDK, Amazon Corretto, Azul Zulu, etc.)

## JFR vs Related Tools

| Tool          | Layer          | Overhead     | Production Safe | Best For                     |
|---------------|----------------|--------------|-----------------|------------------------------|
| **JFR**       | JVM            | Very Low     | Yes             | Production profiling & diagnostics |
| **JMC**       | Analysis UI    | N/A          | N/A             | Analyzing JFR recordings     |
| **jstack**    | Thread dumps   | Low          | Yes (short)     | Quick thread state snapshots |
| **jcmd**      | JVM commands   | Low          | Yes             | Starting/stopping JFR        |
| **async-profiler** | Native + JVM | Low-Medium | Yes             | Flame graphs & CPU profiling |
| **VisualVM**  | GUI            | Medium       | Limited         | Development & light profiling |
| **JConsole**  | JMX            | Low          | Yes             | Basic monitoring             |

## JFR Architecture

```
Application Code
      ↓
JVM (HotSpot)
      ↓
JFR Event Producers
   (GC, JIT, Threads, Memory, Locks, I/O, etc.)
      ↓
JFR Recording Engine (Ring Buffer)
      ↓
.jfr File (Binary Recording)
      ↓
JMC / JDK Mission Control / Custom Tools
      ↓
Analysis & Visualization
```

JFR works by instrumenting the JVM internally at key points and emitting structured **events** that are written to a highly efficient ring buffer.

---

# Module 2: Why Every SRE Should Learn JFR

Metrics tell you **WHAT** is happening.  
Logs tell you **WHEN** something happened.  
**JFR tells you WHY** — at the exact moment the problem occurred inside the JVM.

## Common Production Incidents Where JFR Shines

| Incident                    | What Metrics/Logs Show          | What JFR Reveals                              |
|----------------------------|---------------------------------|-----------------------------------------------|
| Slow API / High Latency    | P95/P99 high                    | Which methods, locks, DB calls, or GC pauses are causing it |
| CPU Spike                  | CPU at 90-100%                  | Hot methods, JIT compilation storms, infinite loops |
| GC Pauses / Latency Spikes | GC time increasing              | Allocation rate, promotion failures, humongous objects |
| Memory Leak / OOMKill      | Heap usage growing              | Allocation hotspots, leaking objects, ThreadLocal leaks |
| Thread Pool Starvation     | Threads blocked / queue growing | Which threads are blocked on what locks |
| Database Latency           | DB response time high           | JDBC calls, connection acquisition time, query execution |
| Kafka Consumer Lag         | Lag increasing                  | Deserialization time, processing time per record |
| Connection Pool Exhaustion | Timeouts on DB calls            | Connection acquisition latency & contention |

**Key Insight**: JFR gives you **ground truth** from inside the JVM during the exact time window of the incident.

---

# Module 3: JVM Internals Required for JFR

To effectively use JFR, SREs must understand these core JVM components:

## Key Areas

- **Heap Memory**: Young (Eden, Survivor) + Old Generation
- **Metaspace**: Class metadata (replaced PermGen)
- **Thread Stacks**: Per-thread call stacks
- **Garbage Collectors**: G1GC, ZGC, Shenandoah, Parallel, Serial
- **Safepoints**: Global JVM pauses for certain operations
- **JIT Compiler**: C1/C2 compilation of hot methods
- **Class Loading**: ClassLoader hierarchy and loading time
- **TLAB / PLAB**: Thread-Local Allocation Buffers (critical for allocation performance)

JFR can observe and record events from **all** of these components with very low overhead because the instrumentation is built directly into the JVM.

---

# Module 4: Capturing JFR Recordings

## Using jcmd (Recommended for Running Processes)

```bash
# Start a recording
jcmd <PID> JFR.start name=MyAppRecording duration=300s filename=/tmp/app.jfr

# Dump current buffer (without stopping)
jcmd <PID> JFR.dump filename=/tmp/emergency.jfr

# Stop recording
jcmd <PID> JFR.stop name=MyAppRecording
```

## Startup Recording (via JVM Flags)

```bash
java -XX:StartFlightRecording=filename=/tmp/app.jfr,dumponexit=true,settings=profile \
     -jar myapp.jar
```

**Production-safe settings**:
- Use `settings=default` or `settings=profile` (profile has slightly higher detail)
- Limit duration or use ring buffer (`maxage`, `maxsize`)
- Avoid `dumponexit=true` in very long-running services unless needed

## Emergency Capture During Incidents

When an application is slow or about to OOM:

```bash
jcmd <PID> JFR.start name=Emergency duration=60s filename=/tmp/emergency.jfr
# Wait 30-60 seconds then
jcmd <PID> JFR.dump filename=/tmp/emergency.jfr
```

---

# Module 5: Understanding JFR Events

JFR records **hundreds of event types**. Key categories:

### CPU & Compilation
- `jdk.CPULoad`
- `jdk.ExecutionSample`
- `jdk.Compilation`

### Memory & Allocation
- `jdk.ObjectAllocationInNewTLAB`
- `jdk.ObjectAllocationOutsideTLAB`
- `jdk.JavaMonitorEnter`

### GC Events
- `jdk.GarbageCollection`
- `jdk.GCPhasePause`
- `jdk.PromotionFailed`

### Threads & Locking
- `jdk.ThreadStart`
- `jdk.ThreadPark`
- `jdk.JavaMonitorEnter`
- `jdk.ThreadSleep`

### I/O & Network
- `jdk.SocketRead`
- `jdk.SocketWrite`
- `jdk.FileRead`
- `jdk.FileWrite`

### Exceptions
- `jdk.ExceptionThrow`

For each event, JFR captures timestamp, thread, stack trace (when enabled), and event-specific fields.

---

# Module 6: Using Java Mission Control (JMC)

**Java Mission Control (JMC)** is the official (and best) tool for analyzing JFR recordings.

### Key Views in JMC

1. **Automated Analysis** — Rules engine highlights problems automatically
2. **Event Browser** — Filter and search all events
3. **Threads** — Thread states over time + stack traces
4. **Memory** — Heap usage, allocations, GC pauses
5. **Method Profiling** / Flame Graphs — Hot methods
6. **Lock Instances** — Contended monitors

**Pro Tip**: Always start with the **Automated Analysis** page — it often points directly to the root cause.

---

# Module 7: CPU Troubleshooting with JFR

**Scenario**: CPU at 90%+, response time increasing.

### Investigation Workflow

1. Capture JFR during the spike
2. Open in JMC → **Method Profiling** or **Flame Graph**
3. Look for:
   - Methods consuming > 5-10% of CPU
   - Excessive JIT compilation (`jdk.Compilation`)
   - Hot loops or expensive operations (JSON, regex, serialization)

**Common Culprits**:
- Infinite loops / busy waiting
- Excessive object creation + serialization
- Heavy regex or XML/JSON parsing
- Inefficient algorithms in hot paths

---

# Module 8: Memory Leak Analysis

JFR excels at finding leaks **before** OOMKill.

### Key Events
- `jdk.ObjectAllocationInNewTLAB`
- `jdk.ObjectAllocationOutsideTLAB`

### Investigation Steps in JMC
1. Go to **Memory** view
2. Look at **Allocation** tab
3. Identify classes with highest allocation rate
4. Check for growing collections, caches, or ThreadLocals

**Common Leaks**:
- Unbounded caches
- Growing `ConcurrentHashMap` or `ArrayList`
- Session objects not cleaned up
- `ThreadLocal` not removed after use

---

# Module 9: Garbage Collection Analysis

JFR provides deep visibility into GC behavior.

### What to Analyze
- GC pause times (`jdk.GCPhasePause`)
- Allocation rate vs promotion rate
- Humongous object allocations (G1)
- Full GC frequency
- Concurrent mark failures

### Modern GCs
- **G1GC** (default in JDK 9+)
- **ZGC** & **Shenandoah** (low-pause)
- **Parallel GC**

JFR helps you decide if you need to tune heap size, change GC, or fix allocation patterns.

---

# Module 10: Thread Analysis

JFR shows thread states over time:

- **Runnable**
- **Blocked** (waiting for monitor)
- **Waiting** (Object.wait / park)
- **Timed Waiting**

### Common Issues Found
- Deadlocks (multiple threads blocked on each other)
- Lock contention (many threads blocked on same monitor)
- Thread pool saturation (all threads blocked or waiting)
- Executor starvation

---

# Module 11: Lock Contention Analysis

Lock contention is one of the most common hidden causes of latency.

### Key JFR Events
- `jdk.JavaMonitorEnter`
- `jdk.ThreadPark`
- `jdk.LockInstances`

### Analysis in JMC
- **Lock Instances** view shows which locks are most contended
- Correlate with thread stacks to find the exact synchronized block or `ReentrantLock`

**Impact**: Even small contention on hot locks can destroy throughput under load.

---

# Module 12: Database Troubleshooting

JFR can show JDBC-level activity (with some configuration).

### What You Can See
- Time spent acquiring connections from pool
- Time spent in actual query execution (if using JDBC instrumentation)
- Connection pool exhaustion patterns

### Popular Pools
- HikariCP (recommended)
- C3P0, DBCP, Tomcat JDBC Pool

JFR helps distinguish between **pool acquisition latency** vs **actual database query slowness**.

---

# Module 13: API Latency Investigation

**Scenario**: P95 latency increased suddenly.

### End-to-End Workflow
1. Capture JFR during the degradation window
2. Analyze:
   - Thread pool utilization
   - Lock contention
   - Database / external call latency
   - Serialization / deserialization time
   - GC impact on request threads

JFR lets you build a complete picture of where time is being spent inside the JVM for slow requests.

---

# Module 14: Exception Analysis

Frequent exceptions can silently destroy performance.

### What JFR Shows
- `jdk.ExceptionThrow` events with full stack traces
- Frequency of specific exception types
- Hidden retry loops causing exception storms

**Examples**:
- `NullPointerException` in hot paths
- `SocketTimeoutException` / connection resets
- `SQLException` from connection issues

Business impact: Increased CPU, latency, and noisy logs.

---

# Module 15: Kubernetes and JFR (Critical for SREs)

### Capturing JFR from Pods

```bash
# Exec into pod
kubectl exec -it <pod> -- /bin/sh

# Start JFR
jcmd 1 JFR.start name=prod duration=120s filename=/tmp/app.jfr

# Copy recording out
kubectl cp <pod>:/tmp/app.jfr ./app.jfr
```

### Advanced Techniques
- **Ephemeral containers** (recommended for distroless)
- Sidecar containers with JFR tools
- Init containers or debug containers

### Kubernetes-Specific Issues JFR Helps Solve
- OOMKilled pods (memory leak vs heap sizing)
- CPU throttling vs actual JVM CPU usage
- Startup delays (class loading, JIT warm-up)
- HPA scaling problems caused by GC pauses
- Kafka consumer lag in containerized workloads

---

# Module 16: JFR and Spring Boot

### Common Areas to Analyze
- Controller method execution time
- Serialization (Jackson) performance
- Bean initialization & startup time
- @Async / thread pool usage
- Reactive (WebFlux) vs Servlet performance

JFR is excellent for finding slow endpoints or initialization bottlenecks in Spring Boot applications.

---

# Module 17: Kafka Troubleshooting with JFR

### Key Things to Investigate
- Record deserialization time
- Processing time per record
- Consumer rebalance storms
- Producer send latency
- Serialization bottlenecks on producer side

JFR helps you see whether lag is caused by **slow processing**, **deserialization**, or **network**.

---

# Module 18: SRE Incident War Stories

(20 detailed real-world incidents will be expanded in full version — examples include eCommerce checkout slowness, payment processing timeouts, inventory service OOM, Kafka rebalance storms, MongoDB driver issues, PostgreSQL connection pool exhaustion, Redis latency, Kubernetes OOMKills, etc.)

Each story includes:
- Symptoms + observed metrics
- JFR evidence
- Root cause
- Resolution steps
- Lessons learned

---

# Module 19: JFR vs Other Tools

### Decision Tree

**CPU Issue?**
- Use JFR (Method Profiling + Flame Graphs) first
- Fall back to async-profiler for native code or when JFR overhead is concern
- Use `perf` for kernel-level CPU

**Memory / Leak?**
- JFR (Allocation events) → Best for production
- Heap dump (jcmd GC.heap_dump) for post-mortem

**GC Issue?**
- JFR (GC events + pause times)
- GC logs (`-Xlog:gc*`)

**Lock / Thread Issue?**
- JFR (Thread states + Monitor events)
- jstack for quick snapshot

**Container / Kubernetes?**
- JFR + kubectl + ephemeral containers
- Combine with Prometheus + node metrics

---

# Module 20: SRE Production Playbook

### Recommended Incident Response Flow

```
Alert triggered
   ↓
Check Metrics (Prometheus/Grafana)
   ↓
Check Logs (ELK / Loki)
   ↓
Capture JFR (emergency or continuous)
   ↓
Analyze in JMC (start with Automated Analysis)
   ↓
Correlate with system tools (strace, top, iostat if needed)
   ↓
Identify Root Cause
   ↓
Apply Fix / Mitigation
   ↓
Document + Improve Runbook
```

### Emergency JFR Commands

```bash
# Quick 60-second capture
jcmd <PID> JFR.start name=Incident duration=60s filename=/tmp/incident.jfr

# Dump immediately
jcmd <PID> JFR.dump filename=/tmp/incident.jfr
```

---

## Bonus Modules (Summary)

**JVM Tuning Using JFR**
- Use allocation rate and GC data to right-size heap
- Tune thread pools based on actual utilization
- Optimize connection pools

**Continuous Profiling**
- Run low-overhead JFR continuously in production
- Integrate with observability platforms

**AI-Assisted JFR Analysis**
- Export JFR to JSON/CSV
- Use LLMs to summarize hot methods, leaks, and GC issues
- Auto-generate RCA drafts

---

## Hands-on Labs

1. Capture JFR from a running Spring Boot app
2. Analyze CPU hotspot using JMC Flame Graphs
3. Find a memory leak before OOM
4. Diagnose lock contention
5. Investigate GC pauses in G1 vs ZGC
6. Capture JFR from a Kubernetes pod using ephemeral container
7. Correlate JFR with Prometheus metrics during a simulated incident

---

## Interview Questions

(Full set of 30+ questions covering JVM internals, JFR commands, analysis techniques, Kubernetes scenarios, and comparison with other tools will be included in the complete version.)

---

## JFR Production Cheat Sheet

**Start Recording**
```bash
jcmd <PID> JFR.start name=Prod duration=300s filename=/tmp/recording.jfr settings=profile
```

**Dump Emergency**
```bash
jcmd <PID> JFR.dump filename=/tmp/emergency.jfr
```

**Key JMC Views**
- Automated Analysis (start here)
- Method Profiling / Flame Graph
- Memory → Allocations
- Threads
- Lock Instances

**Common Events to Watch**
- `jdk.ObjectAllocation*`
- `jdk.GCPhasePause`
- `jdk.JavaMonitorEnter`
- `jdk.ThreadPark`
- `jdk.ExceptionThrow`

---

## Troubleshooting Flowcharts

(Text-based flowcharts for CPU, Memory, GC, Thread, Lock, DB, and Kubernetes issues will be added in full version.)

---

**End of Course Outline**

This Markdown file provides the complete structure and substantial content for the first 15+ modules. The full version will expand every module with more diagrams, code examples, screenshots descriptions, detailed war stories, and all deliverables requested.

Would you like me to expand any specific module in more detail right now, or generate the full expanded version in parts? 

I can also create supporting files (labs, diagrams as ASCII/Mermaid, cheat sheet as separate MD, etc.). 

Ready for the next course in the series!