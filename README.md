# Django E-Commerce

A Persian Django storefront built as a learning project for backend development.
**Status: in development.** The shopping cart and order workflow have regression tests;
this is not a production-ready store. My main portfolio project is
[Coach Management System](https://github.com/arman-031/coach-management-system).

## Implemented features

- Custom phone-based users, registration, password validation, login and POST logout.
- Optional email authentication for users whose email has been set; inactive users cannot log in.
- Products, categories, search, color/size filtering and pagination.
- Session cart with product-specific option validation and quantities from 1 to 99 per line.
- Decimal prices in **tomans**, with two decimal places retained for exact arithmetic.
- POST order creation, atomic order/item storage and a unique checkout token to prevent replaying the same cart.
- Prices are recalculated from the product catalog at checkout; saved order items retain that price.
- One discount per unpaid order, with a transaction and conditional updates to guard coupon usage.
- Owner-only order details and authenticated address creation in the account.
- Django admin for products, users, addresses, orders and discount codes.

## Not implemented yet

Payment gateway, order/address linkage, shipping charges, inventory tracking, order status
workflow, price-range filtering, REST API, Redis integration and production deployment.
The storefront template still contains some placeholder sections and English text.
Registration currently uses phone and password; SMS/OTP verification is not implemented.

## Stack and structure

Python 3.12 (tested), Django 5.2.9, SQLite, Django Templates, Bootstrap, Pillow and python-dotenv.

| Directory | Purpose |
| --- | --- |
| `Blog/` | Project settings and URL routing (original project name) |
| `Home/` | Homepage |
| `account/` | Users, authentication, registration and account addresses |
| `product/` | Catalog, search and filters |
| `cart/` | Session cart, orders, coupons and regression tests |
| `templates/`, `static/` | Shared templates and storefront assets |

## Local setup

```bash
git clone https://github.com/arman-031/django-ecommerce.git
cd django-ecommerce
python -m venv venv
```

Activate on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` (`Copy-Item .env.example .env` on PowerShell,
`cp .env.example .env` on macOS/Linux). Generate a key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Paste it into `.env` as `DJANGO_SECRET_KEY='your-generated-key'` (keep the quotes).
Use `DJANGO_DEBUG=True` and `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1` for local development.
The actual `.env`, database and uploaded media are ignored by Git. Do not commit real keys.
No Redis service is needed for local setup; the default cache is in memory.

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000/> and <http://127.0.0.1:8000/admin/>.
Create products and their available colors/sizes in admin before trying the shopping flow.
Product discounts in the catalog are not applied automatically; the implemented discount
flow uses order coupon codes.

### Existing local databases

Back up your database before applying the new migrations. They convert float/integer
money columns to two-decimal `DecimalField` columns and add integrity constraints.
Old float values are rounded to two decimal places. Existing negative prices/totals,
order quantities outside 1–99, or coupon percentages outside 0–100 must be corrected
before migration. New fields do not reconstruct the discount history of older orders.

## Tests

```bash
python manage.py check
python manage.py makemigrations account product cart Home --check --dry-run
python manage.py test
```

GitHub Actions runs these checks plus a clean database migration on every push and pull request.
Tests cover input validation, exact money calculations, CSRF, access control, inactive
accounts, checkout replay, rollback after failed order creation, and coupon exhaustion/reuse.
The local suite uses SQLite; true concurrent requests on PostgreSQL have not been tested.

## Next steps

1. Link a selected account address to an order and define order statuses.
2. Add inventory checks and payment integration with idempotent callbacks.
3. Move to PostgreSQL and test real concurrent checkout/coupon requests.
4. Complete Persian copy and replace remaining template placeholders.
5. Add a DRF API and deployment configuration once the storefront flow is stable.

## Author

Arman Rezagholian — Backend Developer | Python & Django
