# 🚀 FoodFlow Vercel Deployment Guide

This guide explains how to deploy **FoodFlow** to [Vercel](https://vercel.com/) with zero configuration issues.

---

## 📋 What Has Been Configured

1. **Vercel Framework Configuration (`vercel.json`)**:
   - Configured with the modern `"framework": "django"` preset and automatic `collectstatic` execution.
2. **Vercel Entrypoint Discovery (`pyproject.toml`)**:
   - Declares `[tool.vercel] entrypoint = "config.wsgi:application"`.
3. **Python Runtime (`.python-version`)**:
   - Pinned to **Python 3.12** for stability and pre-built binary wheel support.
4. **Static & Media Serving**:
   - Static files are compressed and cached via **WhiteNoise** and served globally through Vercel's Edge CDN.
   - Media photos are automatically copied to `/tmp/media` on Vercel so they remain readable and writable in serverless environments.
5. **CSRF & Security**:
   - Automatically trusts dynamic `*.vercel.app` domains and any custom domains specified in `CSRF_TRUSTED_ORIGINS`.
6. **Dual Database Architecture**:
   - **Out of the box**: Runs immediately with pre-seeded demo users and listings using SQLite copied to `/tmp/db.sqlite3`.
   - **Production PostgreSQL**: If you provide `DATABASE_URL` (e.g. from free [Neon.tech](https://neon.tech) or [Supabase](https://supabase.com)), FoodFlow connects directly to Postgres.
   - **Auto-Migration Hook**: If `AUTO_MIGRATE=true` is set, FoodFlow runs `python manage.py migrate` automatically on startup.

---

## 🛠️ Step-by-Step Deployment Instructions

### Step 1: Push your Code to GitHub

1. In your local project directory (or IDE terminal), stage and commit all files:
   ```bash
   git add .
   git commit -m "Configure FoodFlow for Vercel deployment"
   ```

2. Create a new repository on [GitHub](https://github.com/new) named `FoodFlow-web`.

3. Link and push your repository:
   ```bash
   git remote add origin https://github.com/<your-username>/FoodFlow-web.git
   git branch -M main
   git push -u origin main
   ```

---

### Step 2: Import into Vercel

1. Log in to [Vercel.com](https://vercel.com/).
2. On your dashboard, click **"Add New..."** &rarr; **"Project"**.
3. Select your GitHub repository **`FoodFlow-web`** and click **"Import"**.
4. In the Project Configuration screen:
   - **Framework Preset**: Vercel will automatically detect **Django**.
   - **Root Directory**: `./` (leave default).
   - **Build Command**: Automatically detected (`python manage.py collectstatic --noinput`).
   - **Output Directory**: Automatically handled by Vercel.

---

### Step 3: Configure Environment Variables (Optional but Recommended)

Under the **Environment Variables** section, you can add:

| Name | Recommended Value | Notes |
| :--- | :--- | :--- |
| `DJANGO_SECRET_KEY` | *(Generate a 50-character random string)* | Used for cryptographic session signing. |
| `DEBUG` | `False` | Set `True` if you are debugging, `False` for production. |
| `DATABASE_URL` | `postgres://user:pass@ep-cool.neon.tech/neondb?sslmode=require` | *(Optional)* Free cloud PostgreSQL from [Neon.tech](https://neon.tech). If omitted, FoodFlow uses pre-seeded SQLite in `/tmp`. |
| `AUTO_MIGRATE` | `true` | *(Optional)* If using `DATABASE_URL`, automatically runs database migrations on first start. |
| `SEED_DEMO` | `true` | *(Optional)* Seeds demo accounts and listings into your Postgres database. |

---

### Step 4: Click "Deploy"

1. Click the **"Deploy"** button.
2. Vercel will:
   - Install Python 3.12 dependencies (`requirements.txt`).
   - Collect static assets (`collectstatic`).
   - Provision serverless function runtime for `config.wsgi:application`.
3. Within 1–2 minutes, your deployment will be live!

---

## 👥 Demo Logins for Testing on Vercel

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin` | `admin123` | Access `/admin/` and full platform control |
| **Verified Food Donor** | `greengarden` | `donor123` | Can post food listings, manage claims & verify handovers |
| **Verified Recipient NGO** | `hopefoundation` | `recipient123` | Can claim available food and view pickup codes |
| **Individual Recipient** | `john_doe` | `recipient123` | Individual account |

---

## 💡 Troubleshooting & Tips

- **Static Files Not Loading?**
  WhiteNoise is integrated and pre-configured. Vercel's Edge CDN will serve static assets from `/static/`.
- **403 CSRF Verification Failed?**
  FoodFlow dynamically whitelists `https://*.vercel.app` and `VERCEL_URL`. If using a custom domain (e.g. `foodflow.org`), add it to the `CSRF_TRUSTED_ORIGINS` environment variable.
- **Want Permanent Cloud Storage for Postgres?**
  Create a free project at [Neon.tech](https://neon.tech), copy your connection string, paste it as `DATABASE_URL` in Vercel, set `AUTO_MIGRATE=true`, and redeploy.
