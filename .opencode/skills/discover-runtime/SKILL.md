---
name: discover-runtime
description: Discover deployed versions, runtime configuration, containers, logs, metrics, traces and health information when access is available.
compatibility: opencode
---

# Runtime Discovery

Optional. Only inspect explicitly available runtime sources. Never reveal secrets. Never mutate runtime state.

## Inputs

- `run_id`: Current discovery run ID
- `runtime_access`: User-provided access configuration (optional)

## Sources (if available)

| Source | Access Method | Data |
|--------|---------------|------|
| Deployed version | Git tag, CI/CD artifact, API `/version` | Commit hash, version, build date |
| Running containers | Docker CLI, Kubernetes API | Image, status, resources, env vars (masked) |
| Environment | Kubernetes ConfigMap/Secret, Azure App Configuration, AWS Parameter Store | Config keys (values masked) |
| Health | `/health`, `/healthz`, `/live`, `/ready` endpoints | Status, dependencies |
| Logs | File, stdout, Elasticsearch, Loki, CloudWatch | Recent errors, patterns |
| Metrics | Prometheus, Grafana, Datadog, App Insights | Latency, error rate, throughput |
| Traces | Jaeger, Zipkin, Tempo, App Insights | Request flows, bottlenecks |

## Algorithm

1. Check what runtime access is configured
2. For each available source:
   - Query deployed version (compare with git HEAD)
   - List running containers/services
   - Fetch health status
   - Sample recent logs (last 1000 lines)
   - Query key metrics (latency p99, error rate, QPS)
   - Sample traces for key endpoints
3. Record unavailable sources explicitly

## Knowledge Operations

```bash
# Runtime source
python knowledge.py add-source --data '{
  "type": "runtime",
  "uri": "kubernetes://prod-cluster/myapp",
  "metadata": {"cluster": "prod-cluster", "namespace": "myapp"},
  "access": {"available": true, "limitation": "read_only"}
}'

# Deployed version entity
python knowledge.py add-entity --data '{
  "type": "deployment",
  "name": "myapp-api-prod",
  "canonical_name": "myapp-api",
  "source": "<runtime_src_id>",
  "location": {"path": "kubernetes://prod-cluster/myapp/myapp-api"},
  "metadata": {"image": "myapp-api:v2.3.1", "replicas": 5, "revision": "abc123def", "deployed_at": "2026-08-28T14:30:00Z"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["dynamic_observation"]},
  "status": "active",
  "discovered_by": {"agent": "runtime-discovery", "skill": "discover-runtime", "run": "<run_id>"}
}'

# Fact: repo vs production diff
python knowledge.py add-fact --data '{
  "subject": {"entity": "<repository_ent_id>"},
  "predicate": "differs_from",
  "object": {"kind": "entity", "entity": "<myapp-api-prod_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["dynamic_observation", "direct_observation"]},
  "status": "active",
  "discovered_by": {"agent": "runtime-discovery", "skill": "discover-runtime", "run": "<run_id>"}
}'

# Health fact
python knowledge.py add-fact --data '{
  "subject": {"entity": "<myapp-api-prod_ent_id>"},
  "predicate": "has_health",
  "object": {"kind": "value", "value": "healthy"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["dynamic_observation"]},
  "status": "active",
  "discovered_by": {"agent": "runtime-discovery", "skill": "discover-runtime", "run": "<run_id>"}
}'

# Unavailable source
python knowledge.py add-source --data '{
  "type": "logs",
  "uri": "elasticsearch://prod-logs",
  "access": {"available": false, "limitation": "offline"}
}'
```

## Rules

- Record unavailable sources explicitly in run.sources.unavailable
- Mask all secrets, connection strings, API keys in evidence
- Never mutate runtime state (no restarts, no config changes)
- If no runtime access, skip gracefully - discovery continues without it