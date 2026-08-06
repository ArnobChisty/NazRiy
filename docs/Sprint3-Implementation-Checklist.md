# Sprint 3 Implementation Checklist

- [x] Cart and checkout component/API plan
- [x] Persistent cart: add, update, remove, quantity limits, navbar count
- [x] Responsive cart page and order summary
- [x] Responsive registration and login with validation and feedback
- [x] Registration, login, logout, and current-user endpoints
- [x] Required delivery-information form and validation
- [x] Loading, empty-cart, API-error, and order-success states
- [x] Cart, CartItem, Order, and OrderItem models, migration, and admin
- [x] Cart CRUD, transactional checkout, order history, backend totals, and stock validation APIs
- [x] Desktop, tablet, mobile, frontend build/lint, Django checks/migrations/tests

## Architecture

The React cart remains immediately responsive and persists in localStorage. Authentication uses a signed, expiring Django token. Checkout sends cart lines to Django, where products are locked in a database transaction, stock and options are revalidated, totals are recalculated from database prices, the order is saved, and stock is reduced atomically.
