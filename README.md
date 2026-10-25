# FoodFlow — Expiry-Aware Food Donation Platform
> **University CSE Lab & Capstone Project (Team of 4 Members)**  
> *Connecting surplus food donors with verified local charities before food expires.*

![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Vercel Ready](https://img.shields.io/badge/Vercel-Deployed-black?style=for-the-badge&logo=vercel&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-39%20Passing%20(100%25)-success?style=for-the-badge)
![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-blue?style=for-the-badge)

---

## 📖 Overview

**FoodFlow** is a full-stack Django web application designed to eliminate edible food waste in urban communities. In cities like Dhaka, restaurants, caterers, and households generate substantial surplus meals daily, while shelters, orphanages, and families in need face shortages.

Traditional charities struggle because cooked food is highly perishable. FoodFlow bridges this gap with an **expiry-aware donation pipeline**:
- Donors list food with an **exact expiration deadline**.
- Real-time client-side **countdowns** highlight urgency.
- Verified recipients in the **same neighborhood or city** receive instant in-app alerts.
- High-concurrency **database row-locking (`select_for_update`)** prevents double-booking.
- An **8-character physical handover code** guarantees safe, verified collections.

---

## 🌟 Key Features

1. **Role-Based Access Control & Dual Login**:
   - Distinct workflows, dashboards, and permissions for **Donors**, **Recipients**, and **Admins**.
   - Universal login supports both registered **username** and **email address**.
2. **Full Name Personalization**:
   - Users register with their Full Name, greeting them across navbars and dashboard views.
3. **Clean City & Neighborhood Addressing**:
   - Location management based strictly on Street Address, Area/Neighborhood (Dhanmondi, Gulshan, Banani, etc.), and City (Dhaka, etc.) without postal code hassles.
4. **Live Remaining Shelf-Life Countdown**:
   - Dynamic Vanilla JavaScript countdown timer. Expired food automatically disables the claim button in real time.
5. **Real Food Photo Galleries**:
   - High-quality, appetizing food photos for all listings with multiple photo uploads and thumbnail previews.
6. **Manual Quantity Typing**:
   - Decimal inputs (`inputmode="decimal"`) allow users to type exact amounts without confusing number spinners, steppers, or wheel interactions.
7. **Area-Based Recipient Notifications**:
   - Alerts nearby verified recipients in the same area or city when surplus food is posted.
8. **Race-Condition Safe Food Claiming**:
   - Database row-level locking (`select_for_update`) within atomic transactions ensures zero overclaiming even if multiple recipients claim the last portion concurrently.
9. **8-Character Pickup Verification Code**:
   - Cryptographically secure 8-character token (e.g. `4F9B2C1A`) issued to the recipient and verified by the donor during physical handover.
10. **Cloud & Serverless Ready (Vercel Native)**:
    - Pre-configured for seamless 1-click deployment on [Vercel](https://vercel.com/) with Edge CDN static caching and dual SQLite/PostgreSQL architecture.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend Framework** | Python 3.12+, Django 5.x (Django ORM, FBVs, CSRF Protection) |
| **Database** | SQLite3 (local & ephemeral serverless demo), PostgreSQL / Neon (production) via `dj-database-url` & `psycopg2-binary` |
| **Static & Media Files** | WhiteNoise (`CompressedStaticFilesStorage`), Pillow |
| **Frontend** | HTML5, Plain CSS3 (Design System & CSS Variables), Vanilla JavaScript (No React/Vue/Node build bloat) |
| **Cloud Deployment** | Vercel (Zero-Config Django Framework Preset with Fluid Compute) |

---

## 📂 Project Structure

```text
FoodFlow-web-main/
├── manage.py                          # Django management script
├── requirements.txt                   # Production dependencies (Django, whitenoise, Pillow, etc.)
├── pyproject.toml                     # Vercel entrypoint discovery specification
├── vercel.json                        # Modern Vercel Django framework configuration
├── .python-version                    # Python runtime lock (3.12)
├── build_files.sh                     # CI/CD & fallback build script
├── VERCEL_DEPLOYMENT_GUIDE.md         # Dedicated cloud deployment guide
├── db.sqlite3                         # Seeded database with demo users & listings
├── README.md                          # Full documentation & viva defense guide
│
├── config/                            # Root project configuration
│   ├── settings.py                    # Settings (CSRF, WhiteNoise, serverless MEDIA_ROOT)
│   ├── urls.py                        # Root URL router & /browse/ shortcut
│   └── wsgi.py                        # WSGI entrypoint with /tmp sync & AUTO_MIGRATE hook
│
├── accounts/                          # Custom User, Authentication & Roles
│   ├── models.py                      # User (AbstractUser), Donor, Recipient profiles
│   ├── forms.py                       # UserRegistrationForm, UserLoginForm, ProfileUpdateForm
│   ├── views.py                       # login_view, register_view, logout_view, dashboards
│   ├── urls.py                        # /login/, /register/, /profile/, /dashboard/
│   ├── admin.py                       # Verification action toggles
│   └── management/commands/
│       └── seed_foodflow_demo.py      # Demo dataset seeder with real food images
│
├── locations/                         # Address & Neighborhood Matching
│   ├── models.py                      # Location (address, area, city)
│   ├── services.py                    # LocationMatchingService (area/city filter)
│   └── forms.py                       # LocationForm
│
├── listings/                          # Surplus Food Listings & Expiry
│   ├── models.py                      # FoodListing (quantities, expiry status), FoodPhoto
│   ├── forms.py                       # FoodListingForm (manual decimal quantity input)
│   ├── services.py                    # ExpiryService (sweeps expired listings)
│   └── views.py                       # donor_listings_list, recipient_browse_view, photos
│
├── claims/                            # Food Reservations & Pickup Verification
│   ├── models.py                      # Claim model (8-character pickup_code)
│   ├── services.py                    # ClaimService (atomic select_for_update locking)
│   ├── forms.py                       # ClaimForm & PickupVerificationForm
│   └── views.py                       # create_claim, claim_detail, verify_pickup
│
├── notifications/                     # Real-time In-App Notifications
│   ├── models.py                      # Notification model
│   ├── services.py                    # NotificationService
│   └── views.py                       # notification_list, unread_notification_count_json
│
├── templates/                         # Django HTML Templates
│   ├── base.html                      # Global layout & header/footer
│   ├── home.html                      # Landing page with active impact metrics
│   ├── partials/                      # navbar.html, messages.html, footer.html
│   ├── accounts/                      # login, register, profile, dashboards
│   ├── listings/                      # browse, cards, detail, photo_gallery
│   └── claims/                        # my_claims, claim_detail, verify_pickup
│
├── static/                            # Static CSS and Vanilla JS
│   ├── css/styles.css                 # Responsive design system
│   ├── js/countdown.js                # Live dynamic countdown timer
│   ├── js/claims.js                   # Double-submit guard & validation
│   └── js/notifications.js            # Unread notifications badge polling
│
└── media/                             # Real uploaded food photos
    └── food_photos/2026/10/           # Chicken curry, sourdough, croissants, biryani, ramen
```

---

## ⚡ Quick Start (Local Development)

### 1. Prerequisites
- Python 3.10+ installed
- Virtual environment activated (recommended)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations & Seed Demo Data
```bash
python manage.py migrate
python manage.py seed_foodflow_demo
```

### 4. Start Local Development Server
```bash
python manage.py runserver
```
Visit **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

### 5. Run Automated Tests
```bash
python manage.py test
```
All **39 unit and integration tests** execute in seconds with 100% success rate.

---

## 🌐 Deploy to Vercel (Step-by-Step)

FoodFlow is completely configured for **zero-config Vercel deployment** with modern framework detection.

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Deploy FoodFlow to Vercel"
git remote add origin https://github.com/<your-username>/FoodFlow-web.git
git branch -M main
git push -u origin main
```

### Step 2: Import into Vercel
1. Go to [vercel.com](https://vercel.com) and log in.
2. Click **"Add New..."** &rarr; **"Project"**.
3. Select your **`FoodFlow-web`** GitHub repository and click **"Import"**.
4. Framework Preset will automatically display **Django**.
5. *(Optional)* Add Environment Variables:
   - `DJANGO_SECRET_KEY`: Enter any random 50-character string.
   - `DEBUG`: `False` (for production) or `True` (for testing).
   - `DATABASE_URL`: *(Optional)* Your PostgreSQL database URL (e.g. from free [Neon.tech](https://neon.tech)).
   - `AUTO_MIGRATE`: `true` *(if using PostgreSQL to auto-run migrations on boot)*.
6. Click **"Deploy"**.

Within 1–2 minutes, your project is live at `https://<project-name>.vercel.app`!

---

## 🔑 Demo Accounts for Viva & Evaluation

| Role | Username | Password | Purpose & Access |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin` | `admin123` | Full admin control at `/admin/`, verify NGOs/donors |
| **Verified Food Donor** | `greengarden` | `donor123` | Green Garden Bistro (post food, manage claims, verify handovers) |
| **Verified Recipient NGO** | `hopefoundation` | `recipient123` | Hope Foundation NGO (browse food, claim portions, view pickup code) |
| **Individual Recipient** | `john_doe` | `recipient123` | Individual recipient account in Banani |

---

## 🔗 Main Route Navigation

| URL Path | Name | Description |
| :--- | :--- | :--- |
| `/` | `home` | Landing page with platform stats & featured listings |
| `/browse/` | `browse_shortcut` | Quick redirect to active food browse catalog |
| `/recipient/food/` | `listings:browse_food` | Filter food by area/city, view photos & live countdown |
| `/login/` | `login` | Dual username or email authentication |
| `/register/` | `register` | User signup with role selection & Full Name |
| `/donor/dashboard/` | `accounts:donor_dashboard` | Donor management hub for listings & active claims |
| `/recipient/dashboard/` | `accounts:recipient_dashboard`| Recipient claim tracking & pickup codes |
| `/donor/pickups/verify/` | `claims:verify_pickup` | Enter 8-character code to confirm food handover |
| `/admin/` | `admin:index` | Django administrative interface |

---

## 👥 4-Member Student Team Work Split

| Member | Primary Modules & Responsibilities | Key Code Files |
| :--- | :--- | :--- |
| **Member 1** (Team Lead & Auth) | Custom User model, Role profiles, Authentication (Username/Email dual login), Registration with Full Name, and Admin verification. | `accounts/models.py`, `accounts/views.py`, `accounts/forms.py`, `accounts/admin.py` |
| **Member 2** (Listings & Expiry) | FoodListing models, manual quantity decimal forms, `ExpiryService`, background `expiry_sweep` command, real food images, and browse views. | `listings/models.py`, `listings/views.py`, `listings/forms.py`, `listings/services.py` |
| **Member 3** (Claims & Security) | Claim reservation workflow, race condition protection (`select_for_update`), 8-character pickup code generation and donor verification. | `claims/models.py`, `claims/views.py`, `claims/forms.py`, `claims/services.py` |
| **Member 4** (UI, Locations & Deployment) | Responsive templates, design system (`styles.css`), Vanilla JS countdown timer, Location model, in-app notifications, and Vercel cloud deployment. | `templates/`, `static/`, `locations/`, `notifications/`, `vercel.json`, `config/wsgi.py` |

---

## 🎓 Viva Presentation & Defense Guide

### 1. Project Motivation
> **Question**: *Why did you build FoodFlow and what problem does it solve?*  
> **Answer**:  
> In cities like Dhaka, restaurants and catered events generate significant edible food waste every day, while local shelters and charities struggle for resources. Traditional donation channels are too slow for perishable meals. FoodFlow solves this by focusing on **expiry-aware donations**: food is listed with an exact expiration time, matched to local charities in the same neighborhood, and protected with a live countdown timer and secure pickup verification code.

### 2. Custom User Model & Role-Based Access
> **Question**: *Why did you extend `AbstractUser` instead of using Django's default `User`?*  
> **Answer**:  
> Extending `AbstractUser` is the recommended Django best practice. It allowed us to add custom fields (`role`, `full_name`, `phone`) while retaining Django's built-in authentication, password hashing (`PBKDF2`), and session management. We then linked `Donor` and `Recipient` profiles using a `OneToOneField` with `on_delete=models.CASCADE`.

### 3. Preventing Overclaiming & Race Conditions
> **Question**: *What happens if two recipients attempt to claim the last 5 portions at the exact same millisecond?*  
> **Answer**:  
> In `claims/services.py`, the `create_claim` method runs inside `with transaction.atomic():` and uses `FoodListing.objects.select_for_update().get(pk=listing_id)`. This triggers SQL row-level locking (`SELECT ... FOR UPDATE`). The first transaction locks the row, validates that `quantity <= quantity_available`, saves the claim, and updates the listing. The second transaction must wait; when it acquires the lock, it re-evaluates `quantity_available` and raises a `ValidationError` ("Requested quantity exceeds available amount").

### 4. Physical Pickup Verification
> **Question**: *How do you prevent unauthorized individuals from collecting claimed food?*  
> **Answer**:  
> When a recipient reserves food, `ClaimService.generate_unique_pickup_code()` generates an 8-character token (e.g. `4F9B2C1A`). This code is displayed only to the claimant. When the recipient arrives at the donor's address, the donor enters this code at `/donor/pickups/verify/`. The system verifies donor ownership and marks the claim completed.

### 5. Why Function-Based Views (FBVs)?
> **Question**: *Why did your team choose Function-Based Views over Class-Based Views?*  
> **Answer**:  
> Function-Based Views are explicit, readable, and ideal for a student CSE lab project. Each step (handling `request.method`, checking `@login_required`, running form validation, calling service logic, and rendering templates) is written sequentially line by line, making it straightforward to debug, explain, and defend during viva examinations.

### 6. Serverless Deployment & Architecture on Vercel
> **Question**: *How does Django operate on Vercel's serverless environment given ephemeral storage?*  
> **Answer**:  
> Vercel executes serverless AWS Lambda containers with a read-only filesystem except for `/tmp`. We solved this through three architectural enhancements:
> 1. **Signed Cookie Sessions**: `SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'` ensures user sessions persist across stateless instances without local session tables.
> 2. **Static & Media Asset Delivery**: WhiteNoise handles asset compression and Vercel Edge CDN caches `/static/`, while `MEDIA_ROOT` synchronizes to writable `/tmp/media` and is served via Django's `serve` view.
> 3. **Dual Database Strategy**: Out of the box, `config/wsgi.py` synchronizes the pre-seeded SQLite database to `/tmp/db.sqlite3` for instant demo access, while production can connect to a managed PostgreSQL cluster (e.g. Neon) via `DATABASE_URL` with automated schema migrations via the `AUTO_MIGRATE=true` hook.
