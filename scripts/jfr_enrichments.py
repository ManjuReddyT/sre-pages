"""Supplemental rich content for JFR course modules (parity with strace Academy depth)."""

from typing import List, Tuple

def insight(title: str, body: str) -> str:
    return f'''<div class="bg-slate-950 border border-slate-700 p-5 rounded-2xl my-6 text-sm">
        <div class="font-semibold mb-2 text-amber-400">{title}</div>
        <p class="text-slate-300">{body}</p>
    </div>'''

def tip(body: str) -> str:
    return f'''<div class="mt-6 p-4 bg-amber-950/30 border border-amber-900 rounded-2xl text-sm">
        <div class="text-xs uppercase tracking-widest text-amber-400 mb-1">SRE TIP</div>
        <p class="text-slate-300">{body}</p>
    </div>'''

def pattern_cards(cards: List[Tuple[str, str, str]]) -> str:
    items = "".join(
        f'<div class="p-4 bg-slate-950 rounded-2xl border border-slate-800">'
        f'<span class="font-mono text-sm {color}">{label}</span><br>'
        f'<span class="text-xs text-slate-400 mt-1 block">{desc}</span></div>'
        for label, color, desc in cards
    )
    return f'<div class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">{items}</div>'

def command_grid(commands: List[Tuple[str, str]]) -> str:
    rows = "".join(
        f'<div class="flex gap-3 text-sm"><code class="jfr-code flex-shrink-0">{cmd}</code>'
        f'<span class="text-slate-400">{desc}</span></div>'
        for cmd, desc in commands
    )
    return f'<div class="space-y-4 mt-4">{rows}</div>'

