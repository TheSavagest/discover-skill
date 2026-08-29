---
name: discover-infrastructure
description: Discover Docker, Kubernetes, cloud, Terraform, CI/CD, deployment and environment configuration.
compatibility: opencode
---

# Infrastructure Discovery

Inspect infrastructure definitions. Record configuration facts only. Do not claim correctness.

## Inputs

- `run_id`: Current discovery run ID
- `project_root`: Repository root

## Inspect

| Category | Files/Patterns |
|----------|----------------|
| Docker | `Dockerfile*`, `docker-compose*.yml`, `.dockerignore` |
| Kubernetes | `k8s/**/*.yaml`, `kubernetes/**/*.yaml`, `helm/**/*.yaml`, `*.k8s.yaml` |
| Helm | `Chart.yaml`, `values*.yaml`, `templates/**/*.yaml` |
| Terraform | `*.tf`, `*.tfvars`, `modules/**/*.tf` |
| CloudFormation | `*.cfn.yaml`, `*.cfn.json`, `cloudformation/**/*.yaml` |
| Azure Bicep | `*.bicep` |
| CI | `.github/workflows/*.yml`, `.gitlab-ci.yml`, `azure-pipelines.yml`, `Jenkinsfile`, `.circleci/config.yml` |
| CD | ArgoCD, Flux, Spinnaker configs |
| Environments | `.env*`, `appsettings.*.json`, `*.env`, `*.local.json` |
| Health | `healthcheck` in Dockerfile, `/health` endpoints, Kubernetes probes |
| Logging | `serilog`, `ILogger`, `Microsoft.Extensions.Logging`, `winston`, `pino` config |
| Monitoring | `prometheus`, `grafana`, `datadog`, `newrelic`, `appinsights` config |

## Algorithm

1. Glob for infrastructure files
2. Parse each file type for configuration facts
3. Extract: base images, ports, env vars, volumes, resources, replicas
4. Extract CI/CD: triggers, jobs, steps, environments
5. Extract Terraform: resources, modules, providers, outputs
6. Create entities for each infrastructure component

## Knowledge Operations

```bash
# Dockerfile entity
python knowledge.py add-entity --data '{
  "type": "container",
  "name": "MyApp.Api",
  "canonical_name": "myapp-api",
  "source": "<repository_src_id>",
  "location": {"path": "src/MyApp.Api/Dockerfile", "revision": "<rev>"},
  "metadata": {"base_image": "mcr.microsoft.com/dotnet/aspnet:8.0", "ports": [8080], "env_vars": ["ASPNETCORE_ENVIRONMENT"]},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation"]},
  "status": "active",
  "discovered_by": {"agent": "infrastructure-discovery", "skill": "discover-infrastructure", "run": "<run_id>"}
}'

# Kubernetes deployment entity
python knowledge.py add-entity --data '{
  "type": "deployment",
  "name": "myapp-api",
  "canonical_name": "myapp-api",
  "source": "<repository_src_id>",
  "location": {"path": "k8s/deployment.yaml", "revision": "<rev>"},
  "metadata": {"replicas": 3, "image": "myapp-api:latest", "resources": {"limits": {"cpu": "500m", "memory": "512Mi"}}},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation"]},
  "status": "active",
  "discovered_by": {"agent": "infrastructure-discovery", "skill": "discover-infrastructure", "run": "<run_id>"}
}'

# CI pipeline entity
python knowledge.py add-entity --data '{
  "type": "pipeline",
  "name": "CI",
  "canonical_name": "github-actions-ci",
  "source": "<repository_src_id>",
  "location": {"path": ".github/workflows/ci.yml", "revision": "<rev>"},
  "metadata": {"trigger": "push", "jobs": ["build", "test", "docker"]},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation"]},
  "status": "active",
  "discovered_by": {"agent": "infrastructure-discovery", "skill": "discover-infrastructure", "run": "<run_id>"}
}'

# Fact: pipeline deploys container
python knowledge.py add-fact --data '{
  "subject": {"entity": "<github-actions-ci_ent_id>"},
  "predicate": "deploys_to",
  "object": {"kind": "entity", "entity": "<myapp-api_deployment_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 0.9, "basis": ["inference"]},
  "status": "active",
  "discovered_by": {"agent": "infrastructure-discovery", "skill": "discover-infrastructure", "run": "<run_id>"}
}'
```