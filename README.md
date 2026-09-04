# Django E-Commerce

A Django-based e-commerce web application built to practice and demonstrate core backend development concepts through a real-world shopping workflow.

## Overview

This project is an online store developed with Django. It implements common e-commerce features such as user authentication, product management, product filtering and search, session-based shopping cart, order creation, and discount codes.

The main purpose of this project was to move from learning individual Django concepts to combining them into a complete backend application.

## Features

* User registration and authentication
* Login and logout
* Custom user model
* Email-based authentication
* Product and category management
* Product detail pages
* Dynamic category navigation
* Product search
* Product filtering by:

  * Category
  * Color
  * Size
  * Price range
* Product pagination
* Session-based shopping cart
* Add and remove products from cart
* Product quantity management
* Product color and size selection
* Order creation
* User-specific order information
* Discount code system
* Django Admin panel
* Dynamic homepage content

## Technologies

* Python
* Django
* Django Templates
* SQLite
* HTML5
* CSS3
* Bootstrap
* JavaScript
* Git
* GitHub

## Backend Concepts

This project was developed to practice and understand several important backend concepts:

* Django Class-Based Views
* Django Models and ORM
* Foreign Key relationships
* Many-to-Many relationships
* Custom User Model
* Authentication backends
* User authentication
* Sessions and cookies
* Query parameters
* Database filtering
* Pagination
* CRUD operations
* Form handling
* Access control
* Django Admin
* URL routing
* Template context
* Session-based cart management
* Order and discount business logic

## Project Structure

```text
django-ecommerce/
│
├── Blog/              # Django project configuration
├── Home/              # Homepage functionality
├── account/           # Authentication and user management
├── cart/              # Cart, orders and discount functionality
├── product/           # Products, categories, colors and sizes
├── static/            # CSS, JavaScript and static images
├── templates/         # Django templates
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/arman-031/django-ecommerce.git
cd django-ecommerce
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment.

**Windows:**

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Create a superuser

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

## Admin Panel

The Django Admin panel can be used to manage application data such as:

* Products
* Categories
* Colors
* Sizes
* Orders
* Discount codes
* Users
* Addresses

## Application Flow

The main shopping workflow can be summarized as:

```text
User
  │
  ▼
Authentication
  │
  ▼
Browse Products
  │
  ├── Search
  ├── Filter
  └── Pagination
  │
  ▼
Product Details
  │
  ▼
Session-based Cart
  │
  ▼
Order Creation
  │
  ▼
Discount
```

## Project Status

The core e-commerce functionality has been implemented.

This project is currently being used as a backend development portfolio project. Further improvements are planned to make the application closer to production-level standards.

## Future Improvements

* Automated testing
* PostgreSQL database
* Django REST Framework API
* Payment gateway integration
* Improved order status management
* Stronger input validation
* Better error handling
* Query optimization
* Redis caching improvements
* Production deployment
* API documentation

## Learning Outcomes

Working on this project helped me understand how different backend components work together in a real-world application.

Instead of focusing only on individual Django features, the project combines authentication, database relationships, sessions, business logic, filtering, pagination, orders, and discounts into one application.

## Author

**Arman Rezagholian**

Backend Developer | Python & Django

This project was developed as part of my backend development learning and portfolio journey.