MODULE_ENRICHMENTS = {
    1: insight("Key Insight", "JFR writes events to a ring buffer — old events are overwritten unless you dump to a <code class=\"jfr-code\">.jfr</code> file. This is why duration and <code class=\"jfr-code\">maxsize</code> matter in production."),
    2: insight("Ground Truth", "When Prometheus shows high latency but logs are clean, JFR often reveals GC pauses, lock waits, or JDBC acquisition time that APM agents miss."),
    3: tip("TLAB allocations are fast path — when you see high <code class=\"jfr-code\">ObjectAllocationOutsideTLAB</code>, allocation pressure is severe and GC will follow.")
        + '''<h4 class="font-semibold text-amber-400 mt-6 mb-3">Heap Generations (G1)</h4>
    <div class="jfr-output rounded-2xl text-xs">Young Gen (Eden + Survivor) → promotion → Old Gen
Metaspace (class metadata, unbounded by default)
Thread stacks + native memory (not in heap, but affects RSS)</div>''',
    4: '<div class="grid md:grid-cols-2 gap-8 mt-4">'
        + '<div><h4 class="font-semibold text-amber-400 mb-3">Live Process (jcmd)</h4>'
        + command_grid([
            ("jcmd <PID> JFR.start name=R duration=300s filename=/tmp/app.jfr", "Timed recording"),
            ("jcmd <PID> JFR.dump filename=/tmp/snapshot.jfr", "Dump buffer now"),
            ("jcmd <PID> JFR.check", "List active recordings"),
            ("jcmd <PID> JFR.stop name=R", "Stop named recording"),
        ]) + '</div><div><h4 class="font-semibold text-amber-400 mb-3">Startup Flags</h4>'
        + command_grid([
            ("-XX:StartFlightRecording=settings=profile", "High-detail profile at boot"),
            ("-XX:StartFlightRecording=maxsize=250M", "Ring buffer cap"),
            ("-XX:StartFlightRecording=delay=60s", "Skip startup noise"),
            ("-XX:FlightRecorderOptions=stackdepth=256", "Deeper stack traces"),
        ]) + '</div></div>',
    5: pattern_cards([
        ("jdk.ExecutionSample + CPULoad", "text-amber-400", "CPU hotspots and JVM load"),
        ("jdk.ObjectAllocationInNewTLAB", "text-sky-400", "Allocation rate per class"),
        ("jdk.GCPhasePause", "text-red-400", "Stop-the-world pause duration"),
        ("jdk.JavaMonitorEnter", "text-purple-400", "Synchronized block contention"),
        ("jdk.ExceptionThrow", "text-rose-400", "Exception frequency + stacks"),
    ]),
    6: '''<h4 class="font-semibold text-amber-400 mt-6 mb-3">JMC Analysis Workflow</h4>
    <ol class="list-decimal pl-5 space-y-2 text-sm text-slate-300">
        <li>Open <strong>.jfr</strong> file → start with <strong>Automated Analysis</strong></li>
        <li>Review flagged problems (GC, memory, hot methods)</li>
        <li>Drill into <strong>Method Profiling</strong> / flame graph for CPU</li>
        <li>Check <strong>Memory → Allocations</strong> for leak suspects</li>
        <li>Use <strong>Threads</strong> + <strong>Lock Instances</strong> for contention</li>
        <li>Export findings for postmortem / ticket</li>
    </ol>''' + tip("Always correlate JMC timestamps with your Grafana incident window — misaligned recordings lead to wrong conclusions."),
    7: '''<h4 class="font-semibold text-amber-400 mt-4 mb-3">Investigation Workflow</h4>
    <ol class="list-decimal pl-5 space-y-1 text-sm text-slate-300 mb-4">
        <li>Capture JFR during CPU spike (60–120s)</li>
        <li>Open Method Profiling / flame graph in JMC</li>
        <li>Sort by self-time and total-time</li>
        <li>Check jdk.Compilation event rate (JIT storm?)</li>
        <li>Correlate hot methods with deployment / config change</li>
    </ol>''' + pattern_cards([
        ("com.fasterxml.jackson.* 35%", "text-amber-400", "JSON serialization storm"),
        ("java.util.regex.* 22%", "text-red-400", "Catastrophic backtracking"),
        ("jdk.Compilation burst", "text-sky-400", "Cold start or new code path"),
        ("while(true) tight loop", "text-red-400", "Bug or missing sleep/backoff"),
    ]),
    8: pattern_cards([
        ("byte[] growing", "text-amber-400", "Buffer leak or unbounded cache"),
        ("ConcurrentHashMap entries", "text-amber-400", "Unbounded in-memory map"),
        ("ThreadLocal + pool threads", "text-red-400", "Classic leak in Tomcat/Spring"),
        ("char[] from String concat", "text-amber-400", "Logging or XML building in loop"),
    ]) + '''<h4 class="font-semibold text-amber-400 mt-6 mb-3">Investigation Steps</h4>
    <ol class="list-decimal pl-5 space-y-1 text-sm text-slate-300">
        <li>Memory view → Allocations tab → sort by allocated bytes</li>
        <li>Identify top 3 classes by rate and total</li>
        <li>Check if rate grows linearly over recording window</li>
        <li>Take heap dump only if you need object retainers</li>
    </ol>''',
    9: '''<h4 class="font-semibold text-amber-400 mt-4 mb-3">GC Red Flags in JFR</h4>
    <ul class="list-disc pl-5 text-sm text-slate-300 space-y-1">
        <li>Full GC more than once per hour in steady state</li>
        <li>GCPhasePause &gt; 200ms on latency-sensitive services</li>
        <li>PromotionFailed events (G1 cannot evacuate in time)</li>
        <li>Humongous allocations dominating old gen (G1)</li>
    </ul>
    <div class="mt-4 grid md:grid-cols-3 gap-3 text-sm">
        <div class="p-4 bg-slate-950 rounded-2xl"><strong class="text-amber-400">G1GC</strong><br><span class="text-slate-400">Default JDK 9+. Balance throughput &amp; pauses.</span></div>
        <div class="p-4 bg-slate-950 rounded-2xl"><strong class="text-amber-400">ZGC</strong><br><span class="text-slate-400">Sub-ms pauses, large heaps, JDK 17+.</span></div>
        <div class="p-4 bg-slate-950 rounded-2xl"><strong class="text-amber-400">Shenandoah</strong><br><span class="text-slate-400">Low pause, concurrent compaction.</span></div>
    </div>''',
    10: pattern_cards([
        ("All threads BLOCKED", "text-red-400", "Deadlock or pool exhaustion"),
        ("RUNNABLE but low throughput", "text-amber-400", "CPU burn in tight loop"),
        ("WAITING on pool queue", "text-amber-400", "Thread pool too small"),
        ("TIMED_WAITING on HTTP", "text-sky-400", "Slow downstream dependency"),
    ]),
    11: tip("If <code class=\"jfr-code\">JavaMonitorEnter</code> duration exceeds request SLA on hot path, even microsecond locks aggregate to seconds under load."),
    12: '''<h4 class="font-semibold text-amber-400 mt-4 mb-3">Pool vs Query — Decision Guide</h4>
    <div class="grid md:grid-cols-2 gap-4 text-sm">
        <div class="p-4 bg-slate-950 rounded-2xl border border-slate-800">
            <strong class="text-red-400">Pool acquisition slow</strong>
            <p class="text-slate-400 mt-2">All threads waiting for connection. Fix pool size, leak, or DB connectivity.</p>
        </div>
        <div class="p-4 bg-slate-950 rounded-2xl border border-slate-800">
            <strong class="text-amber-400">Query execution slow</strong>
            <p class="text-slate-400 mt-2">Connections acquired fast but JDBC/socket time high. Index/query/DB issue.</p>
        </div>
    </div>''',
    13: '''<h4 class="font-semibold text-amber-400 mt-4 mb-3">Latency Budget Breakdown</h4>
    <div class="jfr-output rounded-2xl text-xs">Request thread timeline (example P99 = 2.4s):
  0–50ms   Controller + validation
  50–80ms  Jackson deserialize
  80–2100ms HikariCP acquire + JDBC (ROOT CAUSE)
  2100–2300ms Jackson serialize
  2300ms   Response sent</div>''',
    14: pattern_cards([
        ("NullPointerException × 50k/min", "text-red-400", "Hot path bug — CPU waste"),
        ("SocketTimeoutException burst", "text-amber-400", "Downstream or pool issue"),
        ("SQLException in retry loop", "text-red-400", "Amplifies load during incident"),
    ]),
    15: '''<div class="my-4"><div class="code-header">kubectl debug (ephemeral container)</div><pre class="jfr-output">kubectl debug -it &lt;pod&gt; --image=amazoncorretto:17 --target=&lt;container&gt; --share-processes
jcmd 1 JFR.start name=k8s duration=120s filename=/tmp/pod.jfr settings=profile
jcmd 1 JFR.dump filename=/tmp/pod.jfr
exit
kubectl cp &lt;pod&gt;:/tmp/pod.jfr ./pod-incident.jfr</pre></div>'''
        + tip("For distroless images, never install JDK into the app container — ephemeral debug containers are the production-safe pattern."),
    16: command_grid([
        ("-XX:StartFlightRecording=filename=/tmp/boot.jfr,delay=10s", "Profile Spring Boot startup"),
        ("spring.jmx.enabled=true", "Enable JMX for jcmd in some setups"),
        ("management.endpoints.web.exposure.include=health", "Keep actuator minimal in prod"),
    ]),
    17: '''<p class="text-slate-300 mb-4">Kafka lag triage with JFR:</p>
    <ol class="list-decimal pl-5 text-sm text-slate-300 space-y-1">
        <li>High <code class="jfr-code">ObjectAllocation</code> on deserialize → payload/schema issue</li>
        <li>Long method samples in <code class="jfr-code">@KafkaListener</code> → business logic slow</li>
        <li>Many threads in rebalance/wait → consumer group instability</li>
        <li>SocketWrite blocked → broker or network bottleneck</li>
    </ol>''',
    19: '''<div class="mt-4 space-y-3 text-sm">
        <div class="p-4 bg-slate-950 rounded-2xl"><strong class="text-amber-400">CPU?</strong> → JFR flame graph first, async-profiler if native-heavy</div>
        <div class="p-4 bg-slate-950 rounded-2xl"><strong class="text-amber-400">Memory leak?</strong> → JFR allocations live, heap dump post-mortem</div>
        <div class="p-4 bg-slate-950 rounded-2xl"><strong class="text-amber-400">GC pauses?</strong> → JFR GC events + correlate GC logs</div>
        <div class="p-4 bg-slate-950 rounded-2xl"><strong class="text-amber-400">Threads/locks?</strong> → JFR + jstack snapshot</div>
        <div class="p-4 bg-slate-950 rounded-2xl"><strong class="text-amber-400">OS/syscall?</strong> → strace at kernel boundary (Course 1)</div>
    </div>''',
    20: '''<h4 class="font-semibold text-amber-400 mt-4 mb-3">Production Incident Playbook</h4>
    <div class="flex flex-wrap gap-2 mb-4">
        <span class="text-xs px-3 py-1 bg-slate-800 rounded-full">1. Alert fires</span>
        <span class="text-xs px-3 py-1 bg-slate-800 rounded-full">2. Grafana dashboards</span>
        <span class="text-xs px-3 py-1 bg-slate-800 rounded-full">3. Log correlation</span>
        <span class="text-xs px-3 py-1 bg-amber-900/50 text-amber-300 rounded-full">4. JFR capture</span>
        <span class="text-xs px-3 py-1 bg-slate-800 rounded-full">5. JMC analysis</span>
        <span class="text-xs px-3 py-1 bg-slate-800 rounded-full">6. strace if needed</span>
        <span class="text-xs px-3 py-1 bg-slate-800 rounded-full">7. Fix + postmortem</span>
    </div>''',
}

