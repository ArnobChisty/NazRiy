# NazRiy Deployment Readiness

## Backend

1. Copy `backend/.env.example` to `backend/.env` and replace every production value.
2. Use a long, unique `DJANGO_SECRET_KEY`; keep `DJANGO_DEBUG=false`.
3. Configure `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` with HTTPS origins only.
4. Configure PostgreSQL using the `DB_*` variables, then run:
   - `python manage.py migrate`
   - `python manage.py collectstatic --noinput`
   - `python manage.py check --deploy`
5. Persist `backend/media` in object storage or a durable mounted volume. The database stores image paths and metadata; uploaded files must not use ephemeral disk.
6. Serve Django through a production WSGI/ASGI server behind an HTTPS reverse proxy.

## Frontend

1. Set `VITE_API_URL=https://api.example.com/api` in the production build environment.
2. Run `npm ci`, `npm run lint`, and `npm run build`.
3. Deploy `frontend/dist` as static assets and configure the host to serve `index.html` for application routes such as `/account` and `/orders/123`.

## Release verification

- Run all backend tests and migration checks against the production database engine.
- Verify registration, login, session restoration, profile updates, password changes, checkout, order ownership, and staff status updates.
- Confirm media URLs, static assets, HTTPS redirects, secure cookies, backups, monitoring, and rollback procedures.
