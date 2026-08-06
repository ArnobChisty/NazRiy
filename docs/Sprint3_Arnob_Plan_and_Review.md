# Sprint 3 — Arnob Implementation Plan and Review

## Assigned scope (8 hours)

1. Review the Cart and Checkout wireframe and prepare the implementation plan — 1 hour
2. Implement frontend cart state management and persistence — 3 hours
3. Build the responsive Cart and Checkout page — 3 hours
4. Review, test, and finalize Sprint 3 integration — 1 hour

## Component plan

- `CartProvider`: owns cart state and persists it to `localStorage`.
- `useCart`: exposes cart actions and calculated values to pages and navigation.
- `ProductDetailsPage`: adds the selected product, size, colour and quantity.
- `Navbar`: displays the live total cart quantity and links to `/cart`.
- `CartPage`: displays cart lines, controls, totals, empty state and checkout handoff.
- `ProductArtwork`: reused for consistent product-image rendering.

## State and calculation rules

- Cart variants are keyed by product ID, size and colour.
- Adding the same variant increases its quantity.
- Quantity cannot be lower than 1 or higher than current product stock.
- Cart state is stored under `nazriy-cart-v1` and restored after refresh.
- Item count, subtotal, delivery and total are derived values, not persisted values.
- Delivery is ৳80 below ৳2,000 and free from ৳2,000.

## API requirements and dependencies

Arnob's frontend cart does not require the unfinished cart/order API to operate locally. Final server synchronization requires Maria's assigned endpoints:

- `GET /api/cart/`
- `POST /api/cart/items/`
- `PATCH /api/cart/items/{id}/`
- `DELETE /api/cart/items/{id}/`
- `POST /api/orders/`

Authentication and protected routes depend on Maria's authentication API. The delivery-information form and final loading/error/success states depend on Nazeefa's assigned frontend work.

## Implementation checklist

- [x] Product Details adds selected variants to the cart.
- [x] Navbar displays the total item quantity.
- [x] Cart survives browser refresh.
- [x] Cart lines show product, options, price and stock.
- [x] Quantity controls enforce stock limits.
- [x] Products can be removed and the cart can be cleared.
- [x] Subtotal, delivery and total update immediately.
- [x] Empty-cart state links back to products.
- [x] Desktop, tablet and mobile layouts are implemented.
- [x] Checkout handoff is visible without implementing teammates' scope.
- [ ] Authentication integration — assigned to Maria.
- [ ] Delivery form and order feedback states — assigned to Nazeefa.
- [ ] Cart/order database and APIs — assigned to Maria.

## Review notes

- Cart calculations use numeric product prices and recalculate on every state change.
- Malformed `localStorage` content safely falls back to an empty cart.
- Product data is stored with each line for offline refresh persistence; server reconciliation should replace this when the cart API is available.
- Final integration with authentication and orders must not trust frontend totals; the backend must recalculate prices and validate stock.

## Verification results

- `npm.cmd run lint` — passed.
- `npm.cmd run build` — passed; 31 modules compiled.
- Production preview `/cart` route — HTTP 200.
- Production preview `/products` route — HTTP 200.
- `python manage.py check` — passed against PostgreSQL.
- `python manage.py test` — 3 backend regression tests passed.

Arnob's four assigned tasks are complete. Full Sprint 3 integration remains intentionally incomplete until the authentication, delivery-form, cart/order-model and API tasks assigned to the other members are implemented.
