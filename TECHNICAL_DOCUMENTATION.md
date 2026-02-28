# BrandNest - Influencer Marketing Platform
## Technical Documentation

---

## 1. PROJECT OVERVIEW

- **Project Name:** BrandNest - Influencer Marketing Platform
- **Project Type:** Full-stack web application for connecting brands with social media influencers
- **Development Period:** 2026
- **Architecture:** RESTful API-based client-server architecture with separate frontend and backend

### Purpose
- The platform serves as a marketplace where brands can discover and collaborate with influencers across multiple social media platforms (Instagram, TikTok, YouTube, UGC)
- Creators can showcase their profiles, set their rates, and connect with brands for collaboration opportunities
- The system facilitates influencer discovery and profile management with secure authentication

---

## 2. TECHNOLOGY STACK

### 2.1 Backend Technologies

#### Core Framework
- **Flask 2.3.3** - Lightweight Python web framework chosen for its simplicity, flexibility, and extensive ecosystem, making it ideal for RESTful API development
- **Python 3.x** - Primary programming language selected for its readability, extensive libraries, and strong support for web development

#### Database & ORM
- **SQLAlchemy 3.0.5** - SQL toolkit and Object-Relational Mapping (ORM) library chosen to provide database-agnostic approach and simplified database operations through Python objects
- **SQLite** - Embedded relational database selected for development due to its zero-configuration setup, portability, and sufficient capabilities for learning and testing environments
- **Flask-SQLAlchemy** - Integration extension that combines Flask with SQLAlchemy, providing convenient patterns for database operations

#### Authentication & Security
- **PyJWT 2.8.0** - JSON Web Token implementation for stateless authentication, chosen to enable scalable session management without server-side storage
- **Bcrypt (via Werkzeug 2.3.7)** - Password hashing algorithm used for secure password storage, implementing salted hash functions to prevent rainbow table attacks
- **Firebase Authentication** - Initially implemented for authentication services but later migrated to JWT-based custom authentication for better control and customization

#### Email Services
- **Flask-Mail 0.9.1** - Email sending extension integrated with SMTP protocols to handle transactional emails like OTP verification
- **SMTP (Gmail)** - Simple Mail Transfer Protocol configured with Gmail SMTP servers for reliable email delivery during development phase

#### Additional Backend Libraries
- **Flask-CORS 4.0.0** - Cross-Origin Resource Sharing extension to enable secure communication between frontend and backend hosted on different origins
- **python-dotenv 1.0.0** - Environment variable management library for secure configuration handling and separation of sensitive data from codebase
- **Werkzeug 2.3.7** - WSGI utility library providing secure filename handling, password hashing, and other security utilities

### 2.2 Frontend Technologies

#### Core Technologies
- **HTML5** - Modern semantic markup language used for structuring web pages with accessible and SEO-friendly content
- **CSS3** - Styling language implementing custom design system with modern features like flexbox, grid, and CSS variables for maintainable styling
- **Vanilla JavaScript (ES6+)** - Pure JavaScript without frameworks, chosen for better understanding of core concepts and optimal performance for application size

#### UI/UX Design
- **Custom CSS Architecture** - Modular CSS files (styles.css, auth.css, dashboard.css) organized by functionality for better maintainability
- **Google Fonts (Manrope, DM Mono)** - Typography system using professional web fonts for enhanced visual hierarchy and readability
- **Responsive Design** - Mobile-first approach with media queries ensuring optimal experience across devices
- **CSS Grid & Flexbox** - Modern layout systems for creating flexible and responsive component structures

#### Frontend Patterns
- **MVC Pattern** - Separation of concerns with distinct files for different pages (auth.js for authentication, app.js for main functionality)
- **RESTful API Integration** - Fetch API for asynchronous HTTP requests enabling smooth user experience without page reloads
- **Session Management** - LocalStorage for client-side token storage and user session persistence
- **Form Validation** - Client-side validation with real-time error messaging to improve user experience before server-side validation

### 2.3 Development Tools & Environment

- **Git** - Version control system for tracking changes, collaboration, and maintaining code history
- **VS Code** - Primary code editor with integrated terminal and debugging capabilities
- **PowerShell** - Command-line interface for running development servers and managing dependencies
- **pip** - Python package manager for installing and managing backend dependencies

