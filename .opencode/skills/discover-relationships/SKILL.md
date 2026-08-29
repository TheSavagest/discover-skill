---
name: discover-relationships
description: Resolve symbols and build code, project, API, component, data-flow and integration relationships.
compatibility: opencode
---

# Relationship Discovery

Build relationships from deterministic evidence. Do not invent relationships.

## Inputs

- `run_id`: Current discovery run ID
- All entities and facts from previous discovery phases

## Relationship Types to Build

| From Type | Relationship | To Type | Evidence Source |
|-----------|--------------|---------|-----------------|
| dotnet_project | depends_on | dotnet_project | ProjectReference |
| dotnet_project | depends_on | npm_project | PackageReference (JS interop) |
| class | depends_on | class/interface | Constructor injection, field type |
| class | implements | interface | `: IInterface` |
| class | inherits | class | `: BaseClass` |
| controller | implements_endpoint | endpoint | Route attribute + action |
| endpoint | implemented_by | controller | Controller action |
| react_component | uses | react_hook | Hook call in component |
| react_component | calls_endpoint | endpoint | API client call |
| react_hook | calls_endpoint | endpoint | API client call |
| api_client | calls_endpoint | endpoint | Fetch/axios call |
| service | calls | repository | Method call |
| service | uses | external_service | HttpClient call |
| db_context | connects_to | database | Connection string |
| entity | maps_to | table | EF Core mapping |
| migration | creates | table | Migration Up() |

## Algorithm

1. **Project → Project**: From `.csproj` ProjectReference, `package.json` dependencies
2. **Class → Class/Interface**: From Roslyn semantic analysis (constructor params, field types, method return types)
3. **Controller → Endpoint**: From ASP.NET route attributes
4. **Component → Hook**: From React component JSX/TSX (hook calls)
5. **Hook/Component → Endpoint**: From API client usage (fetch, axios, React Query)
6. **Service → Repository**: From method call analysis
7. **DbContext → Database**: From connection string + provider
8. **Entity → Table**: From EF Core mappings (attributes + Fluent API)
9. **Frontend → Backend**: Chain: Component → Hook → API Client → Endpoint → Controller → Service → Repository → DbContext → Database

## Deterministic Resolution

- Use Roslyn `SemanticModel` for C# symbol resolution
- Use TypeScript `Symbol` API for TS symbol resolution
- For cross-language (API): match by route path + HTTP method

## Knowledge Operations

```bash
# Relationship: project depends on project
python knowledge.py add-relationship --data '{
  "from": "<MyApp.Api_ent_id>",
  "type": "depends_on",
  "to": "<MyApp.Core_ent_id>",
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation", "static_analysis"]},
  "source_facts": ["<fact_id>"],
  "timestamps": {"created_at": "<now>"}
}'

# Relationship: component uses hook
python knowledge.py add-relationship --data '{
  "from": "<OrderTable_ent_id>",
  "type": "uses",
  "to": "<useOrders_ent_id>",
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["static_analysis"]},
  "source_facts": ["<fact_id>"],
  "timestamps": {"created_at": "<now>"}
}'

# Relationship: frontend -> endpoint -> controller -> service -> repository -> db
python knowledge.py add-relationship --data '{
  "from": "<useOrders_ent_id>",
  "type": "calls_endpoint",
  "to": "<GET_orders_endpoint_ent_id>",
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 0.95, "basis": ["static_analysis"]},
  "source_facts": ["<fact_id>"],
  "timestamps": {"created_at": "<now>"}
}'
```