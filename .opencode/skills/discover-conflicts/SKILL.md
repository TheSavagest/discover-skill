---
name: discover-conflicts
description: Detect contradictory facts from repository, documentation, Git, runtime and user-provided sources.
compatibility: opencode
---

# Conflict Detection

A conflict exists when credible sources assert incompatible facts. Do not resolve by guessing.

## Conflict Types

| Type | Example |
|------|---------|
| contradictory_facts | Source A says PostgreSQL, Source B says SQL Server |
| documentation_vs_code | README says RabbitMQ, code uses Kafka |
| documentation_vs_runtime | Docs say v1 API, runtime serves v2 |
| source_vs_source | appsettings.json vs environment variable |
| stale_vs_current | Migration says column exists, DB doesn't have it |

## Detection Algorithm

1. **Group facts by subject + predicate**
2. **For each group, check if object values conflict**
3. **Check documentation claims vs code facts**
4. **Check runtime facts vs code facts**
5. **Check Git history vs current state**
6. **For each conflict, create Conflict entity**

## Severity

- **Critical** - Affects production correctness, security, data integrity
- **High** - Affects major architectural understanding
- **Medium** - Affects component behavior understanding
- **Low** - Minor discrepancy, cosmetic

## Knowledge Operations

```bash
# Create conflict
python knowledge.py add-conflict --data '{
  "subject": "<AppDbContext_ent_id>",
  "claims": ["<fact_postgresql_id>", "<fact_sqlserver_id>"],
  "type": "contradictory_facts",
  "severity": "critical",
  "status": "unresolved",
  "detected_by": {"agent": "knowledge-consolidator", "run": "<run_id>"}
}'

# Documentation vs code conflict
python knowledge.py add-conflict --data '{
  "subject": "<Messaging_ent_id>",
  "claims": ["<fact_readme_rabbitmq_id>", "<fact_code_kafka_id>"],
  "type": "documentation_vs_code",
  "severity": "high",
  "status": "unresolved",
  "detected_by": {"agent": "documentation-discovery", "run": "<run_id>"}
}'
```

## Resolution (later phase)

Conflicts are resolved in Analysis phase by:
- Checking evidence strength (direct_observation > documentation > inference)
- Checking source freshness (recent code > old docs)
- Asking user (via discover-questions)
- Creating Decision (ADR) with rationale