---
name: discover-evidence
description: Convert direct observations into provenance-backed evidence records with precise source locations and confidence.
compatibility: opencode
---

# Evidence Creation

Every important discovery claim must have evidence.

## Evidence Structure

```yaml
id: EVD-000001
source: SRC-000001
locator:
  type: code_range
  path: src/Orders/OrderService.cs
  line_start: 120
  line_end: 145
observation:
  type: text
  value: "class OrderService : IOrderService"
  raw_text: "class OrderService : IOrderService {\n    private readonly IOrderRepository _repo;\n    ..."
extracted:
  symbols: [OrderService, IOrderService]
  dependencies: [IOrderRepository, ILogger]
discovered_by:
  agent: backend-discovery
  skill: discover-dotnet
  run: RUN-000001
confidence: 1.0
```

## Locator Types

| Type | Fields | Example |
|------|--------|---------|
| code_range | path, line_start, line_end, revision | File lines 120-145 |
| git_commit | commit_hash, path | Commit abc123 |
| document_section | path, heading | README.md#Architecture |
| log_entry | timestamp, level, logger | 2026-08-29T10:00:00Z ERROR OrderService |
| metric_sample | metric_name, timestamp, labels | http_requests_total{handler="/api/orders"} |
| trace_span | trace_id, span_id, operation | abc123/def456 GET /api/orders |
| user_statement | question_id | Q-000001 |
| configuration_value | path, key | appsettings.json:ConnectionStrings:Default |

## Observation Types

| Type | Value Format | Use Case |
|------|--------------|----------|
| text | string | Code snippets, doc excerpts |
| structured | JSON object | Parsed AST, JSON config |
| ast_node | JSON (node type, children) | Roslyn/TS AST nodes |
| symbol | {name, kind, signature} | Class, method, interface |
| dependency | {from, to, type} | Import, reference, call |
| metric | {name, value, unit, labels} | Prometheus metrics |

## Confidence Guidelines

| Basis | Confidence |
|-------|------------|
| direct_observation | 1.0 |
| static_analysis | 0.95 |
| dynamic_observation | 0.9 |
| user_statement | 0.9 |
| documentation | 0.8 |
| inference | 0.7 |
| heuristic | 0.5 |

## Rules

1. Always include raw_text for human verification
2. Use precise locators - line ranges, not whole files
3. One evidence per observation - don't bundle multiple claims
4. Link to source - evidence.source must exist
5. Capture extractor - discovered_by.agent + skill + run