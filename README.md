# FoodFlow — Expiry-Aware Food Donation Platform
**University CSE Lab Project (Team of 4 Members)**

FoodFlow is a beginner-friendly full-stack Django web application designed to connect food donors (restaurants, households, grocers, caterers) with verified recipients (charities, shelters, and individuals in need) to rescue surplus food before it expires. The system features real-time remaining shelf-life countdowns, local area matching notifications, race-condition safe food reservations, and secure 8-character verification codes for physical handovers.

---

## 🌟 Key Features

1. **Role-Based Access Control & Dual Login**: Separate dashboards, workflows, and permissions for Food Donors, Recipients, and Platform Administrators. Login supports both registered **username** and **email address**.
2. **Full Name Personalization**: Users provide their Full Name upon registration, displayed across navigation, dashboards, and personalized greetings.
3. **Clean Address Handling**: Locations are organized strictly by Street Address, Area/Neighborhood, and City (Dhaka, etc.) without postal code complexity.
4. **Simple Password Rules**: Simplified beginner-friendly password validation (`password == password_confirm`) with secure password hashing (`PBKDF2`).
5. **Secure Authentication Requirements**: Guests see only **Home**, **Login**, and **Register**. All claim tracking, food reservations, and dashboards require authentication.
6. **Live Remaining Time Countdown**: Client-side JavaScript countdown dynamically displays remaining shelf life until `expires_at`. Expired food automatically disables the claim button.
7. **Manual Quantity Typing**: Decimal inputs (`inputmode="decimal"`) allow users to type exact amounts without confusing number spinners, steppers, or wheel interactions.
8. **Area-Based Recipient Notifications**: Automatically alerts matching verified recipients in the same neighborhood or city when surplus food is posted.
9. **Race-Condition Safe Claiming**: Concurrency-protected claiming using database row-locking (`select_for_update`) and atomic transactions (`transaction.atomic`).
10. **8-Character Pickup Verification Code**: Unique cryptographic token generated for the recipient and verified by the donor during physical handover.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.14+, Django 5.x (Django ORM, Authentication, Function-Based Views)
- **Database**: SQLite3 for simple local development
- **Static Files**: WhiteNoise (`CompressedStaticFilesStorage`)
- **Frontend**: HTML5, Plain CSS3 (Responsive Grid & Custom Variables), Vanilla JavaScript (No React, Vue, TypeScript, Tailwind, or npm build tools)

---

## 📂 Project Structure

```text
FoodFlow-1/
├── manage.py                          # Django command-line runner
├── requirements.txt                   # Minimal project dependencies
├── README.md                          # Documentation, team split & viva guide
├── db.sqlite3                         # Local SQLite database
│
├── config/                            # Root project configuration
│   ├── settings.py                    # Settings (AUTH_PASSWORD_VALIDATORS = [], etc.)
│   ├── urls.py                        # Root URL routing
│   └── wsgi.py                        # WSGI entrypoint
│
├── accounts/                          # User accounts, authentication & profiles
│   ├── models.py                      # User (AbstractUser with full_name), Donor, Recipient
│   ├── forms.py                       # UserRegistrationForm (full_name required), UserLoginForm, ProfileUpdateForm
│   ├── views.py                       # register_view, login_view, logout_view, profile_view, dashboards
│   ├── urls.py                        # Account routes (/register/, /login/, etc.)
│   ├── admin.py                       # Admin verification actions (verify/unverify donors & recipients)
│   ├── tests.py                       # Auth & profile test suite
│   └── management/commands/
│       └── seed_foodflow_demo.py      # Demo dataset seeder
│
├── locations/                         # Physical address management & geo-matching
│   ├── models.py                      # Location model (address, area, city)
│   ├── services.py                    # LocationMatchingService (area/city matching)
│   ├── forms.py                       # LocationForm
│   ├── admin.py                       # Location admin configuration
│   └── tests.py                       # Matching service tests
│
├── listings/                          # Food listings & expiry checks
│   ├── models.py                      # FoodListing (available, claimed, completed, expired)
│   ├── services.py                    # ExpiryService (mark expired listings)
│   ├── forms.py                       # FoodListingForm (manual decimal quantity input)
│   ├── views.py                       # Donor management & Recipient browse views
│   ├── admin.py                       # FoodListingAdmin
│   ├── tests.py                       # Listing & expiry tests
│   └── management/commands/
│       └── expiry_sweep.py            # Management command for expired food sweep
│
├── claims/                            # Food reservation & pickup verification
│   ├── models.py                      # Claim model (8-character unique pickup_code)
│   ├── services.py                    # ClaimService (atomic locking & handovers)
│   ├── forms.py                       # ClaimForm (manual decimal quantity) & PickupVerificationForm
│   ├── views.py                       # @login_required claims views (create, list, cancel, verify)
│   ├── admin.py                       # ClaimAdmin
│   └── tests.py                       # Claim & pickup test suite
│
├── notifications/                     # In-app notifications
│   ├── models.py                      # Notification model
│   ├── services.py                    # NotificationService
│   ├── views.py                       # Notification list & unread count JSON
│   └── admin.py                       # NotificationAdmin
│
├── templates/                         # Django HTML templates
│   ├── base.html                      # Main layout template
│   ├── home.html                      # Landing page with live impact stats
│   ├── partials/                      # Reusable navbar, alerts, and footer
│   ├── accounts/                      # Register, login, profile, dashboards
│   ├── listings/                      # Cards, forms, browse, detail pages
│   ├── claims/                        # My claims, claim detail, pickup verify
│   └── notifications/                 # In-app notification center
│
└── static/                            # Static CSS and Vanilla JS assets
    ├── css/styles.css                 # Responsive styling & design system
    ├── js/countdown.js                # Live dynamic countdown timer
    └── js/claims.js                   # Double-submit guard & confirmation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed
- Virtual environment activated

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Seed Demo Dataset
```bash
python manage.py seed_foodflow_demo
```
This initializes demo accounts:
- **Admin**: `admin` / `admin123`
- **Verified Donor**: `greengarden` / `donor123`
- **Verified Recipient**: `hopefoundation` / `recipient123`
- **Unverified Recipient**: `john_doe` / `recipient123`

### 5. Run Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

### 6. Run Automated Test Suite
```bash
python manage.py test
```
All 39 unit and integration tests run in ~18 seconds and pass with 100% success.

---

## 👥 4-Member Student Team Work Split

| Member | Primary Modules & Responsibilities | Key Code Files |
| :--- | :--- | :--- |
| **Member 1** (Team Lead & Auth) | Custom User model, Role profiles, Authentication (Username/Email dual login), Registration with Full Name, and Admin verification. | `accounts/models.py`, `accounts/views.py`, `accounts/forms.py`, `accounts/admin.py` |
| **Member 2** (Listings & Expiry) | FoodListing models, manual quantity decimal forms, `ExpiryService`, background `expiry_sweep` command, and browse views. | `listings/models.py`, `listings/views.py`, `listings/forms.py`, `listings/services.py` |
| **Member 3** (Claims & Security) | Claim reservation workflow, race condition protection (`select_for_update`), 8-character pickup code generation and donor verification. | `claims/models.py`, `claims/views.py`, `claims/forms.py`, `claims/services.py` |
| **Member 4** (UI, Locations & Notifications) | Responsive templates, design system (`styles.css`), Vanilla JS countdown timer, Location model and in-app notifications. | `templates/`, `static/css/`, `static/js/`, `locations/`, `notifications/` |

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
