---
name: discover-semantic
description: Use semantic reasoning to classify discovered code entities, identify domain terminology and normalize project concepts without making quality judgments.
compatibility: opencode
---

# Semantic Discovery

Use semantic reasoning ONLY after deterministic discovery. Do not make quality judgments.

## Allowed Operations

- Classify component role (controller, service, repository, component, page, hook)
- Identify likely domain concepts (Order, Payment, User, Product)
- Normalize terminology (OrderService, OrderManager, OrderHandler → Order Service)
- Summarize modules (Orders module handles order lifecycle)
- Identify explicit business terminology from code (class names, comments, constants)

## NOT Allowed

- Architectural criticism ("this violates SRP")
- Refactoring recommendations ("should extract interface")
- Quality scoring ("complexity: high")
- Performance judgments ("this is slow")
- Security judgments ("this is vulnerable")
- Maintainability assessments ("hard to maintain")

## Algorithm

1. Receive deterministic entities/facts from other skills
2. For each entity without semantic classification:
   - Analyze name, namespace, attributes, base types
   - Infer role from patterns (Controller suffix, Service suffix, Repository suffix)
   - Infer domain from namespace (MyApp.Orders → Orders domain)
3. Assign classification with confidence
4. Create/Update entity metadata

## Classification Patterns

| Pattern | Classification | Confidence |
|---------|----------------|------------|
| `*Controller` + `[ApiController]` | controller | 0.95 |
| `*Service` + implements `I*Service` | application_service | 0.9 |
| `*Repository` + implements `I*Repository` | repository | 0.9 |
| `*Handler` + `IRequestHandler` | mediator_handler | 0.85 |
| `*Validator` + `AbstractValidator` | validator | 0.9 |
| `*Middleware` + `IMiddleware` | middleware | 0.9 |
| `use*` function returning state | react_hook | 0.9 |
| `createContext` + Provider | react_context | 0.95 |
| Route-level component | react_page | 0.8 |
| Reusable UI piece | react_component | 0.8 |

## Knowledge Operations

```bash
# Update entity with semantic classification
python knowledge.py add-fact --data '{
  "subject": {"entity": "<OrderService_ent_id>"},
  "predicate": "has_role",
  "object": {"kind": "value", "value": "application_service"},
  "evidence": ["<semantic_evidence_id>"],
  "confidence": {"score": 0.9, "basis": ["inference"]},
  "status": "active",
  "discovered_by": {"agent": "backend-discovery", "skill": "discover-semantic", "run": "<run_id>"}
}'

# Domain concept fact
python knowledge.py add-fact --data '{
  "subject": {"entity": "<Order_entity_ent_id>"},
  "predicate": "represents_domain",
  "object": {"kind": "value", "value": "Order"},
  "evidence": ["<semantic_evidence_id>"],
  "confidence": {"score": 0.85, "basis": ["inference"]},
  "status": "active",
  "discovered_by": {"agent": "backend-discovery", "skill": "discover-semantic", "run": "<run_id>"}'
}
```

## Uncertainty Handling

If uncertain:
- Lower confidence (0.6-0.7)
- Add `inference` to basis
- Create Question for user clarification
- Do not assert as fact