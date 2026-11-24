# YMC & Associates — Work Tracker Enterprise

Modern, pro-level CA Practice ERP and compliance management web app with **Multi-ID & Password Authentication** and live **Neon PostgreSQL database integration**.

## 🚀 Instant Deployment (GitHub + Vercel)

### Step 1: Push to GitHub
1. Create a new repository on GitHub named `ymc-work-tracker`.
2. In this folder, initialize and push:
```bash
git init
git add .
git commit -m "Initial commit - YMC Work Tracker with Neon DB"
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/ymc-work-tracker.git
git push -u origin main
```

### Step 2: Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) and click **"Add New Project"**.
2. Select your `ymc-work-tracker` GitHub repository.
3. In **Environment Variables**, add:
   - **Name**: `DATABASE_URL`
   - **Value**: `postgresql://neondb_owner:npg_kSJ9La4cECpq@ep-little-hat-bkmnlplt-pooler.c-2.ap-southeast-2.aws.neon.tech/neondb?sslmode=require`
4. Click **Deploy**! 🚀

---

## 📱 Mobile App (APK / PWA) Feature
- **Direct 1-Click Install**: When you or any employee or client opens the deployed Vercel URL on an Android, iPhone, or PC, an **"Install App Now"** banner appears automatically.
- No Play Store or APK hassle required: It installs directly onto the home screen as a native-feeling app with standalone fullscreen view.

---

## 🔐 Default Access Accounts
| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Partner / Admin** | `admin` | `admin` | Full firm control, team management, security, database backup |
| **Senior / FCA** | `manager` | `manager` | Task assignments, reviewing filings & logs |
| **Article Assistant**| `rohit` | `staff` | Personal assignments, time logging |
| **Client Portal** | `client` | `client` | Exclusive view of their firm filings & compliances |
