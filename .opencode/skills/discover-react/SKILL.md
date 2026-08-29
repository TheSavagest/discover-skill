---
name: discover-react
description: Discover React applications, components, pages, routes, hooks, contexts, providers and state management.
compatibility: opencode
---

# React Discovery

Use TypeScript AST where possible (ts-morph, TypeScript Compiler API).

## Inputs

- `run_id`: Current discovery run ID
- `package_json_paths`: Paths to package.json files from discover-project

## Inspect

- React applications (entry points: `index.tsx`, `main.tsx`, `App.tsx`)
- Components (function components, class components)
- Pages (route-level components)
- Routes (React Router, TanStack Router, Next.js file-based routing)
- Hooks (custom hooks, `use*` functions)
- Contexts (`createContext`, `useContext`)
- Providers (`<Context.Provider>`)
- State management (Redux, Zustand, Jotai, Context, React Query)
- Forms (React Hook Form, Formik, native)
- Tests (`.test.tsx`, `.spec.tsx`, `__tests__/`)

## Algorithm

1. For each React project (has `react` in dependencies):
   - Parse `tsconfig.json` for project references, paths
   - Find entry points
   - Scan `.tsx` files for component declarations
   - Extract component hierarchy from JSX
   - Find hooks (functions starting with `use`)
   - Find contexts (`React.createContext`)
   - Find routing configuration
   - Find API client usage (`fetch`, `axios`, `ky`, React Query)
   - Build component → hook → API call relationships

## Deterministic Tooling

- `ts-morph` or TypeScript Compiler API for AST parsing
- Regex/glob for file discovery
- Package.json parsing for dependencies

## Knowledge Operations

```bash
# React app entity
python knowledge.py add-entity --data '{
  "type": "react_app",
  "name": "admin-app",
  "canonical_name": "admin-app",
  "source": "<repository_src_id>",
  "location": {"path": "apps/admin", "revision": "<rev>"},
  "metadata": {"framework": "react", "router": "react-router", "state": "redux-toolkit", "build": "vite"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation", "static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "frontend-discovery", "skill": "discover-react", "run": "<run_id>"}
}'

# Component entity
python knowledge.py add-entity --data '{
  "type": "react_component",
  "name": "OrderTable",
  "canonical_name": "features/orders/components/OrderTable",
  "source": "<repository_src_id>",
  "location": {"path": "apps/admin/src/features/orders/components/OrderTable.tsx", "start_line": 1, "end_line": 85, "revision": "<rev>"},
  "metadata": {"component_type": "function", "props_interface": "OrderTableProps", "hooks_used": ["useOrders", "useDeleteOrder"]},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation", "static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "frontend-discovery", "skill": "discover-react", "run": "<run_id>"}
}'

# Hook entity
python knowledge.py add-entity --data '{
  "type": "react_hook",
  "name": "useOrders",
  "canonical_name": "features/orders/hooks/useOrders",
  "source": "<repository_src_id>",
  "location": {"path": "apps/admin/src/features/orders/hooks/useOrders.ts", "start_line": 1, "end_line": 45, "revision": "<rev>"},
  "metadata": {"returns": "Order[]", "dependencies": ["ordersApi"]},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation", "static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "frontend-discovery", "skill": "discover-react", "run": "<run_id>"}
}'

# Fact: component uses hook
python knowledge.py add-fact --data '{
  "subject": {"entity": "<OrderTable_ent_id>"},
  "predicate": "uses",
  "object": {"kind": "entity", "entity": "<useOrders_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "frontend-discovery", "skill": "discover-react", "run": "<run_id>"}
}'

# Fact: hook calls API endpoint
python knowledge.py add-fact --data '{
  "subject": {"entity": "<useOrders_ent_id>"},
  "predicate": "calls_endpoint",
  "object": {"kind": "entity", "entity": "<GET_orders_endpoint_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 0.95, "basis": ["static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "frontend-discovery", "skill": "discover-react", "run": "<run_id>"}'
}
```