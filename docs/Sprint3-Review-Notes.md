# Sprint 3 Review Notes

## Completed flow

Users can register, log in, keep a cart through refreshes, update and remove lines, see correct totals, enter validated delivery information, submit a protected checkout request, and receive success or error feedback. Orders and immutable order-line prices are stored in Django. Stock is locked and validated during checkout.

## API

- `POST /api/auth/register/`, `POST /api/auth/login/`, `POST /api/auth/logout/`, `GET /api/auth/me/`
- `GET|POST /api/cart/`, `PATCH|DELETE /api/cart/:id/`
- `POST /api/orders/checkout/`, `GET /api/orders/`

## Verification

- Frontend TypeScript production build
- ESLint
- Django system check and migration consistency
- Product, authentication, cart, checkout, stock, totals, and protected-route tests
- Responsive verification at desktop, tablet, and mobile widths
