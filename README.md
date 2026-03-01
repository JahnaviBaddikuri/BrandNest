<p align="center">
  <img src="frontend/nature_14835036.png" alt="BrandNest Logo" width="80" height="80">
</p>

<h1 align="center">BrandNest</h1>

<p align="center">
  <strong>A Full-Stack Influencer Marketing Marketplace</strong><br>
  Connecting brands with creators across Instagram, TikTok, YouTube & UGC
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.3-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT">
  <img src="https://img.shields.io/badge/REST-API-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="REST API">
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5">
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3">
  <img src="https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript">
</p>

---

## Overview

**BrandNest** is a production-ready influencer marketing platform that manages the **complete lifecycle** of brand-creator collaborations — from discovery and outreach to campaign execution, order tracking, and reviews. Built with a clean RESTful API backend and a modern, responsive frontend.

---

## Key Features

### 🔐 Authentication & Security
- **Dual registration flows** — separate onboarding for Creators and Brands
- **JWT-based authentication** (HS256) with 7-day token expiry
- **Bcrypt password hashing** with automatic salting
- **Email verification** via 4-digit OTP (5-min expiry, one-time use)
- **Password reset flow** with OTP — doesn't reveal whether email exists
- **Role-based access control** — decorators enforce permissions per user type
- **Admin API key authentication** — separate auth layer for platform administration

### 👥 User Management
- **Creator profiles** — platform, category, rate, followers, engagement rate, bio, profile image
- **Brand profiles** — company name, industry, location, website, logo upload
- **Profile image uploads** — secure handling with UUID naming & extension whitelist
- **Admin verification system** — trust badges for approved creators and brands
- **Cascade account deletion** — removes all related data (orders, reviews, messages, etc.)

### 📢 Campaign System
- **Campaign creation & management** by brands — title, description, budget, platform targeting
- **Advanced filtering** — by status, platform, category, min followers, budget range
- **Campaign applications** — creators apply with proposed rates and cover messages
- **Application review** — brands accept/reject with auto-contact-request on acceptance

### 💬 Messaging System
- **Contact-request-gated messaging** — prevents spam, requires mutual consent
- **Conversation threads** — grouped by partner with unread counts
- **Auto-read marking** — messages marked read when conversation is opened
- **Unread count tracking** — real-time badge indicator support

### 📦 Order Management
- **Full order lifecycle** — pending → accepted → in_progress → delivered → completed
- **Role-based status transitions** — brands and creators have different allowed actions
- **Deliverables tracking** — JSON-based deliverable specifications per order
- **Deadline management** — due dates with status workflow enforcement
- **Revision & cancellation flows** — built into the status state machine

### ⭐ Reviews & Ratings
- **Bidirectional reviews** — both brands and creators can rate each other
- **1.0–5.0 rating scale** with optional comments
- **One review per user per order** — duplicate prevention
- **Public average ratings** — aggregated per user with reviewer attribution

### 🔔 Notification System
- **Real-time notifications** for contact requests, messages, applications, orders & reviews
- **Unread count endpoint** — for badge/indicator support
- **Bulk read operations** — mark single or all notifications as read
- **Polymorphic design** — serves both user types from a single table

### 🛡️ Admin Dashboard
- **User verification panel** — approve pending creators and brands
- **Platform statistics** — totals, verified users, pending approvals
- **Dedicated admin authentication** via API key header

---

## Architecture

