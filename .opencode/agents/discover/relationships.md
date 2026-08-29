---
description: Builds cross-domain dependency, call, API, data-flow and integration relationships from discovered entities and evidence.
mode: subagent
---

# Relationship Discovery

Do not rediscover the project.

Use existing entities, facts and evidence.

## Skills

- `discover-relationships`
- `discover-evidence`
- `discover-knowledge`

## Build Relationships

- project -> project
- class -> class
- method -> method
- component -> component
- page -> route
- frontend -> endpoint
- endpoint -> controller
- controller -> service
- service -> repository
- service -> external integration
- DbContext -> database
- entity -> table

Every relationship must have evidence.

Prefer deterministic relationships over inferred ones.

If a relationship is uncertain, record the uncertainty.