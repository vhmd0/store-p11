# Smart S3r - Electronics E-Commerce Store

A Django-powered e-commerce store for electronics with Arabic/English bilingual support.

## Features

- 🛒 Full e-commerce functionality (cart, orders, wishlist)
- 📱 Responsive design for mobile & desktop
- 🌐 Bilingual support (English & Arabic)
- 🔐 User authentication with profiles & addresses
- 📦 Order management with status tracking
- ⭐ Product reviews & ratings
- 💳 Cash on delivery payment

## Tech Stack

- **Backend:** Django 6.0
- **Database:** MariaDB/MySQL
- **Frontend:** Bootstrap 5 + django-bootstrap5
- **Admin:** Jazzmin
- **Icons:** Bootstrap Icons

## Prerequisites

- Python 3.10+
- MariaDB 10.5+ or MySQL 8.0+
- pip or uv

## Quick Start

### 1. Clone & Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Database

#### Option A: Using existing database

```bash
# Create database in MariaDB/MySQL
mysql -u root -p

CREATE DATABASE s3r_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

#### Option B: Fresh setup with sample data

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE s3r_store CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run schema
mysql -u root -p s3r_store < database.sql

# Run sample data (120+ products)
mysql -u root -p s3r_store < data_seeding.sql
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Run Server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000

---

## Project Structure

```
django-store/
├── core/              # Core app (banners, base templates)
├── users/             # User profiles & addresses
├── products/          # Products, categories, brands, tags
├── cart/              # Shopping cart
├── orders/            # Order management
├── shop/              # Django settings
├── templates/         # HTML templates
├── static/           # CSS, JS, images
├── database.sql       # Database schema
├── data_seeding.sql   # Sample products data
└── requirements.txt   # Python dependencies
```

---

## Database Schema

### Tables

| Table | Description |
|-------|-------------|
| `products_category` | Product categories (Smartphones, Laptops, Audio, etc.) |
| `products_brand` | Brands (Apple, Samsung, Sony, etc.) |
| `products_product` | Products with details |
| `products_tag` | Tags (New, Sale, Bestseller, 5G, etc.) |
| `products_review` | User reviews & ratings |
| `products_wishlist` | User wishlists |
| `cart_cart` | Shopping carts |
| `cart_cartitem` | Cart items |
| `orders_order` | Orders |
| `orders_orderitem` | Order items |
| `users_profile` | Extended user info |
| `users_address` | User addresses |

---

## Sample Data

The `data_seeding.sql` includes:

- **6 categories**
- **15+ brands**
- **120 products** with real names, prices (EGP), and images
- **3 test users**
- **Sample reviews, wishlists, carts, and orders**

### Test Users

| Username | Email | Password |
|----------|-------|----------|
| ahmed_salah | ahmed@example.com | (create your own) |
| fatma_ali | fatma@example.com | (create your own) |
| mohamed_hassan | mohamed@example.com | (create your own) |

---

## Configuration

### Database Settings

Edit `shop/settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "s3r_store",
        "USER": "root",
        "PASSWORD": "your_password",  # Add your password
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}
```

### Static & Media Files

```python
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "www" / "media"
```

---

## Admin Panel

Access at: http://127.0.0.1:8000/admin

Features:
- Product management
- Order management
- User management
- Category & brand management
- Review moderation
- Banner management

---

## API Endpoints (Optional)

For REST API, install DRF:

```bash
pip install djangorestframework django-cors-headers
```

Add to `INSTALLED_APPS`:

```python
'rest_framework',
'corsheaders',
```

---

## Troubleshooting

### "mysqlclient not found"

Install the MySQL development libraries:

**Ubuntu/Debian:**
```bash
sudo apt install libmysqlclient-dev
```

**Windows:**
Use `pymysql` instead (already in requirements.txt)

### Database connection errors

1. Ensure MariaDB/MySQL is running
2. Check credentials in `settings.py`
3. Verify database exists: `SHOW DATABASES;`

### Static files not loading

```bash
python manage.py collectstatic
```

---

## License

MIT License
