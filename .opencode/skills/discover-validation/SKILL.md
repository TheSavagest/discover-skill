---
name: discover-validation
description: Validate discovery results for schema correctness, evidence coverage, duplicate entities, unsupported facts and inconsistent references.
compatibility: opencode
---

# Discovery Validation

Validate every discovery result before persistence.

## Validation Rules

### Reject If:
- Missing required IDs
- Missing source reference
- Facts without evidence
- Invalid entity references (referenced entity doesn't exist)
- Invalid relationship endpoints
- Evidence without source
- Duplicate entities (same canonical_name + location)
- Duplicate facts (same subject + predicate + object)

### Schema Validation
Use JSON Schema from `.ai/knowledge/schemas/`:
- entity.yaml
- fact.yaml
- evidence.yaml
- source.yaml
- relationship.yaml
- question.yaml
- conflict.yaml
- discovery_run.yaml

### Cross-Reference Validation
```python
def validate_cross_references(kb):
    errors = []
    
    # Facts reference valid entities
    for fact in kb.query_facts():
        subj = fact["subject"].get("entity")
        if subj and not kb.get_by_id("entity", subj):
            errors.append(f"Fact {fact['id']} references missing entity {subj}")
        
        obj = fact["object"]
        if obj.get("kind") == "entity":
            if not kb.get_by_id("entity", obj["entity"]):
                errors.append(f"Fact {fact['id']} references missing object entity {obj['entity']}")
    
    # Relationships reference valid entities
    for rel in kb.query_relationships():
        if not kb.get_by_id("entity", rel["from"]):
            errors.append(f"Relationship {rel['id']} from missing entity {rel['from']}")
        if not kb.get_by_id("entity", rel["to"]):
            errors.append(f"Relationship {rel['id']} to missing entity {rel['to']}")
    
    # Evidence references valid sources
    for ev in kb.query_evidence():
        if not kb.get_by_id("source", ev["source"]):
            errors.append(f"Evidence {ev['id']} references missing source {ev['source']}")
    
    return errors
```

## Confidence Validation

- Score must be 0.0-1.0
- Basis must be non-empty array from vocabulary
- For structural facts (code structure), basis must include `direct_observation` or `static_analysis`
- Heuristic-only basis requires manual review flag

## Usage

```bash
# Validate all
python knowledge.py validate

# Validate specific run
python knowledge.py query-runs --id RUN-000001
# Check status == "completed" or "audited"
```

## Integration

Run validation:
1. After each skill completes (skill-level validation)
2. After each agent completes (agent-level validation)
3. Before snapshot (run-level validation)
4. In discover-audit (comprehensive validation)

Do not repair uncertain semantic claims by guessing - create questions instead.