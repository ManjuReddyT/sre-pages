# SRE Runbook: High Memory in Kubernetes Java Services

## Purpose
Investigate high memory usage, OOMKills, container restarts, and possible Java heap or native-memory leaks.

## Symptoms
- Container memory near its limit.
- `OOMKilled` termination reason.
- Frequent pod restarts.
- Increasing old-generation occupancy.
- Long or frequent garbage-collection pauses.
- `OutOfMemoryError` in application logs.

## Initial Triage

```bash
kubectl top pods -n <namespace> --sort-by=memory
kubectl describe pod <pod> -n <namespace>
kubectl get events -n <namespace> --sort-by=.lastTimestamp
kubectl get pod <pod> -n <namespace> -o jsonpath='{.status.containerStatuses[*].lastState.terminated.reason}'
```

Check configured resources:

```bash
kubectl get deploy <deployment> -n <namespace> -o yaml
```

Compare:
- Container memory limit.
- JVM heap settings.
- Non-heap and native-memory requirements.
- Number of threads.
- Direct-buffer usage.
- Metaspace usage.

## JVM Memory Checks

```bash
kubectl exec -n <namespace> <pod> -- jcmd <java-pid> VM.flags
kubectl exec -n <namespace> <pod> -- jcmd <java-pid> GC.heap_info
kubectl exec -n <namespace> <pod> -- jcmd <java-pid> VM.native_memory summary
```

Native Memory Tracking must be enabled at JVM startup for detailed output:

```text
-XX:NativeMemoryTracking=summary
```

Check GC logs for:
- Increasing post-GC heap occupancy.
- Full GC frequency.
- Promotion failures.
- Humongous allocations.
- Long pause times.

## Heap Dump

Only capture a heap dump after assessing disk capacity and operational impact:

```bash
kubectl exec -n <namespace> <pod> -- jcmd <java-pid> GC.heap_dump /tmp/heap.hprof
kubectl cp <namespace>/<pod>:/tmp/heap.hprof ./heap.hprof
```

Analyze with Eclipse MAT or another approved heap-analysis tool.

Look for:
- Dominator tree leaders.
- Large collections and maps.
- Retained objects.
- Class-loader leaks.
- Unbounded caches.
- Request/session objects retained too long.

## Common Causes
- Unbounded in-memory caches.
- Static collections retaining objects.
- ThreadLocal leaks.
- Excessive direct buffers.
- Too many threads.
- Large response/request payloads.
- Class-loader leaks after redeployments.
- Heap sizing too close to the container limit.
- Native memory or off-heap allocations.

## Mitigation
- Scale out if memory pressure is traffic-related.
- Reduce cache size or add expiry.
- Fix object-retention or listener leaks.
- Reduce payload sizes and buffering.
- Review thread-pool sizes.
- Increase container memory only after identifying the memory category.
- Keep headroom between JVM heap and container limit.
- Enable heap-dump-on-OOM only with sufficient disk capacity.

## Validation
```bash
kubectl top pod <pod> -n <namespace>
kubectl get pod <pod> -n <namespace> -w
```

Confirm:
- Memory remains below the limit.
- No repeated OOMKills.
- Post-GC heap occupancy is stable.
- Restart rate returns to normal.
- Latency and error rates remain healthy.
