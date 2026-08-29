---
name: discover-integrations
description: Discover external services, SDKs, HTTP clients, webhooks, queues, brokers and third-party integrations.
compatibility: opencode
---

# Integration Discovery

Identify external boundaries from code configuration and usage.

## Inputs

- `run_id`: Current discovery run ID
- `dotnet_entities`: HttpClient, background services from discover-dotnet
- `typescript_entities`: fetch/axios calls from discover-typescript

## Search For

| Integration Type | Detection |
|------------------|-----------|
| HTTP clients | `HttpClient`, `AddHttpClient`, `IHttpClientFactory`, `fetch`, `axios`, `ky` |
| SDK packages | NuGet: `Stripe.net`, `AWSSDK.*`, `SendGrid`, `Twilio` / npm: `@stripe/stripe-js`, `aws-sdk`, `sendgrid` |
| URLs/Endpoints | Configuration: `appsettings.json`, `.env`, constants |
| Webhooks | Controllers with `[HttpPost]` + specific routes, signature verification |
| Message publishers | `IMessagePublisher`, `PublishAsync`, `RabbitMQ`, `Kafka`, `Azure Service Bus`, `MassTransit` |
| Message consumers | `IConsumer`, `@RabbitListener`, `@KafkaListener`, background services |
| Queues | `IQueueClient`, `QueueClient`, `CloudQueue` |
| Brokers | Connection strings, configuration sections |
| Storage | `BlobServiceClient`, `S3Client`, `Azure.Storage.Blobs`, `@aws-sdk/s3-client` |
| Identity | `AddAuthentication`, `AddJwtBearer`, `AddOpenIdConnect`, `IdentityServer`, `Auth0`, `Clerk` |
| Third-party APIs | Any `HttpClient` with base address to external domain |

## Algorithm

1. Scan for HTTP client registrations and usages
2. Scan for known SDK package references
3. Extract base addresses, API keys from configuration
4. Find webhook endpoints (POST + specific path patterns)
5. Find message broker connections
6. For each integration, create entity with type `external_service`

## Knowledge Operations

```bash
# External service entity
python knowledge.py add-entity --data '{
  "type": "external_service",
  "name": "Stripe",
  "canonical_name": "stripe.com",
  "source": "<repository_src_id>",
  "location": {"path": "appsettings.json", "revision": "<rev>"},
  "metadata": {"category": "payment", "sdk": "Stripe.net", "base_url": "https://api.stripe.com"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 0.9, "basis": ["direct_observation", "static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "integration-discovery", "skill": "discover-integrations", "run": "<run_id>"}
}'

# Fact: service uses external service
python knowledge.py add-fact --data '{
  "subject": {"entity": "<PaymentService_ent_id>"},
  "predicate": "uses",
  "object": {"kind": "entity", "entity": "<Stripe_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 0.9, "basis": ["static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "integration-discovery", "skill": "discover-integrations", "run": "<run_id>"}
}'

# Fact: webhook endpoint
python knowledge.py add-fact --data '{
  "subject": {"entity": "<StripeWebhookController_ent_id>"},
  "predicate": "implements_endpoint",
  "object": {"kind": "entity", "entity": "<stripe_webhook_endpoint_ent_id>"},
  "evidence": ["<evidence_id>"],
  "confidence": {"score": 0.95, "basis": ["static_analysis"]},
  "status": "active",
  "discovered_by": {"agent": "integration-discovery", "skill": "discover-integrations", "run": "<run_id>"}
}'
```

## Important

Do not infer business criticality without evidence. Record as Question if unknown.