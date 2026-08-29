---
name: discover-aspnet
description: Discover ASP.NET Core controllers, minimal APIs, middleware, filters, authentication, authorization, hosted services and HTTP clients.
compatibility: opencode
---

# ASP.NET Discovery

Discover ASP.NET Core specific components.

## Inputs

- `run_id`: Current discovery run ID
- `project_entities`: .NET project entities from discover-dotnet

## Inspect

- Controllers (`ControllerBase`, `[ApiController]`)
- Actions (methods with `[HttpGet]`, `[HttpPost]`, etc.)
- Routes (attribute routing, conventional routing)
- Minimal API mappings (`MapGet`, `MapPost`, `MapMethods`)
- Middleware (`UseMiddleware`, `Use*`, `IMiddleware`)
- Filters (`IActionFilter`, `IAsyncActionFilter`, `IExceptionFilter`)
- Endpoint metadata (`[ProducesResponseType]`, `[Authorize]`)
- Authentication schemes (`AddAuthentication`, `AddJwtBearer`)
- Authorization policies (`AddAuthorization`, `[Authorize(Policy=...)]`)
- Background services (`IHostedService`, `BackgroundService`)
- Hosted services
- HttpClient registrations (`AddHttpClient`, `AddTypedClient`)
- Configuration (`IOptions<>`, `IConfiguration`)

## Algorithm

1. For each ASP.NET project (has Microsoft.AspNetCore.App framework reference):
   - Scan for Controllers using Roslyn
   - Scan for Minimal API registrations in `Program.cs`
   - Scan for Middleware pipeline
   - Scan for Authentication/Authorization setup
   - Scan for HttpClient registrations
   - Map endpoints to implementations

## Knowledge Operations

```bash
# Controller entity
python knowledge.py add-entity --data '{
  "type": "controller",
  "name": "OrdersController",
  "canonical_name": "MyApp.Api.Controllers.OrdersController",
  "source": "<repository_src_id>",
  "location": {"path": "src/MyApp.Api/Controllers/OrdersController.cs", "start_line": 10, "end_line": 120, "revision": "<rev>"},
  "metadata": {"namespace": "MyApp.Api.Controllers", "base_type": "ControllerBase", "attributes": ["ApiController", "Route(\"api/[controller]\")"]},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation", "static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "backend-discovery", "skill": "discover-aspnet", "run": "<run_id>"}
}'

# Endpoint entity
python knowledge.py add-entity --data '{
  "type": "endpoint",
  "name": "GET /api/orders",
  "canonical_name": "MyApp.Api.Controllers.OrdersController.GetOrders",
  "source": "<repository_src_id>",
  "location": {"path": "src/MyApp.Api/Controllers/OrdersController.cs", "start_line": 25, "end_line": 35, "revision": "<rev>"},
  "metadata": {"http_method": "GET", "route": "api/orders", "controller": "OrdersController", "action": "GetOrders", "authentication": "required", "authorization_policies": []},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["direct_observation", "static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "backend-discovery", "skill": "discover-aspnet", "run": "<run_id>"}
}'

# Fact: endpoint implemented by controller
python knowledge.py add-fact --data '{
  "subject": {"entity": "<endpoint_ent_id>"},
  "predicate": "implemented_by",
  "object": {"kind": "entity", "entity": "<controller_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 1.0, "basis": ["static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "backend-discovery", "skill": "discover-aspnet", "run": "<run_id>"}
}'
```