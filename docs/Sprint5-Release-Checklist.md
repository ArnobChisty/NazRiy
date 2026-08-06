# Sprint 5 Production Release Checklist

## Pre-release

- [ ] Pull request checks pass: backend, frontend tests, coverage, lint, and build.
- [ ] `python manage.py makemigrations --check --dry-run` reports no model changes.
- [ ] `python manage.py migrate --plan` is reviewed.
- [ ] `python manage.py check --deploy` is reviewed with production environment variables.
- [ ] `DJANGO_SECRET_KEY` is long, random, private, and not the development fallback.
- [ ] `DJANGO_DEBUG=false`.
- [ ] Allowed hosts, CORS origins, and CSRF trusted origins match the deployment.
- [ ] PostgreSQL credentials use a least-privilege application user.
- [ ] HTTPS redirect, secure cookies, HSTS, proxy SSL header, and frame protection are enabled.
- [ ] Static and media persistence locations are configured and writable.
- [ ] `VITE_BKASH_MERCHANT_NUMBER` contains the approved NazRiy bKash number and is visible correctly at checkout.
- [ ] Administrators can verify/reject bKash references against the merchant statement; no PIN or OTP is collected.

## Backup

Create and verify an application-data backup:

```powershell
cd backend
python manage.py backup_database
```

For PostgreSQL production, also create a database-native backup:

```text
pg_dump --format=custom --file=nazriy-before-release.dump <database>
```

Store backups outside the application host, encrypt them, record checksums, and test restoration in staging.

## Deployment

1. Record the current release commit and deployment version.
2. Enable maintenance mode if the platform requires it.
3. Create database and media backups.
4. Deploy the exact reviewed commit.
5. Install locked dependencies.
6. Run migrations once.
7. Collect static files.
8. Restart application processes.
9. Check logs and health endpoints.
10. Run smoke tests: home, products, login, bKash checkout, payment verification, admin, and order history.

## Logging and monitoring

- Django and store logs use timestamped structured console output controlled by `DJANGO_LOG_LEVEL`.
- Production should collect stdout/stderr centrally with retention and alerting.
- Never log passwords, tokens, personal delivery data, payment request bodies, or secret environment values.
- Alert on repeated 5xx responses, migration failures, payment failures, and abnormal login failures.

## Rollback

1. Stop new deployments and record the failure.
2. Re-deploy the previously known-good commit.
3. If the migration is reversible, run its documented reverse migration.
4. If data was changed incompatibly, restore the verified pre-release database backup.
5. Restore matching media when necessary.
6. Restart processes and repeat smoke tests.
7. Document root cause and block release until regression tests cover it.

## Release ownership

Assign one person to deployment, one to database/backup verification, and one to UAT/smoke testing. The release owner makes the final go/no-go decision from evidence, not from schedule pressure.
