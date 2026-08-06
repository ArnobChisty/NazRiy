# Production Deployment and Operations Guide

## Deploy with the included Render blueprint

1. Push the reviewed `main` branch to GitHub.
2. In Render, create a Blueprint from `render.yaml`.
3. Supply the backend hostname in `DJANGO_ALLOWED_HOSTS` and the complete HTTPS frontend URL in `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`.
4. Supply the frontend `VITE_API_URL` as `https://<api-host>/api` and the approved `VITE_BKASH_MERCHANT_NUMBER`.
5. Supply the matching backend `BKASH_MERCHANT_NUMBER`.
6. Add Supabase S3 endpoint, region, bucket, access key, and secret key directly in Render. Never commit them.
7. Set `FRONTEND_URL` to the public HTTPS storefront URL. Password-reset links are built from this value.
8. Configure an authenticated SMTP provider with `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, and `DEFAULT_FROM_EMAIL`.
9. Deploy, then create the first superuser using Render Shell.

The blueprint installs dependencies, collects hashed static files, applies migrations once, starts Gunicorn, uses managed PostgreSQL, and exposes `/api/health/` for health checks.

## Release verification

```powershell
python manage.py check --deploy --fail-level WARNING
python manage.py showmigrations
python manage.py database_status
```

Verify HTTPS redirects, admin login, image uploads, CORS, CSRF, customer journey, bKash/COD status, and all UAT scenarios.

## Password-recovery email verification

Development uses Django's console email backend by default, so reset links appear in the backend terminal. Production must use the SMTP backend and must never expose SMTP credentials to the React frontend.

After deployment:

1. Request a reset for a real test account and confirm the response does not disclose whether the email exists.
2. Verify both HTML and plain-text email content and confirm the link points to the HTTPS storefront.
3. Confirm the link expires after `PASSWORD_RESET_TIMEOUT` seconds and fails after one successful use.
4. Confirm weak and mismatched passwords are rejected.
5. Confirm repeated requests are limited by `PASSWORD_RESET_THROTTLE_RATE`.
6. Remove the test email and credentials from release evidence.

## Backup and restore

Application-level backup:

```powershell
python manage.py backup_database --output backups/pre-release.json
python manage.py restore_database backups/pre-release.json --flush --yes
```

For production, also use the hosting provider's encrypted PostgreSQL snapshot or `pg_dump`. Test restoration in an isolated database, validate row counts and images, then destroy the rehearsal environment.

## Monitoring

- Poll `/api/health/` and alert on non-200 responses.
- Monitor 5xx rate, latency, failed login spikes, payment rejections, low stock, database capacity, and Supabase storage errors.
- Keep logs access-controlled and avoid logging passwords, tokens, bKash credentials, PINs, OTPs, or full personal details.

## Rollback

1. Stop new deployments and record the incident window.
2. Roll back to the last known-good Git commit/build.
3. Restore the database only when schema/data corruption requires it; never overwrite newer legitimate orders casually.
4. Re-run health, migration, payment, checkout, admin, and UAT checks before reopening traffic.
