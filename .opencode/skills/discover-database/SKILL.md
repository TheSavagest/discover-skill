---
name: discover-database
description: Discover database providers, schemas, entities, EF Core mappings, migrations, SQL, indexes and cache stores.
compatibility: opencode
---

# Database Discovery

Discover data stores from source configuration and available metadata.

## Inputs

- `run_id`: Current discovery run ID
- `dotnet_entities`: DbContext, entity entities from discover-dotnet
- `connection_strings`: From configuration (appsettings, env vars)

## Inspect

- Database providers (PostgreSQL, SQL Server, MySQL, SQLite, etc.)
- Connection configuration
- DbContext classes
- Entity classes (EF Core `[Entity]`, `[Table]`)
- Entity mappings (Fluent API, attributes)
- Migrations (`.cs` files in `Migrations/`)
- Raw SQL (`.sql` files, `FromSqlRaw`, `ExecuteSqlRaw`)
- Tables, views, stored procedures (from migrations or direct DB access)
- Indexes (from migrations or direct DB access)
- Redis/cache configuration

## Algorithm

1. Find all DbContext classes (inherit from `DbContext`)
2. For each DbContext:
   - Extract `DbSet<>` properties → entities
   - Scan `OnModelCreating` for Fluent API configuration
   - Scan entity classes for attributes
3. Parse migrations for schema operations
4. If direct DB access available (optional):
   - Inspect `INFORMATION_SCHEMA` / `pg_catalog`
   - Get actual table/column/index metadata
5. Detect Redis: `IDistributedCache`, `StackExchange.Redis`, `Microsoft.Extensions.Caching.StackExchangeRedis`

## Knowledge Operations

```bash
# Database entity
python knowledge.py add-entity --data '{
  "type": "database",
  "name": "PostgreSQL",
  "canonical_name": "postgresql://localhost:5432/myapp",
  "source": "<repository_src_id>",
  "location": {"path": "appsettings.json", "revision": "<rev>"},
  "metadata": {"provider": "Npgsql.EntityFrameworkCore.PostgreSQL", "connection_string_key": "DefaultConnection"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation", "static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "data-discovery", "skill": "discover-database", "run": "<run_id>"}
}'

# Table entity (from migration)
python knowledge.py add-entity --data '{
  "type": "table",
  "name": "Orders",
  "canonical_name": "public.Orders",
  "source": "<repository_src_id>",
  "location": {"path": "Migrations/20240101000000_InitialCreate.cs", "revision": "<rev>"},
  "metadata": {"schema": "public", "columns": [{"name": "Id", "type": "uuid", "nullable": false}, {"name": "Total", "type": "numeric", "nullable": false}]},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 0.95, "basis": ["static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "data-discovery", "skill": "discover-database", "run": "<run_id>"}
}'

# Fact: entity maps to table
python knowledge.py add-fact --data '{
  "subject": {"entity": "<Order_entity_ent_id>"},
  "predicate": "maps_to",
  "object": {"kind": "entity", "entity": "<Orders_table_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 0.95, "basis": ["static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "data-discovery", "skill": "discover-database", "run": "<run_id>"}
}'

# Fact: DbContext connects to database
python knowledge.py add-fact --data '{
  "subject": {"entity": "<AppDbContext_ent_id>"},
  "predicate": "connects_to",
  "object": {"kind": "entity", "entity": "<PostgreSQL_db_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation", "static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "data-discovery", "skill": "discover-database", "run": "<run_id>"}'
}
```