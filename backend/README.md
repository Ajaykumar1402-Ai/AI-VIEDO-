# 🚀 SIVACINE AI / NPTEL OAuth 2.0 Authentication & User Management Guide

This system implements **Google OAuth 2.0**, **GitHub OAuth 2.0**, **JWT Session Management**, **CSRF State Verification**, and **MySQL Database Integration** with parameterized queries and fallback store.

---

## 📁 Project Architecture & File Inventory

```
d:\VIDEO AI\
├── .gitignore             # Root git ignore (excludes .env and node_modules)
├── index.html             # SIVACINE AI Studio Web Interface
├── style.css              # Dark mode cinematic design system
├── app.js                 # Frontend studio engine & OAuth callback listener
├── serve-client.js        # Lightweight static frontend server (port 3000)
├── backend/
│   ├── .env               # Environment configuration with your secret keys
│   ├── .env.example       # Example configuration template
│   ├── .gitignore         # Backend git ignore (protects secrets)
│   ├── database.js        # MySQL connection pool & user data access layer
│   ├── package.json       # Express, MySQL2, JWT, Cookie-Parser, CORS dependencies
│   ├── server.js          # Production OAuth 2.0 Express/HTTP server (port 5000)
│   ├── test-oauth.js      # Automated test suite for all auth endpoints
│   └── README.md          # Complete documentation & setup instructions
```

---

## ⚡ Quick Start & Commands

### 1. Install Backend Dependencies
```bash
cd "d:\VIDEO AI\backend"
npm install
```

### 2. Start the Backend Server (Port 5000)
```bash
cd "d:\VIDEO AI\backend"
node server.js
```

### 3. Start the Frontend Web App (Port 3000)
```bash
cd "d:\VIDEO AI"
node serve-client.js
```

### 4. Run Automated Test Suite
```bash
cd "d:\VIDEO AI\backend"
node test-oauth.js
```

---

## 🔑 Google Cloud Console Configuration

To enable live Google Sign-In with your Google Client ID and Client Secret:

1. Visit the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
2. Create a new project (e.g. `SivaCine-AI-NPTEL`).
3. Navigate to **APIs & Services** → **OAuth consent screen**:
   - User Type: **External**
   - App Name: `SIVACINE AI`
   - User Support Email: your email
   - Scopes: `openid`, `.../auth/userinfo.email`, `.../auth/userinfo.profile`
4. Navigate to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**:
   - Application Type: **Web application**
   - Name: `SIVACINE Web Client`
   - **Authorized JavaScript origins**:
     - `http://localhost:3000`
     - `http://localhost:5000`
   - **Authorized redirect URIs**:
     - `http://localhost:5000/auth/google/callback`
5. Copy your **Client ID** and **Client Secret** into `d:\VIDEO AI\backend\.env`:

```env
PORT=5000
CLIENT_URL=http://localhost:3000
NODE_ENV=development
JWT_SECRET=sivacine_ai_super_secret_jwt_key_2026_cinema_filmmaker

GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_CALLBACK_URL=http://localhost:5000/auth/google/callback
```

---

## 🗄️ MySQL Database Migration Schema

The database module automatically creates the table upon startup if MySQL is configured in `.env`. You can also execute the following SQL migration in MySQL Workbench or phpMyAdmin:

```sql
CREATE DATABASE IF NOT EXISTS nptel_sivacine_db;
USE nptel_sivacine_db;

CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(64) PRIMARY KEY,
  provider VARCHAR(32) NOT NULL DEFAULT 'email',
  provider_id VARCHAR(128),
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  avatar TEXT,
  plan VARCHAR(64) DEFAULT 'Free',
  generations_remaining INT DEFAULT 2,
  email_verified TINYINT(1) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_email (email),
  INDEX idx_provider (provider, provider_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 🔄 Authentication Endpoints Reference

| Endpoint | Method | Scope / Query | Description |
| :--- | :--- | :--- | :--- |
| `/auth/google` | `GET` | `openid email profile` | Generates CSRF `state`, sets `oauth_state` cookie, redirects to Google |
| `/auth/google/callback` | `GET` | `code`, `state` | Validates CSRF state, exchanges token, checks `email_verified`, persists user in MySQL, signs JWT |
| `/auth/github` | `GET` | `read:user user:email` | Initiates GitHub OAuth authentication |
| `/auth/github/callback` | `GET` | `code`, `state` | Verifies GitHub code and profile, signs JWT |
| `/auth/me` | `GET` | `Authorization: Bearer <token>` | Returns authenticated user profile (401 if unauthorized) |
| `/auth/logout` | `POST` | - | Clears session cookie |
| `/auth/demo-login` | `POST` | `{ email, name }` | Instant local test sign-in |
| `/health` | `GET` | - | Health check and configuration status |

---

## 🛡️ Security Implementation Details

1. **CSRF State Verification**: Cryptographically random 48-char hex state tokens are generated using `crypto.randomBytes(24)` and stored in an HttpOnly cookie with a 10-minute TTL.
2. **Verified Email Enforcement**: Unverified email addresses from Google are strictly rejected (`email_verified === true`).
3. **No Credential Leaks**: Tokens, client secrets, and sensitive error stacks are never exposed in browser URLs or client responses.
4. **Parameterized Queries**: All database queries use SQL placeholders (`?`) to prevent SQL injection vulnerabilities.
5. **Safe Error Handling**: Cancelled logins (`access_denied`) and expired states redirect smoothly back to the login modal with friendly status messages.
