---
name: discover-audit
description: Audit the discovery knowledge base for missing evidence, duplicates, conflicts, stale facts, orphan entities and incomplete coverage.
compatibility: opencode
---

# Discovery Audit

Check the knowledge base for quality issues before marking discovery complete.

## Checks

### 1. Evidence Coverage
- Every entity has ≥1 evidence
- Every fact has ≥1 evidence
- Every relationship has ≥1 evidence
- Evidence references valid sources

### 2. Provenance Chain
- Fact → Evidence → Source → File/Location
- No orphan evidence (evidence not referenced by any fact/entity)
- No orphan facts (facts not referenced by any relationship)

### 3. Duplicates
- Entities with same canonical_name + location
- Facts with same subject + predicate + object
- Relationships with same from + type + to

### 4. Conflicts
- All detected conflicts have Conflict entity
- No unresolved critical conflicts

### 5. Stale Facts
- Facts from sources older than 30 days (configurable)
- Facts where source file has changed (git diff)
- Mark as `stale` status

### 6. Orphan Entities
- Entities not connected by any relationship
- Entities not referenced by any fact

### 7. Coverage Gaps
- No backend entities found (expected for C# project)
- No frontend entities found (expected for React project)
- No API endpoints found
- No database entities found
- No Git history (if .git exists)

### 8. Analysis Contamination
- No facts with predicate like "is_too_large", "has_bad_architecture"
- No entities with type like "problem", "issue", "smell"
- No facts with confidence.basis containing "heuristic" only for structural facts

## Algorithm

```python
def audit(kb):
    errors = []
    warnings = []
    
    # 1. Evidence coverage
    for entity in kb.query_entities():
        if not entity.get("evidence"):
            errors.append(f"Entity {entity['id']} has no evidence")
    
    for fact in kb.query_facts():
        if not fact.get("evidence"):
            errors.append(f"Fact {fact['id']} has no evidence")
    
    # 2. Provenance
    for fact in kb.query_facts():
        for ev_id in fact["evidence"]:
            if not kb.get_by_id("evidence", ev_id):
                errors.append(f"Fact {fact['id']} references missing evidence {ev_id}")
    
    # 3. Duplicates
    # ... check for duplicate entities, facts, relationships
    
    # 4. Conflicts
    conflicts = kb.query_conflicts({"status": "unresolved"})
    for c in conflicts:
        if c["severity"] in ["critical", "high"]:
            errors.append(f"Unresolved {c['severity']} conflict: {c['id']}")
    
    # 5. Stale
    # ... check source timestamps vs git log
    
    # 6. Orphans
    # ... find entities with no relationships/facts
    
    # 7. Coverage
    if not kb.query_entities({"type": ["controller", "service", "class"]}):
        warnings.append("No backend entities found")
    
    # 8. Analysis contamination
    for fact in kb.query_facts():
        if fact["predicate"] in ["is_too_large", "has_bad_architecture", "is_smell"]:
            errors.append(f"Analysis finding stored as fact: {fact['id']}")
    
    return {"errors": errors, "warnings": warnings, "passed": len(errors) == 0}
```

## Knowledge Operations

```bash
# Run validation
python knowledge.py validate

# Mark stale
python knowledge.py mark-stale --type fact --id FACT-000123

# Query for audit
python knowledge.py query-entities --filter status=active
python knowledge.py query-facts --filter status=active
python knowledge.py query-conflicts --filter status=unresolved
```

## Output

Produce audit report:
```yaml
audit:
  run_id: RUN-000001
  timestamp: "2026-08-29T10:30:00Z"
  errors:
    - "Entity ENT-000042 has no evidence"
    - "Unresolved critical conflict: CON-000001"
  warnings:
    - "No database entities found"
    - "Entity ENT-000100 is orphan (no relationships)"
  passed: false
  statistics:
    entities_total: 1832
    entities_with_evidence: 1820
    facts_total: 5214
    facts_with_evidence: 5198
    conflicts_unresolved: 3
    stale_facts: 12
```

Discovery cannot be marked complete while critical errors remain.