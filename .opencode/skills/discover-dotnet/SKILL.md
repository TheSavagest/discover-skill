---
name: discover-dotnet
description: Discover C# and .NET solution structure, projects, packages, types, references, DI, configuration and tests.
compatibility: opencode
---

# .NET Discovery

Use deterministic tooling (Roslyn, MSBuild, dotnet CLI) whenever possible.

## Inputs

- `run_id`: Current discovery run ID
- `solution_path`: Path to `.sln` or `.slnx`
- `project_root`: Repository root

## Inspect

- `.sln` / `.slnx` - Solution structure, project references
- `.csproj` - TargetFramework, PackageReferences, ProjectReferences, FrameworkReferences
- Namespaces
- Types (classes, interfaces, records, structs, enums)
- Methods, properties
- Attributes
- Inheritance chains
- Interface implementations
- Dependency Injection registrations
- Configuration (IOptions, appsettings)
- Tests (xUnit, NUnit, MSTest projects)

## Deterministic Skills (prefer over LLM)

| Operation | Tool |
|-----------|------|
| Parse solution | `dotnet sln list` or MSBuild API |
| Parse csproj | `dotnet msbuild -pp` or XML parsing |
| Find types | Roslyn / `dotnet-ast` / `csharp-ls` |
| Find DI registrations | Roslyn analyzer on `Program.cs`, `Startup.cs` |
| Find configuration | Roslyn on `IOptions<>` bindings |
| Find tests | ProjectReference to test frameworks |

## Algorithm

1. Parse solution for project list
2. For each project:
   - Parse `.csproj` for metadata
   - Scan source files for types using Roslyn
   - Extract DI registrations from `Program.cs` / `Startup.cs`
   - Extract configuration bindings
3. Build project dependency graph from ProjectReferences
4. Build package dependency graph from PackageReferences

## Knowledge Operations

```bash
# Project entity
python knowledge.py add-entity --data '{
  "type": "dotnet_project",
  "name": "MyApp.Api",
  "canonical_name": "MyApp.Api",
  "source": "<repository_src_id>",
  "location": {"path": "src/MyApp.Api/MyApp.Api.csproj", "revision": "<rev>"},
  "metadata": {
    "target_frameworks": ["net8.0"],
    "package_references": ["Microsoft.AspNetCore.OpenApi", "Swashbuckle.AspNetCore"],
    "project_references": ["MyApp.Core", "MyApp.Infrastructure"]
  },
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation", "static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "backend-discovery", "skill": "discover-dotnet", "run": "<run_id>"}
}'

# Class entity
python knowledge.py add-entity --data '{
  "type": "class",
  "name": "OrderService",
  "canonical_name": "MyApp.Orders.OrderService",
  "source": "<repository_src_id>",
  "location": {"path": "src/MyApp.Core/Orders/OrderService.cs", "start_line": 12, "end_line": 754, "revision": "<rev>"},
  "metadata": {"namespace": "MyApp.Orders", "language": "csharp"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation", "static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "backend-discovery", "skill": "discover-dotnet", "run": "<run_id>"}
}'

# Fact: class implements interface
python knowledge.py add-fact --data '{
  "subject": {"entity": "<OrderService_ent_id>"},
  "predicate": "implements",
  "object": {"kind": "entity", "entity": "<IOrderService_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "backend-discovery", "skill": "discover-dotnet", "run": "<run_id>"}
}'

# Fact: DI registration
python knowledge.py add-fact --data '{
  "subject": {"entity": "<IOrderService_ent_id>"},
  "predicate": "configured_by",
  "object": {"kind": "entity", "entity": "<Program_cs_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 0.95, "basis": ["static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "backend-discovery", "skill": "discover-dotnet", "run": "<run_id>"}
}'
```