WAR_STORY_DETAILS = [
    ("eCommerce Checkout Slowness", "SEV2", "P99 checkout latency 800ms → 4.2s",
     "Grafana: latency spike, normal CPU. Logs: no errors.",
     "JFR: jdk.GCPhasePause events 1.8–2.1s every 45s. Humongous byte[] allocations during cart serialization.",
     "G1 humongous objects + undersized heap. Promotion failures during peak traffic.",
     "Increased heap 4G→8G, tuned -XX:G1HeapRegionSize, fixed oversized session cart caching.",
     "Always check GC pauses in JFR when latency spikes without error logs."),
    ("Payment Gateway Timeouts", "SEV1", "30% payment failures, HikariCP timeouts",
     "Metrics: pool active=50/50, pending threads growing. Logs: getConnection timed out.",
     "JFR: threads blocked 8–12s on HikariCP.getConnection. JDBC events near zero until timeout.",
     "Connection leak in failed-payment rollback path — connections not returned to pool.",
     "Hotfix: try-with-resources on Connection. Pool recovered in 3 min.",
     "Distinguish pool starvation from slow queries using JFR thread + JDBC timing."),
    ("Inventory Service OOMKilled", "SEV2", "Pod restart loop in Kubernetes",
     "K8s: OOMKilled. Heap metrics showed growth over 6 hours.",
     "JFR (pre-OOM): ConcurrentHashMap allocations 2.4 GB/hour. Top class: InventoryCacheEntry.",
     "Unbounded local cache without TTL/eviction on inventory SKU map.",
     "Added Caffeine cache with maxSize + expireAfterWrite. Memory flatlined.",
     "JFR allocation events find leaks days before OOMKill."),
    ("Kafka Consumer Lag Storm", "SEV2", "Lag 2M messages, consumer group stalled",
     "Metrics: lag ↑, CPU moderate. Logs: rebalance noise.",
     "JFR: 68% sample time in Avro deserialization. ObjectAllocation char[] and byte[] dominant.",
     "Schema change increased payload 4x. Deserialization became bottleneck.",
     "Scaled consumers + optimized Avro reader. Consider payload slimming.",
     "Kafka lag is not always broker — JFR shows per-record processing cost."),
    ("PostgreSQL Connection Storm", "SEV2", "API errors, DB 'too many connections'",
     "DB metrics: connections at max. App: thread pool exhausted.",
     "JFR: 200 threads in TIMED_WAITING on socket read; connection storm to PG.",
     "Missing connection pool limit on new microservice — each pod opened 100+ direct connections.",
     "Enforced HikariCP maxPoolSize=20 per pod. Added PgBouncer.",
     "JFR thread view exposes connection storms faster than DB metrics alone."),
    ("Redis Cache Timeout Cascade", "SEV3", "Elevated latency across 12 services",
     "Redis latency P99 high. Dependent services timing out.",
     "JFR on caller service: threads WAITING on Jedis connection pool; ExceptionThrow SocketTimeoutException.",
     "Redis single-node CPU saturated after bad key pattern (KEYS in cron).",
     "Removed KEYS usage, added read replica, increased pool with backoff.",
     "ExceptionThrow frequency in JFR reveals retry/timeout storms early."),
    ("Spring Boot Startup 4 Minutes", "SEV3", "New deployment pods slow to pass readiness",
     "K8s: readiness probe failures for 240s. No runtime errors.",
     "JFR from boot: jdk.ClassLoad + jdk.Compilation dominated first 180s. Bean init for 400+ beans.",
     "Monolith-style classpath scan + eager @PostConstruct on heavy clients.",
     "Lazy init, split actuator, reduced @ComponentScan scope. Startup → 45s.",
     "JFR startup recordings justify JVM tuning and Spring refactor with data."),
    ("API P99 Degradation — Lock Contention", "SEV2", "Checkout API P99 200ms → 1.8s",
     "CPU normal, DB healthy. APM showed gap in 'application' time.",
     "JFR: jdk.JavaMonitorEnter on com.acme.PromoService.applyPromo — 40 threads blocked avg 400ms.",
     "synchronized block around promo DB call — accidental serialization of all requests.",
     "Replaced with per-key locking + async cache. P99 restored.",
     "Lock Instances view in JMC finds hidden serialization under load."),
]

