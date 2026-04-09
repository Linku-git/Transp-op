# Session 86 — Payment & Transport Pass Integration

> Previous: [[sessions/session-85|Session 85 — ERP Finance Export]] | Next: [[sessions/session-87|Session 87 — Performance Optimization]]

## Phase: 6 — Enterprise Integrations
## Prerequisites: [[sessions/session-04|Session 04]] completed
## Complexity: Medium

## Objective
Integrate with Stripe for billing management, Navigo API for Ile-de-France transit pass verification, and Edenred/Swile for NAT (Neobank Avantages Transport) benefits, providing a unified payment and transport pass management layer.

---

## Tasks
- [x] Create `backend/app/services/payment/stripe_client.py` with Stripe integration
- [x] Implement Stripe customer and subscription management
- [x] Implement Stripe webhook handling (payment success, failure, subscription updates)
- [x] Implement webhook signature verification for security
- [x] Integrate with Navigo API for Ile-de-France transit pass verification
- [x] Implement Navigo pass status checking and validation
- [x] Integrate with Edenred for NAT benefits management
- [x] Integrate with Swile for NAT benefits management
- [x] Create API endpoints for payment status management
- [x] Create API endpoints for transport pass management
- [x] Handle payment and pass data securely (PCI compliance considerations)

## Files to Create/Modify
- `backend/app/services/payment/stripe_client.py`
- `backend/app/services/payment/navigo_client.py`
- `backend/app/services/payment/edenred_client.py`
- `backend/app/services/payment/swile_client.py`
- `backend/app/api/v1/payment.py`
- `backend/app/api/v1/transport_pass.py`
- `backend/app/schemas/payment.py`
- `backend/app/schemas/transport_pass.py`
- `backend/app/core/config.py` (add payment and pass provider settings)
- `backend/tests/services/payment/test_stripe_client.py`
- `backend/tests/services/payment/test_navigo_client.py`
- `backend/tests/services/payment/test_edenred_client.py`
- `backend/tests/services/payment/test_swile_client.py`

## Tests
- [x] Test Stripe client creates customers and subscriptions correctly
- [x] Test Stripe webhook handling for payment_intent.succeeded event
- [x] Test Stripe webhook handling for payment_intent.payment_failed event
- [x] Test Stripe webhook handling for subscription update events
- [x] Test Stripe webhook signature verification rejects invalid signatures
- [x] Test Navigo API pass verification with mocked API
- [x] Test Navigo pass status checking returns correct status
- [x] Test Edenred NAT benefits integration with mocked API
- [x] Test Swile NAT benefits integration with mocked API
- [x] Test payment status API endpoints return correct data
- [x] Test transport pass management API endpoints

## Test Results
- Tests written: 21
- Tests passing: 21
- Tests failing: 0
- Coverage: Stripe (11), Navigo (4), Edenred (3), Swile (3)

## Acceptance Criteria
- Stripe integration handles customer creation, subscriptions, and webhook events
- Webhook signature verification prevents unauthorized webhook calls
- Navigo API integration verifies transit pass status for Ile-de-France
- Edenred integration manages NAT benefits correctly
- Swile integration manages NAT benefits correctly
- Payment status and transport pass APIs return accurate data
- All external API calls are mocked in tests
- Sensitive payment data is handled securely

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
