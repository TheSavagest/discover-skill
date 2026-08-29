---
name: discover-api
description: Discover HTTP endpoints, API contracts, OpenAPI specifications, authentication and API consumers.
compatibility: opencode
---

# API Discovery

Build an endpoint registry connecting frontend consumers to backend implementations.

## Inputs

- `run_id`: Current discovery run ID
- `backend_entities`: Controller, minimal API entities from discover-aspnet
- `frontend_entities`: API client, hook entities from discover-react
- `openapi_paths`: Paths to OpenAPI/Swagger files

## Inspect

- Endpoints (HTTP method, path, controller/action)
- Request/response models
- Authentication requirements
- Authorization policies
- API versioning
- OpenAPI/Swagger documents
- Frontend consumers (API client calls)
- External consumers (when discoverable)

## Algorithm

1. Collect all backend endpoints from discover-aspnet
2. Parse OpenAPI/Swagger if available
3. Scan frontend for API calls (fetch, axios, React Query, RTK Query)
4. Match frontend calls to backend endpoints by path/method
5. Build complete endpoint registry with consumers

## Knowledge Operations

```bash
# Endpoint entity (from backend)
python knowledge.py add-entity --data '{
  "type": "endpoint",
  "name": "POST /api/orders",
  "canonical_name": "api.orders.create",
  "source": "<repository_src_id>",
  "location": {"path": "src/MyApp.Api/Controllers/OrdersController.cs", "start_line": 40, "end_line": 55, "revision": "<rev>"},
  "metadata": {
    "http_method": "POST",
    "route": "api/orders",
    "controller": "OrdersController",
    "action": "Create",
    "request_type": "CreateOrderRequest",
    "response_type": "OrderResponse",
    "authentication": "required",
    "authorization_policies": ["RequireAdminRole"]
  },
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation", "static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "api-discovery", "skill": "discover-api", "run": "<run_id>"}
}'

# Fact: frontend consumer calls endpoint
python knowledge.py add-fact --data '{
  "subject": {"entity": "<ordersApi_ent_id>"},
  "predicate": "calls_endpoint",
  "object": {"kind": "entity", "entity": "<POST_orders_endpoint_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 0.95, "basis": ["static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "api-discovery", "skill": "discover-api", "run": "<run_id>"}
}'

# Fact: endpoint implemented by controller
python knowledge.py add-fact --data '{
  "subject": {"entity": "<POST_orders_endpoint_ent_id>"},
  "predicate": "implemented_by",
  "object": {"kind": "entity", "entity": "<OrdersController_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "api-discovery", "skill": "discover-api", "run": "<run_id>"}'
}
```