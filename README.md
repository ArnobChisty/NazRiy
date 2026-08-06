# NazRiy

NazRiy is a full-stack clothing e-commerce application developed for a Software Engineering course. It combines a responsive React storefront with a Django REST backend and a professional administration dashboard.

## Current status

Sprint 1 through Sprint 6 functionality is implemented in the current working branch. The included production blueprint is ready for deployment after authorized hosting domains and secrets are supplied.

- Responsive clothing storefront and animated hero banners
- Product catalogue, search, sorting, filtering, and product details
- Product image galleries, sizes, colours, stock status, and featured products
- Registration, login, logout, secure email password recovery, profile management, and protected customer pages
- Persistent shopping cart, checkout, inventory updates, and order history
- Customer order details and order-status tracking
- Database-managed banners, navigation links, top products, categories, and products
- Professional Django admin dashboard with revenue, order, sales, and inventory information
- Idempotent manual bKash transaction submission, cash on delivery, cancellation feedback, and administrator verification
- Automated Django and React tests, coverage enforcement, dependency auditing, CI, deployment checks, backups, and rollback documentation

## Technology stack

| Area | Technology |
| --- | --- |
| Frontend | React 19, TypeScript, Vite 8 |
| Backend | Django 6, Django REST Framework |
| Authentication | Expiring Django-signed API tokens |
| Database | PostgreSQL in development, testing, CI, and production |
| Images | Supabase-compatible persistent object storage with file metadata stored in PostgreSQL |
| Styling | Responsive custom CSS |
| Testing | Django TestCase, Vitest, React Testing Library, jsdom, V8 coverage, TypeScript, ESLint |

## Project structure

```text
NazRiy/
├── backend/
│   ├── backend/              # Django project configuration
│   ├── store/                # Models, APIs, admin modules, migrations, and tests
│   ├── templates/admin/      # Shared admin templates
│   ├── media/                # Development image uploads
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── public/               # Public storefront assets
│   ├── src/components/       # Shared React components
│   ├── src/pages/            # Storefront and account pages
│   └── package.json
└── docs/                     # Sprint, architecture, and requirements documents
```

## Local development

### Prerequisites

- Python 3.13 or newer
- Node.js 20 or newer
- npm
- PostgreSQL 14 or newer

### 1. Start the backend

From the repository root in PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API will run at `http://127.0.0.1:8000/api/` and the administration site at `http://127.0.0.1:8000/admin/`.

PostgreSQL is required in every environment. Copy `backend/.env.example` to `backend/.env`, configure the local PostgreSQL database, and replace every production placeholder before deployment.

### 2. Start the frontend

Open another PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

The storefront will normally run at `http://127.0.0.1:5173/`. It uses `http://127.0.0.1:8000/api` by default. Set `VITE_API_URL` when the backend is hosted elsewhere.

Copy `frontend/.env.example` to `frontend/.env` and set `VITE_BKASH_MERCHANT_NUMBER` to the approved NazRiy bKash number. The bKash option remains disabled when this value is missing, preventing customers from seeing or paying an unconfigured number.

### Optional demonstration data

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py seed_products
```

## Main routes

### Storefront

| Route | Purpose |
| --- | --- |
| `/` | Home page |
| `/products` | Product listing and filters |
| `/products/<slug>` | Product details |
| `/cart` | Shopping cart |
| `/checkout` | Protected checkout |
| `/login` and `/register` | Customer authentication |
| `/forgot-password` | Enumeration-safe password-reset request |
| `/reset-password` | Secure one-time password-reset confirmation |
| `/account` | Protected customer profile |
| `/orders` | Protected order history |
| `/orders/<id>` | Protected order details |

### Backend

| Route | Purpose |
| --- | --- |
| `/api/products/` | Product catalogue |
| `/api/categories/` | Categories |
| `/api/banners/` | Active banners |
| `/api/top-products/` | Homepage top products |
| `/api/navigation-links/` | Storefront navigation |
| `/api/auth/` | Registration, login, profile, and password endpoints |
| `/api/auth/password/reset/` | Rate-limited password-reset email request |
| `/api/auth/password/reset/confirm/` | Reset-link validation and password confirmation |
| `/api/cart/` | Cart operations |
| `/api/orders/` | Checkout and customer orders |
| `/api/orders/<id>/payment/` | Ownership-protected bKash transaction submission and cancellation |
| `/admin/` | Administration dashboard |

## Verification

Run the backend checks and tests:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py check
python manage.py test store
python manage.py check --deploy
```

Run the frontend validation:

```powershell
cd frontend
npm run build
npm run lint
npm run test:coverage
npm audit
```

The verified suite includes 40 passing Django tests and 25 passing frontend tests. The production frontend build, ESLint, migration drift check, deployment check, PostgreSQL restore rehearsal, and dependency audit pass.

## Administration

After creating a superuser, sign in at `/admin/`. Administrators can manage:

- Products, galleries, prices, sizes, colours, and stock
- Orders, fulfilment status, and bKash/COD payment status
- Homepage top products
- Hero and promotional banners
- Storefront navigation links
- Categories, carts, customers, and authentication records
- Revenue, sales, order, and inventory dashboard information

## Security and deployment

- Secrets and production settings are read from environment variables.
- Production mode enables secure cookies, HTTPS redirection, HSTS, content-type protection, and referrer policy controls.
- CORS, CSRF trusted origins, allowed hosts, database credentials, and token lifetime are configurable.
- Password recovery uses enumeration-safe responses, IP throttling, expiring one-time Django tokens, password validation, and HTML/plain-text email alternatives.
- Development may print reset emails to the console. Production must configure authenticated SMTP settings and an HTTPS `FRONTEND_URL`.
- Never commit `backend/.env`, development databases, uploaded media, virtual environments, or frontend build output.

See [Deployment-and-Operations-Guide.md](docs/Deployment-and-Operations-Guide.md) for deployment, backup, restoration, monitoring, and rollback steps. The repository includes `render.yaml` for the backend, PostgreSQL database, and frontend static site.

## Project documentation

The `docs/` directory contains architecture and use-case diagrams, user stories, testing strategy, UAT/user guide, release checklist, technical review notes, and sprint plans.

## Git workflow

`main` is the integrated branch. Team work is developed on member or feature branches and merged through pull requests after conflict resolution and verification.