### 2.4 Why These Technologies?

#### Backend Choice Reasoning
- **Flask over Django:** Flask was chosen for its minimalist approach, allowing learning of core web concepts without framework abstractions while providing flexibility to add only needed components
- **SQLAlchemy over raw SQL:** ORM approach provides database abstraction, prevents SQL injection attacks, and makes database operations more Pythonic and maintainable
- **JWT over session-based auth:** Stateless authentication enables better scalability, allows frontend-backend separation, and eliminates server-side session storage needs

#### Frontend Choice Reasoning
- **Vanilla JavaScript over React/Vue:** Pure JavaScript helps understand fundamental concepts without framework learning curve, reduces application bundle size, and provides complete control over implementation
- **Custom CSS over Bootstrap:** Building custom styles develops better understanding of CSS, creates unique design identity, and avoids framework bloat
- **Modular architecture:** Separate JS files for different functionalities improve code organization, maintainability, and allow selective loading

---

## 3. DATABASE SCHEMA

### 3.1 Creators Table
- **Purpose:** Stores influencer/creator profiles with their social media details and service rates
- **Primary Key:** `id` (Integer, Auto-increment)
- **Unique Constraints:** `username`, `email` for preventing duplicate accounts
- **Key Fields:**
  - Authentication: `email`, `password_hash`, `email_verified`, `otp_code`, `otp_expiry`
  - Profile: `username`, `bio`, `location`, `profile_image_url`
  - Platform Details: `platform` (Instagram/TikTok/YouTube/UGC), `category` (Fashion/Beauty/Fitness/etc.)
  - Metrics: `followers_count`, `engagement_rate`, `rate` (pricing per post)
  - Verification: `is_verified` (platform verification), `email_verified` (email confirmation)
  - Timestamps: `created_at`, `updated_at` for audit trail
- **Indexes:** Email field indexed for faster authentication lookups

### 3.2 Brands Table
- **Purpose:** Stores company/brand profiles seeking influencer collaborations
- **Primary Key:** `id` (Integer, Auto-increment)
- **Unique Constraints:** `company_name`, `email` to prevent duplicate brand registrations
- **Key Fields:**
  - Authentication: `email`, `password_hash`, `email_verified`, `otp_code`, `otp_expiry`
  - Company Info: `company_name`, `industry`, `website`, `location`, `logo_url`
  - Verification: `verified` (admin verification), `email_verified` (email confirmation)
  - Timestamps: `created_at`, `updated_at`
- **Indexes:** Email field indexed for authentication efficiency

### 3.3 Database Design Decisions
- **Normalization:** Tables follow 3rd Normal Form (3NF) to eliminate data redundancy and ensure data integrity
- **Cascade Deletes:** Implemented to maintain referential integrity when parent records are deleted
- **Timestamps:** All tables include created_at and updated_at for complete audit trail and debugging
- **Soft Deletes:** Not implemented currently but status fields allow marking records as inactive instead of deletion
- **Indexing Strategy:** Email fields indexed for frequent authentication queries, foreign keys automatically indexed for join operations

---

## 4. FEATURES IMPLEMENTED

### 4.1 User Authentication System

#### Dual Role Registration
- **Separate registration flows** for Creators and Brands with role-specific form fields ensuring data relevance for each user type
- **Client-side validation** with real-time error messaging prevents invalid data submission and improves user experience
- **Password strength validation** enforces minimum 6-character requirement with hashing using Bcrypt algorithm before database storage
- **Email uniqueness check** prevents duplicate accounts and provides clear error messages when email already exists

#### JWT-Based Authentication
- **Stateless token generation** upon successful login with 168-hour (7-day) expiration configurable through environment variables
- **Token payload includes** user ID, email, and role (creator/brand) enabling role-based access control without database queries
- **Authorization header** implementation using Bearer token scheme for API requests requiring authentication
- **Token verification middleware** (@require_auth decorator) validates tokens before allowing access to protected endpoints

