---
name: discover-project
description: Discover repository structure, technologies, project boundaries, build systems, configuration, tests and generated files.
compatibility: opencode
---

# Project Discovery

Inspect the repository systematically to build the project inventory.

## Inputs

- `run_id`: Current discovery run ID
- `project_root`: Repository root path
- `source_ids`: Available source IDs from discover-source

## Outputs

Creates entities and facts for:
- Repository root
- Source directories
- Test directories
- .NET solutions (`.sln`, `.slnx`)
- .NET projects (`.csproj`)
- JavaScript/TypeScript applications (`package.json`)
- Package managers (NuGet, npm, yarn, pnpm)
- Build systems (MSBuild, Vite, Webpack, Turbo, Nx)
- Configuration files (`appsettings.json`, `web.config`, `.env`, etc.)
- Generated code directories
- Scripts (PowerShell, Bash, Batch)
- Docker files
- Infrastructure files
- Documentation
- Entry points

## Algorithm

1. **Filesystem scan** - Walk directory tree, categorize by extension/name patterns
2. **Solution detection** - Find `.sln`/`.slnx`, parse for project references
3. **Project detection** - Find `.csproj`, parse for TargetFramework, PackageReferences, ProjectReferences
4. **JS/TS detection** - Find `package.json`, parse for dependencies, scripts, workspaces
5. **Config detection** - Find known config file patterns
6. **Entry point detection** - Find `Program.cs`, `Main`, `index.tsx`, `main.tsx`, `App.tsx`
7. **Generated code detection** - Identify `obj/`, `bin/`, `node_modules/`, `.generated/`, `*.g.cs`, `*.designer.cs`

## Deterministic Tooling

- `find` / `Get-ChildItem` for file discovery
- XML parsing for `.sln`, `.csproj` (not LLM)
- JSON parsing for `package.json`, `tsconfig.json` (not LLM)

## Knowledge Operations

```bash
# Repository entity
python knowledge.py add-entity --data '{
  "type": "project",
  "name": "<repo_name>",
  "canonical_name": "<repo_name>",
  "source": "<repository_src_id>",
  "location": {"path": "<repo_root>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation"]},
  "status": "active",
  "discovered_by": {"agent": "project-discovery", "skill": "discover-project", "run": "<run_id>"}
}'

# Solution entity
python knowledge.py add-entity --data '{
  "type": "solution",
  "name": "MyApp",
  "canonical_name": "MyApp",
  "source": "<repository_src_id>",
  "location": {"path": "MyApp.slnx", "revision": "<rev>"},
  "metadata": {"projects": ["MyApp.Api", "MyApp.Core", ...]},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation"]},
  "status": "active",
  "discovered_by": {"agent": "project-discovery", "skill": "discover-project", "run": "<run_id>"}
}'

# Fact: solution contains project
python knowledge.py add-fact --data '{
  "subject": {"entity": "<solution_ent_id>"},
  "predicate": "contains",
  "object": {"kind": "entity", "entity": "<project_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation"]},
  "status": "active",
  "discovered_by": {"agent": "project-discovery", "skill": "discover-project", "run": "<run_id>"}
}'
```