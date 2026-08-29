# Knowledge Layer - Project Discovery System

## Structure

```
.ai/knowledge/
├── current/                    # Materialized current state (append-only YAML)
│   ├── entities.yaml
│   ├── facts.yaml
│   ├── evidence.yaml
│   ├── sources.yaml
│   ├── relationships.yaml
│   ├── questions.yaml
│   ├── conflicts.yaml
│   └── runs.yaml
├── history/                    # Immutable snapshots per run
│   └── RUN-XXXXXX/
│       ├── entities.yaml
│       ├── facts.yaml
│       └── ...
├── schemas/                    # JSON Schema definitions
│   ├── entity.yaml
│   ├── source.yaml
│   ├── evidence.yaml
│   ├── fact.yaml
│   ├── relationship.yaml
│   ├── question.yaml
│   ├── conflict.yaml
│   ├── discovery_run.yaml
│   └── vocabulary.yaml         # Controlled vocabularies
└── cache/                      # Parsed AST cache (file_path + content_hash)
```

## Schemas Created

All 8 core entity types with JSON Schema validation:
- **Entity** - Code/project entities with location, metadata, evidence
- **Source** - Information sources (files, git, runtime, user, etc.)
- **Evidence** - Direct observations with precise locators
- **Fact** - Normalized (subject, predicate, object) statements
- **Relationship** - Graph projections from facts
- **Question** - Explicit unknowns with priority/blocking status
- **Conflict** - Contradictory claims from different sources
- **DiscoveryRun** - Metadata about each discovery execution

## CLI Usage (requires Python 3.8+)

```bash
# Install dependencies
pip install jsonschema pyyaml

# Add a source
python knowledge.py add-source --data '{"type": "repository_file", "uri": "file://src/Orders/OrderService.cs", "access": {"available": true}}'

# Add an entity
python knowledge.py add-entity --data '{
  "type": "class",
  "name": "OrderService",
  "canonical_name": "MyApp.Orders.OrderService",
  "source": "SRC-000001",
  "location": {"path": "src/Orders/OrderService.cs", "start_line": 12, "end_line": 754},
  "evidence": ["EVD-000001"],
  "confidence": {"score": 1.0, "basis": ["direct_observation"]},
  "status": "active",
  "discovered_by": {"agent": "backend-discovery", "skill": "scan-csharp-types", "run": "RUN-000001"}
}'

# Add evidence
python knowledge.py add-evidence --data '{
  "source": "SRC-000001",
  "locator": {"type": "code_range", "path": "src/Orders/OrderService.cs", "line_start": 120, "line_end": 145},
  "observation": {"type": "text", "value": "class OrderService : IOrderService"},
  "discovered_by": {"agent": "backend-discovery", "skill": "scan-csharp-types", "run": "RUN-000001"},
  "confidence": 1.0
}'

# Add a fact
python knowledge.py add-fact --data '{
  "subject": {"entity": "ENT-000001"},
  "predicate": "implements",
  "object": {"kind": "entity", "entity": "ENT-000002"},
  "evidence": ["EVD-000001"],
  "confidence": {"score": 1.0, "basis": ["direct_observation"]},
  "status": "active",
  "discovered_by": {"agent": "backend-discovery", "skill": "scan-csharp-types", "run": "RUN-000001"}
}'

# Query
python knowledge.py query-entities --filter type=class --filter status=active
python knowledge.py query-facts --filter subject.entity=ENT-000001
python knowledge.py query-evidence --id EVD-000001

# Snapshot
python knowledge.py snapshot --run-id RUN-000001

# Validate all
python knowledge.py validate

# Stats
python knowledge.py stats
```

## Key Principles

1. **Single Writer** - Only this CLI modifies `.ai/knowledge/`. Agents/skills call it via subprocess.
2. **Immutable Observations** - Facts are never overwritten; new versions supersede old.
3. **Provenance Chain** - Every fact → evidence → source → file/line/revision.
4. **Controlled Vocabulary** - Entity types and predicates defined in `vocabulary.yaml`.
5. **Confidence Basis** - Explicit tracking of how confident we are and why.

## Next Steps

1. Install Python: `winget install Python.Python.3.11`
2. Run `pip install -r requirements.txt`
3. Test with `python knowledge.py stats`
4. Begin implementing discovery skills that call this CLI