#### Session Management
- **LocalStorage-based** client-side session storage maintains user login state across page refreshes
- **Automatic token inclusion** in authenticated requests through custom fetch wrapper function
- **Session expiry handling** with automatic redirect to login when token expires (401 response)
- **Role-based routing** redirects users to appropriate dashboards based on their role after successful authentication

#### Firebase Integration (Historical)
- **Initial authentication** was implemented using Firebase Authentication for rapid prototyping and built-in security features
- **Migration to custom JWT** was performed to gain better control over authentication flow, reduce external dependencies, and customize token payload

### 4.2 Email Verification with OTP

#### OTP Generation & Delivery
- **4-digit numeric OTP** generation using Python's random module for balance between security and user convenience
- **5-minute expiration** implemented using datetime comparisons to prevent OTP reuse and enhance security
- **SMTP email integration** with Gmail servers sends professional verification emails with OTP code to user's registered email
- **Fallback to console logging** when email delivery fails during development, ensuring testing can continue without email setup

#### Verification Flow
- **Registration creates unverified account** with email_verified flag set to False, preventing login until verification complete
- **Dedicated verification page** with clean 4-digit OTP input field providing focused user experience
- **Unlimited retry attempts** currently implemented to facilitate learning and testing (can be rate-limited in production)
- **Status persistence** using sessionStorage to maintain verification context when user navigates between pages

#### Security Features
- **One-time use validation** clears OTP from database after successful verification preventing reuse attacks
- **Expiry enforcement** automatically invalidates OTP after 5 minutes requiring new OTP generation
- **Invalid OTP handling** provides clear error messages without revealing whether OTP exists or is expired
- **Email verification requirement** blocks login attempts for unverified accounts with appropriate error messaging

#### Resend OTP Capability
- **Manual resend button** allows users to request new OTP if email wasn't received or OTP expired
- **Previous OTP invalidation** when new OTP generated ensures only latest code is valid
- **No cooldown period** currently for ease of testing but can be enhanced with rate limiting
- **Consistent email delivery** through same SMTP pipeline as initial registration

### 4.3 Profile Management

#### Creator Profiles
- **Profile image upload** with file validation (JPG/PNG/WebP formats) and secure filename handling using Werkzeug's secure_filename
- **Unique storage path** generation using UUID to prevent filename conflicts and enable CDN integration
- **Static file serving** through Flask route (/uploads/) makes uploaded images accessible via public URLs
- **Profile customization** includes bio, location, platform selection, category, follower count, engagement rate, and pricing

#### Brand Profiles
- **Company logo upload** with identical security measures as creator profile images for consistency
- **Separate storage directory** (uploads/brands/) organizes files by user type for better file management
- **Company information** capture including name, industry, location, website URL for brand verification
- **Logo display** on marketplace listings enhances brand recognition and platform professionalism

#### Profile Display
- **Public marketplace** displays verified creators with profile images, platform badges, follower counts, and rates
- **Brand showcase section** on homepage features companies with logos and industry categories
- **Initials fallback** generates two-letter placeholders when no profile image/logo uploaded maintaining visual consistency
- **Verified badges** shown for creators with verified social media accounts enhancing trust

### 4.4 File Upload System

#### Implementation
- **Multipart form-data** handling for file uploads through dedicated endpoints for creators and brands
- **File type validation** restricts uploads to image formats (JPG, JPEG, PNG, WebP) preventing malicious file uploads
- **UUID-based naming** generates unique filenames preventing overwrites and enabling CDN distribution
- **Directory structure** separates uploads by type (creators/, brands/) for organized file management

#### Security Measures
- **Secure filename sanitization** using Werkzeug removes path traversal characters and special characters
- **File size limits** can be configured through Flask's MAX_CONTENT_LENGTH setting
- **Extension validation** checks both file extension and MIME type for comprehensive security
- **Public URL generation** creates accessible links for frontend display while maintaining security

### 4.5 Search & Discovery

#### Creator Search
- **Multi-criteria filtering** by platform, category, location, and rate range
- **Keyword search** across username, bio, and category fields for flexible discovery
- **Sorting options** by followers, engagement rate, or rate for prioritization
- **Pagination support** with configurable page size for large result sets

