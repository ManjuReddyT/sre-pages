# SRE Runbook: High Error Rate in Kubernetes Java Services

## Purpose
Investigate elevated HTTP 4xx/5xx responses, application exceptions, failed dependencies, and rollout-related errors.

## Symptoms
- Increased 5xx rate.
- Unexpected 4xx spike.
- Failed health checks.
- CrashLoopBackOff or frequent restarts.
- Increased timeout, reset, or connection-refused errors.
- Error concentration in one pod, node, version, or endpoint.

## Initial Triage

```bash
kubectl get pods -n <namespace> -o wide
kubectl get deploy <deployment> -n <namespace>
kubectl rollout history deploy/<deployment> -n <namespace>
kubectl get events -n <namespace> --sort-by=.lastTimestamp
```

Inspect logs:

```bash
kubectl logs -n <namespace> <pod> --since=30m
kubectl logs -n <namespace> <pod> --previous
```

Check status-code distribution by:
- Endpoint.
- HTTP method.
- Pod.
- Application version.
- Dependency.
- Tenant or request type.
- Region or availability zone.

## Classify the Errors

### 4xx Errors
Investigate:
- Authentication or authorization failures.
- Invalid request payloads.
- Missing headers or cookies.
- API contract changes.
- Routing or ingress rules.
- Rate limiting.
- Client version incompatibility.

### 5xx Errors
Investigate:
- Application exceptions.
- Database or cache failures.
- Downstream timeouts.
- Connection-pool exhaustion.
- Out-of-memory events.
- Failed readiness or liveness probes.
- Bad configuration or secret changes.
- Deployment regressions.

## Kubernetes Checks

```bash
kubectl describe pod <pod> -n <namespace>
kubectl describe svc <service> -n <namespace>
kubectl describe ingress <ingress> -n <namespace>
kubectl get endpoints <service> -n <namespace>
kubectl get endpointslices -n <namespace>
```

Verify:
- Ready endpoints exist.
- Service selectors match pod labels.
- Readiness probes are correct.
- Ingress routes to the expected service.
- Pods are not repeatedly removed from service.
- Network policies permit required traffic.

## Java Diagnostics

Capture relevant exceptions and a thread dump:

```bash
kubectl exec -n <namespace> <pod> -- jcmd <java-pid> Thread.print
```

Use JFR when errors appear related to:
- Lock contention.
- Slow I/O.
- GC pauses.
- Thread starvation.
- Excessive allocation.

## Mitigation
- Roll back a confirmed bad deployment.
- Remove unhealthy pods only when replacement capacity is available.
- Correct configuration, secret, or routing errors.
- Restore failed dependencies or activate a fallback.
- Adjust probe settings only after validating application startup and health behavior.
- Rate-limit abusive or runaway clients.
- Disable a faulty feature flag if an approved control exists.

## Validation
Confirm:
- 4xx/5xx rates return to baseline.
- Error signatures disappear or reduce materially.
- All intended endpoints have healthy backends.
- No new restart or probe-failure pattern appears.
- Recovery is consistent across pods and versions.

## Evidence to Capture
- Error-rate graph and exact incident window.
- Representative request IDs.
- Application stack traces.
- Pod events and termination reasons.
- Deployment version and recent changes.
- Dependency health and latency.
- Before/after validation metrics.
