# SRE Runbook: High CPU in Kubernetes Java Services

## Purpose
Investigate and mitigate sustained or sudden CPU utilization in Java services running on Kubernetes.

## Symptoms
- CPU utilization above the service or node threshold.
- HPA scaling rapidly or reaching `maxReplicas`.
- Increased request latency or timeout rates.
- High thread activity, excessive retries, or busy loops.
- CPU throttling despite apparently low application CPU usage.

## Initial Triage

```bash
kubectl top pods -n <namespace> --sort-by=cpu
kubectl top nodes
kubectl get hpa -n <namespace>
kubectl describe pod <pod> -n <namespace>
kubectl get events -n <namespace> --sort-by=.lastTimestamp
```

Check the configured requests and limits:

```bash
kubectl get deploy <deployment> -n <namespace> -o yaml
```

Look for:
- Missing or undersized CPU requests.
- Very low CPU limits causing throttling.
- HPA targets that do not match actual workload behavior.
- Uneven traffic distribution across pods.

## JVM and Thread Investigation

Identify the Java process:

```bash
kubectl exec -n <namespace> <pod> -- sh -c 'ps -ef | grep java'
```

Capture thread CPU usage:

```bash
kubectl exec -n <namespace> <pod> -- top -H -p <java-pid>
```

Convert a hot Linux thread ID to hexadecimal:

```bash
printf '%x\n' <thread-id>
```

Capture a thread dump:

```bash
kubectl exec -n <namespace> <pod> -- jcmd <java-pid> Thread.print
```

Correlate the hexadecimal thread ID with the `nid` value in the thread dump.

## Java Flight Recorder

Start a short diagnostic recording where permitted:

```bash
kubectl exec -n <namespace> <pod> --   jcmd <java-pid> JFR.start name=cpu-investigation duration=120s filename=/tmp/cpu.jfr settings=profile
```

Copy the recording:

```bash
kubectl cp <namespace>/<pod>:/tmp/cpu.jfr ./cpu.jfr
```

Review:
- Hot methods and execution samples.
- Thread states and blocked time.
- Lock contention.
- Allocation pressure.
- Garbage-collection activity.
- Socket and file I/O.

## Common Causes
- Inefficient loops or expensive algorithms.
- Excessive JSON serialization/deserialization.
- High-cardinality logging or debug logging.
- Retry storms.
- Synchronous blocking work on request threads.
- Excessive garbage creation.
- CPU throttling from container limits.
- Traffic imbalance or a single hot partition.

## Mitigation
- Scale out temporarily if capacity is available.
- Reduce excessive logging and disable debug logging where safe.
- Correct CPU requests and limits.
- Tune HPA targets and stabilization windows.
- Stop runaway traffic or retry loops.
- Roll back a recent change if evidence points to a deployment.
- Apply a code fix for the identified hot path.

## Validation
```bash
kubectl top pods -n <namespace>
kubectl get hpa -n <namespace>
```

Confirm:
- CPU returns to the expected range.
- Latency and error rates recover.
- HPA stabilizes.
- No new throttling or restart pattern appears.

## Evidence to Capture
- Time window and affected namespace/deployment.
- Pod and node CPU metrics.
- HPA status.
- Deployment version and recent changes.
- Thread dump or JFR recording.
- Relevant application and access logs.
- Before/after graphs.
