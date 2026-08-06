# Sprint 5 Automated Testing Strategy

## Objective

Increase confidence in NazRiy releases by testing critical business rules in isolation, validating API workflows, and running the same deterministic checks in GitHub Actions.

## Test pyramid

| Layer | Scope | Tools |
| --- | --- | --- |
| Unit | Cart keys/quantity rules, payment feedback, token and state helpers, model validation | Vitest, Django TestCase |
| Component | Authentication, cart persistence, protected routes, profile, checkout, payment, order feedback | React Testing Library, jsdom |
| API/integration | Checkout totals, stock locking, ownership, idempotency, payment transitions, cancellation | DRF APITestCase |
| UAT | Browse → cart → login → checkout → bKash transaction submission → verification → tracking | Manual acceptance checklist |

## Critical risks and controls

- **Duplicate checkout:** client-generated UUID plus unique backend idempotency key.
- **Incorrect totals:** totals are recalculated from locked database products, never trusted from the browser.
- **Overselling:** checkout validates stock inside a database transaction and decrements locked products.
- **Payment/order inconsistency:** bKash references remain pending until administrator verification; cancellation cancels the order and restores inventory.
- **Unauthorised access:** signed-token authentication and per-user order/payment lookups.
- **Expired sessions:** authentication restoration clears rejected tokens and protected routes redirect.
- **Frontend regressions:** component tests, TypeScript build, ESLint, and coverage threshold.

## Coverage target

Critical frontend business modules (`cart.ts` and `payment.ts`) must maintain at least:

- 80% statements
- 80% lines
- 80% functions
- 75% branches

Backend payment, stock, permission, ownership, invalid-request, authentication, admin, banner, category, navigation, and order regression tests run together.

## Determinism

- No live payment provider is contacted.
- Tests use SQLite test databases, fixed products, isolated users, and mocked browser APIs.
- Each test clears local and session storage.
- bKash transaction IDs are format-validated, ownership-protected, duplicate-protected, and verified by an administrator against the merchant statement.

## Commands

```powershell
cd backend
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py test store --noinput

cd ..\frontend
npm run test:coverage
npm run lint
npm run build
```
