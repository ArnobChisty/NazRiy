# Sprint 6 Integration and Release Report

## Release scope

NazRiy integrates the React/TypeScript storefront, Django REST API, PostgreSQL database, Supabase-compatible media storage, Django administration dashboard, manual bKash verification, and cash-on-delivery workflow.

## Verified customer journey

1. Browse the homepage and active catalogue products.
2. Search, filter, sort, and open product details.
3. Select valid size/colour options and add an in-stock product to the cart.
4. Register or sign in before checkout.
5. Submit delivery details; the server reloads product prices and locks stock before creating the order.
6. Choose COD or submit only a bKash transaction ID for administrator verification.
7. View order confirmation, payment state, order history, and fulfilment tracking.

## Release controls

- Inactive products are excluded from catalogue, featured, top-product, and detail APIs.
- Checkout totals are calculated from database prices in an atomic transaction.
- Stock is locked during checkout and restored once when an eligible order is cancelled.
- Order and payment endpoints enforce customer ownership.
- bKash references are unique and duplicate checkout/payment submissions are idempotent.
- Django production mode requires a strong secret, secure cookies, HTTPS, HSTS, explicit hosts/origins, PostgreSQL, persistent media, and JSON-only API rendering.
- CI verifies migration drift, PostgreSQL-backed backend tests, frontend coverage, lint, build, dependency audit, deployment checks, and static collection.

## Final local verification — 2026-08-03

| Check | Result |
| --- | --- |
| Django system check | Pass |
| Migration drift | Pass — no changes detected before Sprint 6 migration |
| Django tests | Pass — 35/35 including Sprint 6 release tests |
| Frontend tests | Pass — 22/22 |
| Frontend coverage | 93.1% statements, 88.46% branches, 83.33% functions, 96.15% lines |
| ESLint | Pass |
| Vite production build | Pass |
| npm audit | Pass — 0 vulnerabilities |
| PostgreSQL backup/restore rehearsal | Pass — 78 objects restored; catalogue and order/payment counts verified |

## External release gate

The repository contains a Render blueprint, production environment template, backup/restore tooling, and deployment runbook. A public release still requires an authorized hosting account, final domains, approved bKash merchant number, and production Supabase/PostgreSQL credentials. Those secrets must be entered directly in the hosting dashboard and never committed.
