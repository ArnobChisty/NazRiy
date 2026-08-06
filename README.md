# NazRiy

NazRiy is a full-stack clothing e-commerce application developed for a Software Engineering course. It combines a responsive React storefront with a Django REST backend and a professional administration dashboard.

## Current status

Sprint 1 through Sprint 4 functionality is implemented and integrated into `main`.

- Responsive clothing storefront and animated hero banners
- Product catalogue, search, sorting, filtering, and product details
- Product image galleries, sizes, colours, stock status, and featured products
- Registration, login, logout, profile management, and protected customer pages
- Persistent shopping cart, checkout, inventory updates, and order history
- Customer order details and order-status tracking
- Database-managed banners, navigation links, top products, categories, and products
- Professional Django admin dashboard with revenue, order, sales, and inventory information
- Automated backend tests plus frontend build and lint verification

## Technology stack

| Area | Technology |
| --- | --- |
| Frontend | React 19, TypeScript, Vite 8 |
| Backend | Django 6, Django REST Framework |
| Authentication | Expiring Django-signed API tokens |
| Database | SQLite for local development; PostgreSQL supported for deployment |
| Images | Django media uploads with file metadata and paths stored in the database |
| Styling | Responsive custom CSS |
| Testing | Django TestCase, TypeScript compiler, Vite build, ESLint |

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

- Python 3.12 or newer
- Node.js 20 or newer
- npm

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

Local development uses SQLite automatically. Environment variables are optional locally. For deployment, copy `backend/.env.example` to `backend/.env`, replace every placeholder, and configure PostgreSQL and the production host values.

### 2. Start the frontend

Open another PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

The storefront will normally run at `http://127.0.0.1:5173/`. It uses `http://127.0.0.1:8000/api` by default. Set `VITE_API_URL` when the backend is hosted elsewhere.

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
| `/api/cart/` | Cart operations |
| `/api/orders/` | Checkout and customer orders |
| `/admin/` | Administration dashboard |

## Verification

Run the backend checks and tests:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py check
python manage.py test store
```

Run the frontend validation:

```powershell
cd frontend
npm run build
npm run lint
```

The current store suite contains 20 passing Django tests. The production frontend build and ESLint checks also pass.

## Administration

After creating a superuser, sign in at `/admin/`. Administrators can manage:

- Products, galleries, prices, sizes, colours, and stock
- Orders and fulfilment status
- Homepage top products
- Hero and promotional banners
- Storefront navigation links
- Categories, carts, customers, and authentication records
- Revenue, sales, order, and inventory dashboard information

## Security and deployment

- Secrets and production settings are read from environment variables.
- Production mode enables secure cookies, HTTPS redirection, HSTS, content-type protection, and referrer policy controls.
- CORS, CSRF trusted origins, allowed hosts, database credentials, and token lifetime are configurable.
- Never commit `backend/.env`, development databases, uploaded media, virtual environments, or frontend build output.

See [Sprint4-Deployment.md](docs/Sprint4-Deployment.md) for the deployment checklist.

## Project documentation

The `docs/` directory contains the architecture diagram, use-case diagram, user stories, implementation checklists, review notes, and sprint plans.

## Git workflow

`main` is the integrated branch. Team work is developed on member or feature branches and merged through pull requests after conflict resolution and verification.
