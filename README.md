# Django E-Commerce Platform

A full-stack e-commerce platform built with Django and PostgreSQL,
featuring a modular architecture and Arabic language support.

## Features

- Product catalog with categories and filtering
- Shopping cart with session management
- Order processing and management system
- User authentication and profile management
- Arabic/English internationalization (i18n)
- Sqlite3 with optimized ORM queries

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django, Python |
| Database | Sqlite3 |
| Frontend | HTML, CSS, Bootstrap, JavaScript |
| i18n | Django Translations (AR/EN) |

## Quick Start

### WSL

```bash
git clone https://github.com/vhmd0/store-p11
cd store-p11
chmod +x start.sh
./start.sh
```

### Windows

```bash
git clone https://github.com/vhmd0/store-p11
cd store-p11
chmod +x start.bat
./start.bat
```

Visit: <http://localhost>

## Project Structure

```
├── products/     # Product catalog & categories
├── cart/         # Shopping cart logic
├── orders/       # Order processing
├── users/        # Authentication & profiles
├── shop/         # Main storefront
└── core/         # Shared utilities
```
