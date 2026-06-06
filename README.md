ThriftVibes254 Management System
Overview

ThriftVibes254 Management System is a web-based inventory and sales management application developed using Django, Bootstrap, and MySQL. The system is designed to help thrift clothing businesses efficiently manage products, customers, sales transactions, orders, payments, and business reports from a centralized dashboard.

The project was developed to simplify daily business operations, improve inventory tracking, and provide real-time insights into sales performance for small and medium-sized thrift stores. Similar inventory systems typically focus on stock tracking, sales recording, reporting, and customer management.

Key Features
Dashboard
Business overview dashboard
Total sales statistics
Total orders summary
Product inventory overview
Recent transactions display
Quick access to business operations
Product Management
Add new products
Edit existing products
Delete products
Product categorization
Product image management
Stock quantity tracking
Sales Management
Record customer sales
Generate sales records
Automatic inventory updates after sales
Sales history tracking
Sales reporting
Order Management
Create customer orders
Track order status
Manage pending orders
Update completed orders
Customer Management
Register customers
View customer purchase history
Manage customer information
Customer database management
Inventory Management
Stock monitoring
Low stock tracking
Product availability management
Inventory updates
Payment Integration
M-Pesa STK Push Integration
Payment confirmation tracking
Transaction recording
Payment history management
Reports & Analytics
Daily sales reports
Monthly sales reports
Product performance reports
Revenue analysis
Inventory reports
User Authentication
Secure login system
Logout functionality
Admin access control
User profile management
Technologies Used
Backend
Python 3
Django Framework
Frontend
HTML5
CSS3
Bootstrap 5
JavaScript
Database
MySQL
Payment Gateway
Safaricom M-Pesa API
Version Control
Git
GitHub
System Architecture
User
 │
 ▼
Django Views
 │
 ▼
Business Logic
 │
 ▼
Models
 │
 ▼
MySQL Database
 │
 ▼
Reports / Dashboard / Payments
Project Structure
ThriftVibes254/
│
├── inventory/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│
├── templates/
│   ├── dashboard/
│   ├── products/
│   ├── orders/
│   ├── customers/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/
│
├── manage.py
├── requirements.txt
└── README.md
Installation Guide
1. Clone the Repository
git clone https://github.com/yourusername/thriftvibes254.git
cd thriftvibes254
2. Create Virtual Environment

Linux:

python3 -m venv env
source env/bin/activate

Windows:

python -m venv env
env\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
4. Configure Database

Update your MySQL database settings inside:

settings.py

Example:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'thriftvibes254',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
5. Run Migrations
python manage.py makemigrations
python manage.py migrate
6. Create Superuser
python manage.py createsuperuser
7. Start Development Server
python manage.py runserver

Visit:

http://127.0.0.1:8000/
M-Pesa Integration

The system supports Safaricom M-Pesa STK Push integration.

Features include:

Customer payment requests
Automatic payment verification
Transaction recording
Payment tracking dashboard

To enable M-Pesa:

Create a Safaricom Developer Account.
Generate API credentials.
Add credentials to Django settings.
Configure callback URLs.
Test using the Sandbox Environment.
Future Improvements
QR Code Product Scanning
Barcode Generation
Receipt Printing
Email Notifications
SMS Notifications
Customer Loyalty Program
Supplier Management
Expense Tracking
Mobile Application
Advanced Analytics Dashboard
Screenshots

Add screenshots here:

![Dashboard](screenshots/dashboard.png)

![Products](screenshots/products.png)

![Orders](screenshots/orders.png)

![Reports](screenshots/reports.png)
Author
Brian Mutinda

Founder of ThriftVibes254

Django Developer
System Designer
Content Creator
Entrepreneur
License

This project is licensed under the MIT License.

Copyright (c) 2026 ThriftVibes254

Permission is hereby granted, free of charge,
to any person obtaining a copy of this software...
Acknowledgements
Django Community
Bootstrap Team
MySQL
Safaricom Daraja API
Open Source Contributors

ThriftVibes254 — Simplifying Thrift Business Management Through Technology.
