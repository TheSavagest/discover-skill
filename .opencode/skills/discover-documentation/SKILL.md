---
name: discover-documentation
description: Discover README files, Markdown, ADRs, architecture documents, API documentation, runbooks and documented constraints.
compatibility: opencode
---

# Documentation Discovery

Find documentation and extract explicit statements. Documentation claims are evidence, not automatically truth.

## Inputs

- `run_id`: Current discovery run ID
- `project_root`: Repository root

## Inspect

| Doc Type | Patterns |
|----------|----------|
| README | `README*`, `readme*` |
| Markdown | `docs/**/*.md`, `*.md`, `**/*.md` |
| ADR | `docs/adr/**/*.md`, `docs/architecture/decisions/**/*.md`, `adr/**/*.md` |
| Architecture | `docs/architecture/**/*.md`, `ARCHITECTURE*`, `DESIGN*` |
| API Docs | `docs/api/**/*.md`, `swagger.json`, `openapi.json`, `*.yaml` (OpenAPI) |
| Runbooks | `docs/runbooks/**/*.md`, `runbooks/**/*.md`, `ops/**/*.md` |
| Deployment | `docs/deployment/**/*.md`, `DEPLOY*`, `RELEASE*` |
| Contributing | `CONTRIBUTING*`, `CONTRIBUTE*` |
| Code Comments | XML docs (`///`), JSDoc (`/** */`), architecture decision comments |

## Algorithm

1. Glob for documentation files
2. Parse Markdown for structure (headings, sections)
3. Extract explicit statements as facts
4. Link statements to source location (file + heading + line)
5. Compare documentation claims with code facts -> create conflicts if different

## Statement Extraction

Look for:
- Technology claims ("uses PostgreSQL", "built with React 18")
- Architecture claims ("follows Clean Architecture", "uses CQRS")
- Business claims ("Orders are processed asynchronously")
- Constraints ("API v1 must remain backward compatible")
- Requirements ("requires .NET 8", "Node 20+")

## Knowledge Operations

```bash
# Document entity
python knowledge.py add-entity --data '{
  "type": "document",
  "name": "README.md",
  "canonical_name": "README.md",
  "source": "<repository_src_id>",
  "location": {"path": "README.md", "revision": "<rev>"},
  "metadata": {"format": "markdown", "sections": ["Architecture", "Getting Started", "Deployment"]},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation"]},
  "status": "active",
  "discovered_by": {"agent": "documentation-discovery", "skill": "discover-documentation", "run": "<run_id>"}
}'

# Documentation claim as evidence
python knowledge.py add-evidence --data '{
  "source": "<README_src_id>",
  "locator": {"type": "document_section", "path": "README.md", "heading": "Architecture"},
  "observation": {"type": "text", "value": "The application uses PostgreSQL as the primary database.", "raw_text": "## Architecture\n\nThe application uses PostgreSQL as the primary database."},
  "discovered_by": {"agent": "documentation-discovery", "skill": "discover-documentation", "run": "<run_id>"},
  "confidence": 0.8
}'

# Conflict: docs vs code
python knowledge.py add-conflict --data '{
  "subject": "<PostgreSQL_db_ent_id>",
  "claims": ["<fact_readme_postgresql_id>", "<fact_code_sqlserver_id>"],
  "type": "documentation_vs_code",
  "severity": "high",
  "status": "unresolved",
  "detected_by": {"agent": "documentation-discovery", "run": "<run_id>"}
}'
```

## Rules

- Documentation claims become evidence with `documentation` basis (confidence 0.8)
- When code and documentation disagree, preserve BOTH and create Conflict
- Do not assume documentation is correct
- Extract ADR decisions as Decision entities (for Analysis phase)