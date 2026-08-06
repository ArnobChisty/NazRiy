# NazRiy Django API

## Run locally

```powershell
cd D:\NazRiy\backend
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py seed_products
.\venv\Scripts\python.exe manage.py runserver
```

PostgreSQL is the active development database. Local credentials are loaded from the ignored `backend/.env` file; copy `.env.example` when setting up another machine.

To temporarily use the old SQLite database in the current PowerShell session:

```powershell
$env:DB_ENGINE="sqlite"
.\venv\Scripts\python.exe manage.py runserver
```

## Product endpoints

- `GET /api/categories/`
- `GET /api/products/`
- `GET /api/products/featured/`
- `GET /api/products/<slug>/`
- Filters: `search`, `category`, `min_price`, `max_price`, `size`, `color`, `ordering`
