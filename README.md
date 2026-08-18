# 🏨 Hotel Stockroom & Inventory Management System

A full-stack Hotel Inventory & Stockroom Management System developed using **Flask** and **PostgreSQL** to streamline inventory operations in hotels and restaurants.

The system manages the complete inventory lifecycle, including stock receiving, stock issuing, recipe management, kitchen production, purchase management, wastage tracking, and variance reporting.

---

## 🚀 Features

### 🔐 Authentication

* Role-based login
* Store Keeper
* Chef
* Purchase Manager
* F&B Manager

---

### 📦 Store Module

* Receive inventory
* Record damaged goods
* Issue stock to kitchen
* Store wastage management
* Live store inventory
* View chef stock requests

---

### 👨‍🍳 Chef Module

* Request ingredients from store
* View issued kitchen stock
* Recipe Master
* Recipe ingredient management
* Kitchen Production
* Automatic ingredient consumption
* Kitchen wastage tracking

---

### 🛒 Purchase Manager

* Create Purchase Orders
* Track Purchase Orders
* Vendor management
* Order status tracking

---

### 👨‍💼 F&B Manager

* Approve/Reject Purchase Orders
* View Purchase Order History
* Inventory Variance Report
* Store Balance Report
* Kitchen Balance Report

---

## 📊 Reports

* Inventory Balance
* Kitchen Stock
* Store Stock
* Consumption Report
* Store Wastage Report
* Kitchen Wastage Report
* Variance Report

---

## 🛠️ Tech Stack

**Backend**

* Python
* Flask
* SQLAlchemy

**Database**

* PostgreSQL

**Frontend**

* HTML5
* CSS3
* Bootstrap 5
* Jinja2 Templates

**ORM**

* Flask SQLAlchemy

**Migration**

* Flask-Migrate
* Alembic

---

## 📂 Project Structure

```text
stockroom/
│
├── app.py
├── config.py
├── extension.py
├── models.py
├── seed.py
│
├── routes/
│   ├── auth.py
│   ├── chef.py
│   ├── store.py
│   ├── purchase.py
│   └── manager.py
│
├── templates/
├── migrations/
└── requirements.txt
```

---

## ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/your-username/hotel-stockroom-management.git
cd hotel-stockroom-management
```

Create virtual environment

```bash
python -m venv venv
```

Activate virtual environment

**Windows**

```bash
venv\Scripts\activate
```

**Mac/Linux**

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Configure PostgreSQL in `config.py`

Run database migrations

```bash
flask db upgrade
```

Run the application

```bash
python app.py
```

---

## 👥 User Roles

| Role             | Responsibilities                                        |
| ---------------- | ------------------------------------------------------- |
| Store Keeper     | Receive stock, issue stock, manage store inventory      |
| Chef             | Request ingredients, manage recipes, kitchen production |
| Purchase Manager | Create and manage purchase orders                       |
| F&B Manager      | Approve purchase orders and monitor reports             |

---

## 📈 Future Enhancements

* Hotel POS Integration
* Automatic Stock Deduction from Customer Orders
* Vendor Portal
* QR/Barcode Scanning
* Email Notifications
* Dashboard Analytics
* Multi-Property Management
* Sales & Inventory Analytics

---

## 📜 License

This project is developed for academic and learning purposes.
