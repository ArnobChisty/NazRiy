# NazRiy API Reference

Base path: `/api`. Protected endpoints require `Authorization: Token <signed-token>`.

| Method | Path | Access | Purpose |
| --- | --- | --- | --- |
| GET | `/health/` | Public | Safe database/storage health status |
| GET | `/products/` | Public | Active products with search/filter/sort query parameters |
| GET | `/products/featured/` | Public | Active featured products |
| GET | `/products/<slug>/` | Public | Active product details |
| GET | `/categories/` | Public | Categories |
| GET | `/banners/` | Public | Active scheduled banners |
| GET | `/top-products/` | Public | Active homepage placements for active products |
| GET | `/navigation-links/` | Public | Active navigation links |
| POST | `/auth/register/` | Public | Create customer account |
| POST | `/auth/login/` | Public | Issue signed token |
| POST | `/auth/logout/` | Customer | End local session workflow |
| GET | `/auth/me/` | Customer | Current user |
| PATCH | `/auth/profile/` | Customer | Update profile |
| POST | `/auth/password/change/` | Customer | Change password |
| GET/POST | `/cart/` | Customer | Read or add/update cart items |
| PATCH/DELETE | `/cart/<id>/` | Owner | Update or remove a cart item |
| POST | `/orders/checkout/` | Customer | Atomic idempotent checkout with server totals |
| GET | `/orders/` | Customer | Own orders |
| GET | `/orders/<id>/` | Owner | Own order detail |
| POST | `/orders/<id>/payment/` | Owner | Submit/cancel manual bKash verification request |

Checkout accepts delivery fields, `payment_method`, a UUID `idempotency_key`, and item identifiers/options/quantities. Client prices and totals are ignored. The bKash endpoint accepts `action`, UUID `request_id`, and—only for submission—an 8–32 character transaction ID. It never accepts a PIN or OTP.
