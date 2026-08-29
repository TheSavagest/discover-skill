---
name: discover-knowledge
description: Persist discovery entities, facts, evidence, relationships and snapshots while preserving provenance and history.
compatibility: opencode
---

# Knowledge Persistence

All persisted knowledge must preserve provenance. This skill wraps the `knowledge.py` CLI.

## Operations

### Add Entity
```bash
python knowledge.py add-entity --data '<entity_json>'
```

### Add Fact
```bash
python knowledge.py add-fact --data '<fact_json>'
```

### Add Evidence
```bash
python knowledge.py add-evidence --data '<evidence_json>'
```

### Add Source
```bash
python knowledge.py add-source --data '<source_json>'
```

### Add Relationship
```bash
python knowledge.py add-relationship --data '<relationship_json>'
```

### Add Question
```bash
python knowledge.py add-question --data '<question_json>'
```

### Add Conflict
```bash
python knowledge.py add-conflict --data '<conflict_json>'
```

### Add Run
```bash
python knowledge.py add-run --data '<run_json>'
```

### Query
```bash
# Query entities by type
python knowledge.py query-entities --filter type=class --filter status=active

# Query facts by subject
python knowledge.py query-facts --filter subject.entity=ENT-000001

# Query evidence by source
python knowledge.py query-evidence --filter source=SRC-000001
```

### Snapshot
```bash
python knowledge.py snapshot --run-id RUN-000001
```

### Validate
```bash
python knowledge.py validate
```

### Stats
```bash
python knowledge.py stats
```

## Rules

1. **Never write directly to `.ai/knowledge/current/*.yaml`** - always use this CLI
2. **Every add returns an ID** - capture and use for subsequent references
3. **Evidence first** - create evidence before facts that reference it
4. **Provenance chain** - every object must have `discovered_by` with agent, skill, run
5. **Confidence basis** - must include at least one basis type
6. **Status required** - all objects must have valid status from vocabulary

## Error Handling

- If validation fails, the CLI exits with code 1 and prints errors
- Skills MUST handle validation errors and report them
- Do not continue discovery with invalid data