#### Brand Discovery
- **Industry-based filtering** helps creators find brands in relevant sectors
- **Featured brands section** on homepage showcases top companies increasing visibility
- **Company profile cards** display logo, industry, location, and website for quick evaluation
- **Verified badge display** highlights authenticated companies building trust

### 4.6 Dashboard Interface

#### Role-Based Dashboards
- **Creator dashboard** shows profile overview, statistics, and marketplace access for finding brand partnerships
- **Brand dashboard** displays influencer discovery tools and profile management features
- **Navigation sidebar** with role-specific menu items providing quick access to main features
- **Profile section** allows users to view and edit their information

#### User Experience Features
- **Welcome message** with user's name/company name for personalization
- **Statistics display** showing key metrics and profile completeness
- **Quick actions** for common tasks like updating profile or browsing marketplace
- **Logout functionality** clears session storage and redirects to landing page

---

## 5. API ENDPOINTS DOCUMENTATION

The API follows RESTful conventions with multiple endpoints organized across authentication and user management modules. Key endpoints include POST /api/auth/register/{creator|brand} for user registration with OTP email verification, POST /api/auth/login for JWT token generation, POST /api/auth/verify-email for OTP validation, POST /api/auth/resend-otp for new verification codes, GET /api/auth/profile for authenticated user data, POST /api/{creators|brands}/upload-{profile|logo} for file uploads with secure storage, and GET /api/{creators|brands} for marketplace listings with pagination. All protected endpoints require Bearer token authentication in the Authorization header, and responses follow consistent JSON format with appropriate HTTP status codes (200, 201, 400, 401, 403, 404).

---

## 6. SECURITY IMPLEMENTATIONS

### 6.1 Authentication Security

#### Password Security
- **Bcrypt hashing algorithm** with automatic salt generation ensures irreversible password storage preventing database breaches from exposing passwords
- **Minimum 6-character password** requirement enforced on both client and server sides balancing security with usability
- **Password strength validation** checks for basic requirements and provides user feedback before submission
- **No password storage in logs** or error messages prevents accidental password exposure through debugging

#### Token-Based Security
- **JWT with HS256 algorithm** uses HMAC with SHA-256 for token signing ensuring token integrity and authenticity
- **Token expiration** set to 7 days (configurable) forces periodic re-authentication reducing risk of token theft
- **Secret key from environment** variables prevents hardcoded secrets in codebase and enables key rotation
- **Token payload minimal** containing only user_id, email, and role reduces information exposure if token intercepted

#### Session Management
- **Stateless authentication** using JWT eliminates session fixation attacks and enables horizontal scaling
- **Client-side token storage** in localStorage with clear on logout prevents session persistence
- **Automatic logout on 401** response prevents users from accessing stale data after token expiry
- **No token refresh implemented** currently (enhancement opportunity) forces full re-authentication on expiry

### 6.2 Email Verification Security

#### OTP Security
- **4-digit numeric codes** provide balance between security (10,000 combinations) and user convenience
- **5-minute expiration window** limits time for brute force attempts while allowing reasonable user response time
- **One-time use enforcement** clears OTP after successful verification preventing replay attacks
- **OTP stored in database** (plaintext currently) enables server-side validation; production should use hashing

#### Rate Limiting Considerations
- **Currently no rate limiting** on OTP requests for ease of testing and development
- **Production enhancement needed** to limit OTP generation attempts (5 per hour recommended)
- **Login attempt limiting** not implemented; should add after multiple failed verifications
- **IP-based throttling** could prevent automated attacks on verification system

#### Email Delivery Security
- **SMTP over TLS** for encrypted email transmission preventing eavesdropping
- **Environment-based credentials** for email service prevents hardcoded passwords
- **From address validation** ensures emails appear from legitimate source
- **Fallback to console** only in development; production disables this for security

### 6.3 Input Validation & Sanitization

#### Client-Side Validation
- **Email format validation** using regex ensures proper email structure before submission
- **Required field checks** prevent empty submissions improving user experience
- **Real-time error display** provides immediate feedback reducing invalid submissions
- **Type validation** for numeric fields (rate, followers, budget) prevents string injection

