# FoodFlow: Expiry-Aware Food Rescue and Distribution Platform

> **University CSE Capstone Project**  
> An enterprise-grade web application engineered to optimize the perishable food supply chain and eliminate edible food waste in urban environments.

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.0+-092E20?style=flat-square&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Database-PostgreSQL_%7C_SQLite-336791?style=flat-square&logo=postgresql&logoColor=white" alt="Database">
  <img src="https://img.shields.io/badge/Tests-39_Passing_(100%25)-2EA043?style=flat-square" alt="Tests">
  <img src="https://img.shields.io/badge/Deployment-Vercel_Serverless-000000?style=flat-square&logo=vercel&logoColor=white" alt="Vercel">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="License">
</p>

---

## 1. Abstract

FoodFlow is a full-stack, event-driven web application designed to bridge the logistical gap between surplus food generators (restaurants, caterers, households) and verified charitable organizations. In high-density urban environments, the primary barrier to food rescue is the high perishability of cooked meals and the latency of traditional coordination methods.

FoodFlow addresses this through an **expiry-aware donation pipeline**. The system utilizes real-time client-side telemetry, geospatial filtering, and strict database concurrency controls to ensure that surplus food is claimed, routed, and physically verified before its biological shelf-life expires.

---

## 2. Core Engineering Capabilities

### 2.1 Concurrency & Data Integrity
*   **Race-Condition Mitigation**: Implements database row-level locking (`select_for_update`) within atomic transactions to prevent the "lost update" problem and eliminate inventory overclaiming during high-concurrency access.
*   **Cryptographic Handover Verification**: Generates secure, 8-character alphanumeric tokens for physical collections. This ensures chain-of-custody integrity and prevents unauthorized food diversion.
*   **Automated State Sweeping**: Background expiry services systematically transition listings from `ACTIVE` to `EXPIRED` states, enforcing strict temporal boundaries on donations.

### 2.2 Geospatial & Temporal Routing
*   **Dynamic Shelf-Life Telemetry**: Utilizes Vanilla JavaScript to calculate and render real-time countdowns based on server-side UTC expiry timestamps, automatically disabling claim interfaces upon expiration.
*   **Proximity-Based Notifications**: An event-driven notification service instantly alerts verified recipients operating within the same localized zone (e.g., specific neighborhoods or districts).

### 2.3 System Architecture & Access Control
*   **Strict Role-Based Access Control (RBAC)**: Enforces isolated workflows, dashboard views, and API permissions for three distinct system actors: **Donors**, **Recipients**, and **Administrators**.
*   **Dual-Factor Authentication Vectors**: Supports universal login protocols accepting either unique usernames or registered email addresses.
*   **Precision Quantity Inputs**: Overrides standard browser UI components to enforce manual decimal inputs (`inputmode="decimal"`), ensuring exact mass/volume tracking (e.g., `2.5 kg`) without UI friction.

---

## 3. Academic & Engineering Merit (Capstone Highlights)

*For academic defense and technical evaluation, this project demonstrates proficiency in the following advanced engineering concepts:*

1.  **Transactional Isolation**: Demonstration of PostgreSQL/SQLite transaction management using Django's `transaction.atomic()` to maintain ACID properties during concurrent claim requests.
2.  **Serverless Filesystem Adaptation**: Architectural modifications to Django's `wsgi.py` and media handling to support ephemeral, read-only serverless environments (e.g., Vercel), including dynamic environment variable injection and automated migration hooks.
3.  **Stateless Session Management**: Utilization of secure, cryptographically signed session cookies and CSRF token validation to prevent cross-site request forgery in a multi-tenant environment.
4.  **Comprehensive Test Automation**: A robust suite of 39 unit and integration tests achieving a 100% pass rate, validating ORM logic, view routing, and form validation constraints.

---

## 4. Technology Stack

| Architectural Layer | Technologies & Frameworks |
| :--- | :--- |
| **Backend Logic** | Python 3.12+, Django 5.x (ORM, Function-Based Views, Middleware) |
| **Data Persistence** | PostgreSQL (Production via Neon), SQLite3 (Local/Ephemeral) |
| **Asset Management** | WhiteNoise (`CompressedStaticFilesStorage`), Pillow (Image Processing) |
| **Frontend Presentation** | HTML5, CSS3 (Custom Design System via CSS Variables), Vanilla JavaScript |
| **Infrastructure** | Vercel (Serverless Python Runtime with Edge CDN) |

---

## 5. Repository Structure

```text
FoodFlow/
├── manage.py                 # Django CLI utility
├── requirements.txt          # Pinned production dependencies
├── vercel.json               # Serverless routing and build configuration
├── build_files.sh            # CI/CD build script for serverless environments
│
├── config/                   # Global project settings, WSGI entry, and root routing
├── accounts/                 # Custom User models, RBAC, and authentication workflows
├── locations/                # Geospatial models and neighborhood matching services
├── listings/                 # Inventory management, temporal expiry logic, and media handling
├── claims/                   # Transactional claim processing and cryptographic verification
├── notifications/            # Event-driven alert system and unread state tracking
├── templates/                # DRY HTML architecture (Base layouts, partials, app views)
├── static/                   # Minified CSS design systems and client-side JS logic
└── media/                    # Secure directory for user-uploaded photographic evidence
