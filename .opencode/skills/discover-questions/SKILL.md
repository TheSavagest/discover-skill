---
name: discover-questions
description: Identify unknowns and create prioritized questions when discovery cannot establish required facts.
compatibility: opencode
---

# Discovery Questions

Create a question when:
- Information is unavailable from any source
- Sources conflict and cannot be resolved
- A critical runtime fact cannot be established
- User context is required (business criticality, constraints)

## Question Categories

| Category | Example |
|----------|---------|
| runtime | "Which database is used in production?" |
| architecture | "Is the repository pattern intentional here?" |
| business | "Is the Orders endpoint business-critical?" |
| security | "What authentication scheme is required for /api/admin?" |
| performance | "What is the expected QPS for /api/orders?" |
| integration | "Which payment provider is used in production?" |
| deployment | "What is the acceptable downtime for deployments?" |
| data | "Can the Orders table schema be changed?" |
| constraint | "Is backward compatibility required for v1 API?" |
| ownership | "Who owns the PaymentIntegration service?" |

## Prioritization

1. **Critical** - Blocks discovery or implementation safety
2. **High** - Affects major architectural decisions
3. **Medium** - Clarifies important but non-blocking details
4. **Low** - Nice to have context

## Blocking Questions

Mark `blocking: true` when:
- Discovery cannot proceed without the answer
- Implementation would be unsafe without the answer
- Conflicting sources require human resolution

## Algorithm

1. After each discovery phase, check for gaps:
   - Entities without source
   - Facts without evidence
   - Conflicts without resolution
   - Critical runtime info missing (prod DB, deployed version, secrets)
2. Generate questions for each gap
3. Deduplicate related questions
4. Prioritize and present to user
5. Record answers as evidence → facts

## Knowledge Operations

```bash
# Create question
python knowledge.py add-question --data '{
  "question": "Which database is used in production?",
  "category": "runtime",
  "context": {"entities": ["<AppDbContext_ent_id>"]},
  "reason": "Repository configuration contains multiple database providers (PostgreSQL, SQL Server).",
  "priority": "critical",
  "blocking": true,
  "status": "open",
  "generated_by": {"agent": "discovery-orchestrator", "run": "<run_id>"}
}'

# After user answers
python knowledge.py add-evidence --data '{
  "source": "<user_src_id>",
  "locator": {"type": "user_statement"},
  "observation": {"type": "user_statement", "value": "Production uses PostgreSQL."},
  "discovered_by": {"agent": "user-discovery", "skill": "discover-questions", "run": "<run_id>"},
  "confidence": 0.95
}'

# Update question
python knowledge.py add-question --data '{
  "id": "Q-000001",
  "question": "Which database is used in production?",
  "category": "runtime",
  "context": {"entities": ["<AppDbContext_ent_id>"]},
  "reason": "Repository configuration contains multiple database providers.",
  "priority": "critical",
  "blocking": true,
  "status": "resolved",
  "answer": {"type": "user", "value": "Production uses PostgreSQL.", "evidence": ["<evidence_id>"], "answered_at": "<now>", "answered_by": "user"},
  "generated_by": {"agent": "discovery-orchestrator", "run": "<run_id>"}
}'

# Create fact from answer
python knowledge.py add-fact --data '{
  "subject": {"entity": "<AppDbContext_ent_id>"},
  "predicate": "connects_to",
  "object": {"kind": "entity", "entity": "<PostgreSQL_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 0.9, "basis": ["user_statement"]},
  "status": "active",
  "discovered_by": {"agent": "user-discovery", "skill": "discover-questions", "run": "<run_id>"}
}'
```