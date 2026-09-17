# SRE Runbook: High Latency in Kubernetes Java Services

## Purpose
Diagnose elevated response times, slow endpoints, timeouts, and latency regressions in Java services.

## Symptoms
- Increased p95, p99, or maximum latency.
- Request timeouts.
- Thread-pool saturation.
- Increased downstream dependency time.
- High GC pauses or CPU throttling.
- Queue growth in ingress, application, database, or messaging layers.

## Initial Triage

```bash
kubectl top pods -n <namespace>
kubectl get pods -n <namespace> -o wide
kubectl get hpa -n <namespace>
kubectl get events -n <namespace> --sort-by=.lastTimestamp
```

Review latency by:
- Endpoint.
- HTTP method.
- Status code.
- Pod.
- Availability zone or node.
- Request size.
- Downstream dependency.

## Determine Where Time Is Spent

Break request latency into:
1. Ingress or network time.
2. Application queue time.
3. Controller/service execution.
4. Database or cache calls.
5. External API calls.
6. Serialization and response transfer.

Check:
- Connection-pool wait time.
- Thread-pool queue length.
- Database query latency.
- Redis latency.
- Kafka or messaging lag.
- DNS and connection-establishment time.

## JVM Diagnostics

Capture a thread dump during the incident:

```bash
kubectl exec -n <namespace> <pod> -- jcmd <java-pid> Thread.print
```

Use JFR for a bounded recording:

```bash
kubectl exec -n <namespace> <pod> --   jcmd <java-pid> JFR.start name=latency-investigation duration=120s filename=/tmp/latency.jfr settings=profile
```

Review:
- Blocked and waiting threads.
- Lock contention.
- Socket read/write durations.
- File I/O.
- GC pauses.
- Allocation hotspots.
- Thread-pool saturation.

## Common Causes
- Slow database queries or missing indexes.
- Connection-pool exhaustion.
- Downstream service degradation.
- Lock contention.
- CPU throttling.
- Long GC pauses.
- Synchronous calls to slow dependencies.
- Retry amplification.
- Insufficient replicas.
- Uneven pod load.
- Large payloads or expensive serialization.

## Mitigation
- Reduce or stop retry storms.
- Increase replicas if the bottleneck is stateless capacity.
- Tune connection and thread pools based on measurements.
- Enable timeouts and circuit breakers.
- Route around an unhealthy dependency where possible.
- Roll back a confirmed latency-causing release.
- Optimize slow queries and add validated indexes.
- Reduce payload size or paginate large responses.

## Validation
Confirm recovery using:
- p50, p95, and p99 latency.
- Timeout rate.
- Dependency latency.
- Pool wait time.
- CPU and GC metrics.
- Request throughput.
- Error rate.

Do not close the incident based on average latency alone.