#### Server-Side Validation
- **Duplicate validation** checks email and username uniqueness preventing account enumeration
- **Field type enforcement** through SQLAlchemy models ensures data integrity
- **Required field validation** rejects incomplete requests with descriptive error messages
- **Data length limits** on string fields prevent buffer overflow and database errors

#### File Upload Security
- **Extension whitelist** limits uploads to image formats only preventing executable file uploads
- **Secure filename function** removes path traversal characters and special characters
- **UUID-based naming** prevents filename collisions and predictable file paths
- **File size limits** should be configured (enhancement needed) to prevent DoS attacks

### 6.4 SQL Injection Prevention

#### ORM Usage
- **SQLAlchemy ORM** automatically parameterizes queries preventing SQL injection attacks
- **No raw SQL queries** in codebase eliminates manual sanitization requirements
- **Prepared statements** through ORM ensure user input never directly concatenated with SQL
- **Type-safe queries** through Python objects prevent type confusion attacks

### 6.5 Cross-Site Scripting (XSS) Prevention

#### Frontend Security
- **No innerHTML usage** with user content prevents script injection
- **Text content API** for displaying user input ensures HTML escaping
- **URL sanitization** for profile images and website links prevents javascript: protocol attacks
- **Content Security Policy** headers should be added (enhancement) to restrict script sources

### 6.6 Cross-Origin Resource Sharing (CORS)

#### CORS Configuration
- **Flask-CORS enabled** allows frontend on different origin to access API
- **Currently open configuration** for development; production should whitelist specific origins
- **Credentials support** enabled for cookie/authorization header transmission
- **Preflight handling** automatic through Flask-CORS for complex requests

### 6.7 API Security

#### Authentication Requirements
- **Bearer token authentication** for protected endpoints using Authorization header
- **Role-based access control** through token payload prevents unauthorized actions
- **Endpoint-level protection** using @require_auth decorator on sensitive routes
- **Ownership validation** needed (enhancement) to prevent users modifying others' data

#### Error Handling
- **Generic error messages** for authentication failures prevent account enumeration
- **No stack traces** in production responses prevents information leakage
- **Consistent error format** with status and message fields enables proper error handling
- **HTTP status codes** properly used (401 unauthorized, 403 forbidden, 404 not found)

### 6.8 Data Privacy

#### Sensitive Data Handling
- **Password hashes** never included in API responses or logs
- **Email addresses** only returned to authenticated users viewing own profile
- **OTP codes** cleared from database after use preventing exposure
- **Profile data** only includes public information in marketplace listings

#### Environment Variables
- **.env file** used for sensitive configuration (database URL, secret keys, email credentials)
- **.env in .gitignore** prevents accidental commit of secrets
- **.env.example** provided as template without actual sensitive values
- **Production secrets** should use secret management service (enhancement)

### 6.9 Database Security

#### Connection Security
- **SQLite** for development; production should use PostgreSQL with SSL
- **Connection pooling** through SQLAlchemy prevents connection exhaustion
- **Parameterized queries** through ORM prevent SQL injection
- **Foreign key constraints** enabled to maintain referential integrity

#### Data Integrity
- **Cascade deletes** configured to prevent orphaned records
- **Unique constraints** on email and username prevent data duplication
- **Timestamp fields** on all tables provide audit trail
- **Transaction management** through SQLAlchemy sessions ensures ACID properties

### 6.10 Security Enhancements Needed

#### Current Limitations
- **No HTTPS enforcement** in development; production must use SSL/TLS
- **No rate limiting** on API endpoints vulnerable to DoS attacks
- **No CSRF protection** for state-changing operations from browser
- **No account lockout** after multiple failed login attempts
- **No password reset** functionality leaves users with forgotten passwords
- **No audit logging** of security-relevant events (login attempts, permission changes)
- **No input length limits** on text fields could lead to memory issues
- **File upload size** unlimited could enable DoS through large uploads

