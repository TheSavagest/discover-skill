---
name: discover-typescript
description: Discover TypeScript configuration, modules, imports, exports, types, interfaces and package dependencies.
compatibility: opencode
---

# TypeScript Discovery

Inspect TypeScript projects for structural information.

## Inputs

- `run_id`: Current discovery run ID
- `tsconfig_paths`: Paths to tsconfig.json files

## Inspect

- `package.json` - dependencies, devDependencies, scripts, workspaces
- `tsconfig.json` - compiler options, project references, paths, includes/excludes
- Source files (`.ts`, `.tsx`)
- Imports / exports
- Types, interfaces, enums, type aliases
- Module aliases (`paths` in tsconfig)
- Package dependencies (npm packages)
- Build configuration (Vite, Webpack, Turbo, esbuild, swc)

## Algorithm

1. For each `tsconfig.json`:
   - Parse compiler options
   - Resolve project references
   - Scan included files
2. For each source file:
   - Parse imports/exports using TypeScript AST
   - Extract type/interface declarations
3. Build module dependency graph
4. Map npm package usage to imports

## Deterministic Tooling

- TypeScript Compiler API (`ts.createProgram`, `ts.createSourceFile`)
- `ts-morph` for easier AST navigation
- JSON parsing for package.json, tsconfig.json

## Knowledge Operations

```bash
# npm project entity
python knowledge.py add-entity --data '{
  "type": "npm_project",
  "name": "admin-app",
  "canonical_name": "admin-app",
  "source": "<repository_src_id>",
  "location": {"path": "apps/admin/package.json", "revision": "<rev>"},
  "metadata": {
    "dependencies": {"react": "^18.2.0", "@reduxjs/toolkit": "^2.0.0"},
    "devDependencies": {"typescript": "^5.3.0", "vite": "^5.0.0"},
    "scripts": {"dev": "vite", "build": "tsc && vite build"}
  },
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation"]},
  "status": "active",
  "discovered_by": {"agent": "frontend-discovery", "skill": "discover-typescript", "run": "<run_id>"}
}'

# Interface entity
python knowledge.py add-entity --data '{
  "type": "interface",
  "name": "Order",
  "canonical_name": "features/orders/types/Order",
  "source": "<repository_src_id>",
  "location": {"path": "apps/admin/src/features/orders/types.ts", "start_line": 5, "end_line": 20, "revision": "<rev>"},
  "metadata": {"properties": [{"name": "id", "type": "string"}, {"name": "total", "type": "number"}]},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation", "static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "frontend-discovery", "skill": "discover-typescript", "run": "<run_id>"}
}'

# Fact: file imports module
python knowledge.py add-fact --data '{
  "subject": {"entity": "<OrderTable_tsx_ent_id>"},
  "predicate": "imports",
  "object": {"kind": "entity", "entity": "<useOrders_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "frontend-discovery", "skill": "discover-typescript", "run": "<run_id>"}
}'
```