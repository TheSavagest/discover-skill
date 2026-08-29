---
name: discover-source
description: Register and inspect available discovery sources such as repository files, Git, documentation, runtime, databases and external inputs.
compatibility: opencode
---

# Source Discovery

Identify all sources available to the discovery process.

## Inputs

- `run_id`: Current discovery run ID
- `project_root`: Repository root path

## Sources to Detect

| Source Type | Detection Method | Availability Check |
|-------------|------------------|-------------------|
| repository | Always available | ✓ |
| git_commit | `.git` exists | `git rev-parse HEAD` succeeds |
| documentation | `docs/`, `README*`, `*.md` exist | File system scan |
| database | Connection strings in config, EF Core DbContext | Config inspection |
| runtime | Environment variables, Docker, K8s | Optional - user provided |
| logs | Log files, logging config | Optional |
| metrics | Prometheus, AppInsights, etc. | Optional |
| traces | OpenTelemetry, Jaeger | Optional |
| ci | `.github/workflows`, `.gitlab-ci.yml`, `azure-pipelines.yml` | File system scan |
| deployment | Docker, K8s, Terraform, Helm | File system scan |
| user | Interactive mode | Always available |
| api_specification | OpenAPI/Swagger files | File system scan |

## Algorithm

1. Scan filesystem for indicator files
2. Inspect configuration files for connection strings, endpoints
3. Check environment for runtime access
4. For each detected source, create Source entity via `knowledge.py add-source`
5. Update discovery run with available/unavailable sources

## Knowledge Operations

```bash
# For each detected source
python knowledge.py add-source --data '{
  "type": "<source_type>",
  "uri": "<unique_uri>",
  "repository": {"path": "<path>", "revision": "<rev>"},
  "metadata": {...},
  "access": {"available": true, "limitation": "none"}
}'

# Update run
python knowledge.py query-runs --id <run_id>
# ... modify sources.available/unavailable ...
# (re-add run with updated data, or use merge logic)
```