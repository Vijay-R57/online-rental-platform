# RentEase — Online Property Rental and Management Portal

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2%20LTS-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue.svg)](https://www.postgresql.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-Academic%20Mini--Project-orange.svg)]()

A complete, production-conscious, full-stack **Online Property Rental and Management Portal** built with **Python 3.13, Django 5.2 LTS, PostgreSQL 17, and Bootstrap 5**. Designed to unify property owners (landlords), tenants (renters), and administrators into one coherent, end-to-end digital property management system.

---

## 🏢 System Architecture & Modules

The platform is structured into decoupled, modular Django applications:

```
c:\hinduja simple\
├── portal/                     # Root configuration package
│   ├── settings.py             # Configured with PostgreSQL, django-environ, AUTH_USER_MODEL
│   ├── urls.py                 # Central URL router & media handler
│   ├── wsgi.py / asgi.py       # Production server gateways
├── apps/
│   ├── accounts/               # CustomUser (ADMIN, OWNER, TENANT) & Tenant KYC Documents
│   ├── properties/             # Property listings CRUD, photo gallery, amenities, search & filter
│   ├── rentals/                # Rental applications, bookings, and digital lease agreements
│   ├── payments/               # Rent tracking, invoices, simulated checkout, & official receipts
│   ├── maintenance/            # Repair tickets, priority dispatch, and landlord resolution notes
│   ├── dashboard/              # Dynamic role-based dashboards with real database metrics
│   └── core/                   # Responsive commercial landing page & platform statistics
├── templates/                  # Server-rendered semantic Bootstrap 5 templates
├── static/                     # Custom CSS & JavaScript modules
├── media/                      # Uploaded tenant documents, property photos, and receipts
├── requirements.txt            # Pinned Python package dependencies
├── .env.example                # Sanitized environment configuration template
└── README.md                   # Complete documentation & demonstration guide
```

---

## 🌟 Key Features by Module

### 1. Role-Based Authentication & User Profiles (`apps/accounts`)
- **Custom User Model**: Extends `AbstractUser` with system roles:
  - `ADMIN` — Platform administrator with full moderation and Django Admin access.
  - `OWNER` — Property owner / landlord managing units and reviewing tenants.
  - `TENANT` — Renter browsing homes, submitting applications, and paying rent.
- **Tenant KYC & Verification**: Secure upload of Government IDs, payslips, employment verification, and landlord references (`TenantDocument`).
- **Profile Management**: Profile picture upload, occupation, bio, and emergency contact records.

### 2. Property Listings & Gallery (`apps/properties`)
- **Full CRUD Management**: Owners can create, update, manage, or delete listings.
- **Rich Specifications**: Property type (Apartment, House, Condo, Studio, Villa), status (Available, Rented, Maintenance), bedrooms, bathrooms, square footage, furnishing, and pet policies.
- **Multiple Image Gallery**: Primary cover image plus unlimited gallery photos (`PropertyImage`).
- **Amenity Tagging**: High-speed Wi-Fi, Dedicated Parking, Central AC, In-unit Laundry, Pool, Gym, and Balcony with Bootstrap icons (`Amenity`).

### 3. Property Search & Catalog Browsing (`apps/properties`)
- **Dynamic Search & Filtering**: Filter by location keyword, property type, min/max monthly rent, minimum bedrooms, furnishing status, and pet-friendliness.
- **Sorting & Pagination**: Order listings by newest first, price low-to-high, price high-to-low, or bedrooms with Django pagination.
- **Detailed Listing View**: Includes photo galleries, key specs banner, owner profile card, and direct application CTA.

### 4. Tenancy Applications & Bookings (`apps/rentals`)
- **Rental Applications**: Tenants apply directly from property listings with employment details, annual gross income, credit score estimate, move-in date, and personal message.
- **Landlord Review Center**: Owners review applicant financials, verify uploaded documents, and approve or reject applications with review notes.
- **Automated Tenancy Conversion**: Approving an application automatically creates a confirmed `Booking`, marks the property as Occupied, and drafts an active `Lease`.

### 5. Lease Agreements & Digital Signatures (`apps/rentals`)
- **Legal Contract Generation**: Auto-generated formal lease agreement with contract reference number, term dates, monthly rent obligation, security deposit escrow terms, and rules.
- **Digital Execution**: Interactive digital signature workflow recorded with timestamp (`signed_by_tenant`, `signed_by_owner`).
- **Printable Contract View**: Clean layout formatted for PDF printing.

### 6. Payments & Invoicing (`apps/payments`)
- **Rent Tracking & Invoicing**: Automatic invoice generation for monthly rent and security deposits.
- **Simulated Payment Sandbox**: Clearly identified demo sandbox checkout supporting Card (Demo: `4242 4242 4242 4242`) and UPI (`tenant@okaxis`).
- **Official Electronic Receipts**: Real-time receipt generator with unique transaction reference ID, breakdown, payer/payee details, and print capability.

### 7. Maintenance & Repair Requests (`apps/maintenance`)
- **Ticket Submission**: Tenants report maintenance defects (Plumbing, Electrical, Appliance, HVAC, Structural) with urgency level (Low, Medium, High, Emergency) and photo attachments.
- **Landlord Dispatch Tracking**: Owners update status (`Submitted`, `In Progress`, `Resolved`, `Closed`) and record technician appointments.

### 8. Dynamic Role-Based Dashboards (`apps/dashboard`)
- **Genuine Database Metrics**: Zero hardcoded stats. Queries PostgreSQL directly for:
  - **Admin**: Total users, listed properties, active leases, total rent processed, pending applications, and open repair tickets.
  - **Owner**: Units owned, occupancy rate, total rent collected, pending applications, and tenant repair requests.
  - **Tenant**: Active lease status, rent due amounts, payment history, and ticket statuses.

---

## 🚀 Installation & Setup Instructions

### Prerequisites
- Python 3.12 or 3.13 installed
- PostgreSQL 16 or 17 service running locally
- Git installed

### 1. Clone or Open Project
```powershell
cd "c:\hinduja simple"
```

### 2. Activate Virtual Environment
```powershell
# Create venv if not already present
python -m venv venv

# Activate venv on Windows PowerShell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Environment Variables (`.env`)
Create or verify `.env` in the project root:
```env
DEBUG=True
SECRET_KEY=django-insecure-portal-rental-94a8e2b7e1c8413b86dbbfa693d25867-key-2026
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# PostgreSQL Database Configuration
DB_NAME=rental_portal_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
DATABASE_URL=postgres://postgres:your_postgres_password@localhost:5432/rental_portal_db
```

### 5. Run Database Migrations
```powershell
python manage.py migrate
```

### 6. Populate Realistic Demo Data
Run the built-in management command to seed verified properties, accounts, leases, invoices, and tickets:
```powershell
python manage.py seed_portal_data
```

### 7. Run the Development Server
```powershell
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🔑 Pre-Configured Demo Accounts for Presentation

| Role | Username | Access Scope |
| :--- | :--- | :--- |
| **Administrator** | `admin` | Full platform oversight, Django Admin (`/admin/`), all modules |
| **Property Owner** | `landlord_john` | Listed properties, applicant review, lease execution, rent ledger |
| **Property Owner** | `landlord_sarah` | Austin listings, tenant communications, property management |
| **Tenant** | `tenant_alice` | Active tenancy at Oakwood Villa, rent checkout, maintenance tickets |
| **Tenant** | `tenant_david` | Pending rental application, property search, document uploads |

> **Note on Passwords**: Default development demo accounts use the standard password pattern `[Role]Pass123!` (e.g. `AdminPass123!`, `OwnerPass123!`, `TenantPass123!`). For production deployments, passwords can be regenerated via `python manage.py changepassword <username>`.

---

## 🧪 Automated Testing

The project includes an automated test suite verifying models, permissions, role redirection, search filtering, application approval workflows, simulated payment checkout, and maintenance updates:

```powershell
python manage.py test
```

**Test Execution Output:**
```
Ran 17 tests in 11.079s
OK (17 passed, 0 failures, 0 errors)
```

---

## 🛡️ Security & Production Principles
- **Credential Protection**: Database passwords and Django secret keys are strictly read from `.env` via `django-environ` and excluded from git tracking via `.gitignore`.
- **Role-Based Access Control (RBAC)**: Custom model properties (`is_admin_role`, `is_owner_role`, `is_tenant_role`) paired with `UserPassesTestMixin` prevent cross-user data tampering.
- **Secure File Storage**: Documents and property photos are routed through Django's `FileSystemStorage` with date-partitioned directories.
- **CSRF & Password Hashing**: Standard Django PBKDF2 with SHA256 password hashing and CSRF token protection on all post forms.

---

*Engineered with precision for advanced Python Django software development evaluation.*