#### Recommended Additions
- **Implement Flask-Limiter** for rate limiting on authentication and OTP endpoints
- **Add HTTPS redirect** middleware for production deployment
- **Implement refresh tokens** for better security than long-lived access tokens
- **Hash OTP codes** before database storage similar to passwords
- **Add CSRF tokens** for form submissions using Flask-WTF
- **Implement password reset** flow with time-limited tokens
- **Add security headers** (HSTS, X-Frame-Options, CSP) using Flask-Talisman
- **Setup monitoring** for failed login attempts and suspicious patterns

---

## 7. PROJECT STRUCTURE

### Backend Structure
```
backend/
├── app.py                  # Flask application entry point
├── config.py              # Environment-based configuration
├── models.py              # SQLAlchemy database models
├── jwt_auth.py            # JWT token generation and validation
├── password_utils.py      # Password hashing utilities
├── otp_utils.py          # OTP generation and validation
├── email_service.py      # Email sending functionality
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not in git)
├── .env.example          # Environment template
├── routes/
│   ├── __init__.py       # Routes registration
│   ├── auth.py          # Authentication endpoints
│   ├── creators.py      # Creator management
│   └── brands.py        # Brand management
├── uploads/
│   ├── creators/        # Creator profile images
│   └── brands/          # Brand logos
└── instance/
    └── brandnest.db     # SQLite database file
```

### Frontend Structure
```
frontend/
├── index.html           # Landing page with marketplace
├── login.html          # Login page
├── join-creator.html   # Creator registration
├── join-brand.html     # Brand registration
├── verify-email.html   # Email OTP verification
├── dashboard.html      # User dashboard
├── admin.html          # Admin panel
├── app.js             # Main application logic
├── auth.js            # Authentication logic
├── admin.js           # Admin functionality
├── styles.css        # Global styles
├── auth.css          # Authentication page styles
├── dashboard.css     # Dashboard styles
├── admin.css         # Admin panel styles
└── images/           # Static assets
```

---

## 8. DEVELOPMENT WORKFLOW

### Setup Process
- **Virtual environment creation** using Python venv for dependency isolation
- **Dependency installation** via pip install -r requirements.txt for backend packages
- **Environment configuration** by copying .env.example to .env and filling credentials
- **Database initialization** automatic through SQLAlchemy create_all() on first run

### Development Server
- **Backend runs** on localhost:5000 with Flask development server and hot reload enabled
- **Frontend served** through Live Server extension or simple HTTP server
- **CORS enabled** for local development allowing different port origins

### Testing Workflow
- **Manual testing** through browser and Postman for API endpoint verification
- **Database inspection** using SQLite browser tools for data verification
- **Console logging** extensively used for debugging and OTP display during development

### Version Control
- **Git repository** tracked from project start with meaningful commit messages
- **Gitignore configured** to exclude .env, __pycache__, .venv, and instance/ folders
- **Commit history** shows iterative development of features (authentication → profiles → campaigns → verification)

---

## 9. CONCLUSION

### Project Accomplishments
- **Full-stack implementation** demonstrates proficiency in both frontend and backend technologies
- **RESTful API design** follows industry standards for resource naming and HTTP methods
- **Security-first approach** with JWT authentication, password hashing, and email verification
- **Scalable architecture** enables easy addition of new features and user roles
- **Modern UI/UX** with responsive design and intuitive navigation flows

### Technical Skills Demonstrated
- **Backend Development:** Python, Flask, RESTful API design, ORM usage, database design
- **Frontend Development:** HTML5, CSS3, Vanilla JavaScript, DOM manipulation, async/await
- **Authentication:** JWT implementation, bcrypt hashing, email verification with OTP
- **Database:** SQL, relational database design, normalization
- **Security:** Input validation, secure file handling, CORS configuration
- **DevOps:** Git version control, environment management, dependency management

### Learning Outcomes
- **Understanding of authentication flows** from registration through email verification to secure login
- **API development patterns** including proper error handling, status codes, and response formats
- **Database design and ORM usage** for efficient data management and queries
- **Frontend-backend integration** through asynchronous API calls and token-based authentication
- **Security considerations** in web applications from input validation to secure storage

---

**Document Version:** 1.0  
**Last Updated:** February 16, 2026  
**Technology Stack Versions:** Flask 2.3.3, Python 3.x, SQLAlchemy 3.0.5, PyJWT 2.8.0