```
BrandNest/
├── backend/
│   ├── app.py                 # Flask app factory & blueprint registration
│   ├── config.py              # Environment-based configuration
│   ├── models.py              # SQLAlchemy ORM models (8 models)
│   ├── jwt_auth.py            # JWT token generation & @require_auth decorator
│   ├── email_service.py       # SMTP email service (OTP, welcome, notifications)
│   ├── otp_utils.py           # OTP generation & validation
│   ├── password_utils.py      # Bcrypt hashing utilities
│   ├── utils.py               # Shared helpers
│   ├── seed_data.py           # Database seeder for development
│   └── routes/
│       ├── auth.py            # Authentication endpoints (12 routes)
│       ├── creators.py        # Creator CRUD & search (6 routes)
│       ├── brands.py          # Brand CRUD & search (6 routes)
│       ├── campaigns.py       # Campaign management (6 routes)
│       ├── applications.py    # Campaign applications (5 routes)
│       ├── contact_requests.py # Contact request flow (4 routes)
│       ├── messages.py        # Messaging system (5 routes)
│       ├── orders.py          # Order management (4 routes)
│       ├── reviews.py         # Review system (3 routes)
│       ├── notifications.py   # Notification system (4 routes)
│       └── admin.py           # Admin panel (4 routes)
│
├── frontend/
│   ├── index.html             # Landing page with creator search
│   ├── login.html             # Role-based login
│   ├── join-creator.html      # Creator registration
│   ├── join-brand.html        # Brand registration
│   ├── verify-email.html      # OTP verification page
│   ├── dashboard.html         # User dashboard & profile management
│   ├── campaigns.html         # Campaign browsing & management
│   ├── messages.html          # Messaging interface
│   ├── orders.html            # Order tracking & management
│   ├── requests.html          # Contact request management
│   ├── admin.html             # Admin verification panel
│   ├── styles.css             # Main stylesheet
│   ├── auth.js                # Authentication & session management
│   └── app.js                 # Core application logic
│
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.x, Flask 2.3.3 |
| **Database** | SQLAlchemy 3.0.5 + SQLite |
| **Authentication** | PyJWT (HS256), Bcrypt (Werkzeug) |
| **Email** | Flask-Mail 0.9.1, SMTP |
| **API** | RESTful, 11 Blueprints, 57+ endpoints |
| **Frontend** | Vanilla HTML5, CSS3, ES6+ JavaScript |
| **Typography** | Google Fonts (Manrope, DM Mono) |
| **CORS** | Flask-CORS 4.0.0 |
| **Config** | python-dotenv, environment variables |

---

## Database Schema

**8 interconnected models** with full relational integrity:

| Model | Description |
|-------|------------|
| **Creator** | Influencer profiles with platform, category, rate, engagement metrics |
| **Brand** | Company profiles with industry, website, verification status |
| **Campaign** | Brand-created campaigns with targeting criteria & budget |
| **Application** | Creator applications to campaigns with proposed rates |
| **ContactRequest** | Brand-to-creator outreach with accept/reject flow |
| **Message** | Polymorphic messaging between any two users |
| **Order** | Collaboration orders with deliverables, pricing & status workflow |
| **Review** | Bidirectional ratings (1–5) on completed orders |
| **Notification** | Polymorphic per-user notifications with read tracking |

---

## API Endpoints

> **57+ RESTful endpoints** across 11 route blueprints

| Module | Endpoints | Highlights |
|--------|-----------|-----------|
| **Auth** | 12 | Register, login, OTP verify, password reset, profile updates |
| **Creators** | 6 | CRUD, search with filtering, image upload |
| **Brands** | 6 | CRUD, industry filtering, logo upload |
| **Campaigns** | 6 | Create, browse, filter by platform/category/budget |
| **Applications** | 5 | Apply, review, auto-contact on acceptance |
| **Contact Requests** | 4 | Send, view, accept/reject |
| **Messages** | 5 | Conversations, threads, unread counts |
| **Orders** | 4 | Create, track, role-based status transitions |
| **Reviews** | 3 | Create, per-user aggregation, per-order lookup |
| **Notifications** | 4 | Fetch, unread count, mark read |
| **Admin** | 4 | Verify users, platform stats |

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/brandnest.git
   cd brandnest
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your values:
   ```env
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   SECRET_KEY=your-secret-key
   ADMIN_API_KEY=your-admin-key
   ```

4. **Initialize the database**
   ```bash
   python seed_data.py    # Optional: populate with sample data
   ```

5. **Run the server**
   ```bash
   python app.py
   ```
   The API will be available at `http://localhost:5000`

6. **Open the frontend**
   
   Open `frontend/index.html` in your browser, or serve it with any static file server.

---

## Security Highlights

| Feature | Implementation |
|---------|---------------|
| Password Storage | Bcrypt hashing with automatic salting |
| Token Auth | JWT HS256 with configurable expiry |
| Email Verification | Time-limited OTP, single-use, cleared after validation |
| File Uploads | UUID naming, extension whitelist, secure filename sanitization |
| Access Control | Role-based decorators, ownership verification on all mutations |
| Admin Security | Separate API key authentication channel |
| Data Privacy | Password reset doesn't leak email existence |
| Account Deletion | Full cascade — removes all user data across all tables |

---

## Design Decisions

- **Contact-request-gated messaging** — prevents unsolicited spam between users
- **Auto-contact on application accept** — streamlines the brand-creator connection flow
- **Role-based status machine** — ensures logical order workflow (creators deliver, brands approve)
- **Polymorphic messaging & notifications** — single tables serve both user types cleanly
- **Bidirectional reviews** — builds trust on both sides of the marketplace
- **Deprecation over deletion** — old endpoints return `410 Gone` instead of breaking silently

---

## Screenshots

> *Coming soon — the frontend features a modern gradient-based design with responsive layouts*

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

