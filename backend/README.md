# NazRiy Django API

## PostgreSQL development setup

PostgreSQL is the default database. Copy `.env.example` to `.env`, set the local PostgreSQL credentials, and create the configured database/user before starting Django. SQLite is used only when `DB_ENGINE=sqlite` is set explicitly.

Install dependencies and verify the connection:

```powershell
cd D:\NazRiy\backend
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py database_status
.\venv\Scripts\python.exe manage.py check --database default
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py seed_products
.\venv\Scripts\python.exe manage.py runserver
```

Useful database administration commands:

```powershell
# Open PostgreSQL's command-line client with Django's configured credentials
.\venv\Scripts\python.exe manage.py dbshell

# Create an administrator who can manage products, banners, images, orders, and navigation
.\venv\Scripts\python.exe manage.py createsuperuser

# Create a portable application-data backup
.\venv\Scripts\python.exe manage.py backup_database

# Restore a previously created JSON backup
.\venv\Scripts\python.exe manage.py loaddata .\backups\nazriy-TIMESTAMP.json
```

The public health endpoint is `GET /api/health/`. It returns HTTP 200 only when Django can execute a database query.

To temporarily use the old SQLite database in the current PowerShell session:

```powershell
$env:DB_ENGINE="sqlite"
.\venv\Scripts\python.exe manage.py runserver
```

## Supabase image storage

Django models remain unchanged: PostgreSQL stores product/banner/category records and each `FileField` value, while Supabase Storage stores and serves the uploaded image object itself.

1. Create a Supabase Storage bucket, for example `nazriy-media`.
2. In **Storage > Configuration > S3**, enable S3 and generate server-side S3 access keys.
3. Copy the endpoint and region into `backend/.env`.
4. Set `USE_SUPABASE_STORAGE=true` and fill every `SUPABASE_STORAGE_*` value from `.env.example`.
5. Install requirements, restart Django, and confirm `media_storage` is `supabase` at `/api/health/`.

Keep S3 access keys only in `backend/.env`; never place them in frontend code or commit them. Existing local media is not uploaded automatically. Upload existing images again through Django admin or migrate the `backend/media` objects separately.

## Product endpoints

- `GET /api/categories/`
- `GET /api/products/`
- `GET /api/products/featured/`
- `GET /api/products/<slug>/`
- Filters: `search`, `category`, `min_price`, `max_price`, `size`, `color`, `ordering`
