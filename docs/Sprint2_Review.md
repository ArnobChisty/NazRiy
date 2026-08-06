# Sprint 2 Review — Product Catalogue

## Completed scope

- Django REST backend structure and CORS configuration
- Category and Product models, migration, admin registration, and sample data command
- Repository Pattern for categories, product listing, details, featured products, search, filters, and ordering
- Category, product-list, featured-product, and product-detail JSON endpoints
- Responsive Product Listing page based on Screen 02
- Search, category, price, size, and color filters; sorting and reset controls
- Responsive Product Details page based on Screen 03
- Image gallery, product data, size/color selection, quantity control, and Sprint 3 purchase placeholders
- React integration with the live Django API
- Loading, empty, missing-product, and API-error states

## Verification performed

- `python manage.py check` — passed
- `python manage.py test` — 3 tests passed
- `npm.cmd run lint` — passed
- `npm.cmd run build` — passed
- Live API checks — 8 seeded products, search/category/price/size/color/sort filters passed
- Live frontend route check — `/products` returned HTTP 200

## Run instructions

Backend:

```powershell
cd D:\NazRiy\backend
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py seed_products
.\venv\Scripts\python.exe manage.py runserver
```

Frontend in a second terminal:

```powershell
cd D:\NazRiy\frontend
npm.cmd run dev
```

Open `http://127.0.0.1:5173/products`.

## Sprint boundary

Add to Cart and Buy Now are visible placeholders as required by Sprint 2. Cart, checkout, authentication, and order creation belong to Sprint 3.