INTERVIEW_QUESTIONS = [
    ("What makes JFR safe for production compared to traditional profilers?", "Very low overhead (<1%), built into JVM, ring buffer design, no bytecode injection."),
    ("How do you start a 5-minute JFR recording on PID 12345?", "jcmd 12345 JFR.start name=incident duration=300s filename=/tmp/incident.jfr settings=profile"),
    ("What JMC view do you open first and why?", "Automated Analysis — rules engine surfaces GC, memory, and hot method issues immediately."),
    ("Name three JFR events for memory leak investigation.", "ObjectAllocationInNewTLAB, ObjectAllocationOutsideTLAB, and heap usage trends in Memory view."),
    ("How do you capture JFR from a distroless Kubernetes pod?", "kubectl debug ephemeral container with JDK image, share-processes, jcmd on JVM PID, kubectl cp .jfr out."),
    ("JFR vs heap dump — when to use each?", "JFR live for allocation rate and hotspots; heap dump post-mortem for object retainers and dominators."),
    ("What does high ObjectAllocationOutsideTLAB indicate?", "Severe allocation pressure — objects too large for TLAB or TLAB exhausted."),
    ("How do you correlate JFR with an incident window?", "Note recording start/end UTC, align with Grafana alert time, filter JMC events to that range."),
    ("What JDK versions include JFR for free?", "OpenJDK 11+ (flight recorder enabled by default in modern builds)."),
    ("JFR vs async-profiler?", "JFR: broad JVM events, GC, allocations, low overhead. async-profiler: excellent CPU/native flame graphs."),
]

FLOWCHARTS = [
    ("CPU Spike", ["CPU alert?", "Capture JFR 60–120s", "JMC flame graph", "Hot Java method?", "Fix code / JIT warm-up", "Still high? → strace/perf"]),
    ("Memory / OOM", ["Heap growing?", "JFR allocation events", "Top class growing?", "Leak in app code", "OOMKilled? → heap dump + JFR"]),
    ("High Latency", ["P95/P99 up, no errors?", "JFR during window", "GC pauses?", "Lock contention?", "JDBC/pool wait?", "External timeout?"]),
    ("GC Problems", ["GC pause alert?", "jdk.GCPhasePause in JFR", "Full GC frequent?", "Tune heap/GC or fix allocation", "Humongous objects?"]),
    ("Thread Issues", ["Throughput collapsed?", "JFR Threads view", "All blocked?", "jstack correlate", "Fix deadlock/pool size"]),
    ("Kubernetes", ["Pod slow/OOM?", "kubectl debug + jcmd", "JFR dump + cp", "JMC analysis", "Adjust limits/heap/code"]),
]