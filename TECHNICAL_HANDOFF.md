# Fitna Backend - Technical Handoff Document

This document serves as a complete technical handoff for the Fitna Backend project. It details the architecture, implementation status, codebase structure, and technical decisions made during the initial development phase.

---

## 1. PROJECT OVERVIEW

**Overall project purpose:**
Fitna (فطنة) is an educational platform targeted at students aged 14-18. It provides a structured learning environment across 9 distinct modules (e.g., Quran, Memory, Problem Solving). The backend serves as a robust RESTful API that handles user roles, secure content distribution, interactive quizzes with auto-grading, and comprehensive module analytics.

**Current implementation status:**
The backend foundation is complete, verified, and deployment-ready. The core architecture, database schema, role-based access control (RBAC), authentication, content management, and quiz engine are fully implemented. 

**Completed features:**
- Custom User model with email login and role-based permissions (`SUPER_ADMIN`, `MODULE_ADMIN`, `STUDENT`).
- JWT-based authentication with 7-day token lifetimes.
- Student registration flow with strict age validation (14-18) and module enrollment.
- Module Admin capabilities (approving/rejecting students, managing content, viewing analytics).
- Robust Quiz Engine (MCQ, True/False, Multiple Answer) with auto-grading and analytics.
- Centralized Content Management (Documents, Videos, Voice, Photos, Live Sessions).
- Real-time in-app Notification system (triggered by registration, approval, rejection, new content, and new quizzes).
- Unsigned direct Cloudinary media upload integration.

**Features partially completed:**
- Password Reset: The backend uses standard JWT for authentication, but password reset email flows (forgot password) are not yet implemented.
- Push Notifications: In-app notifications are complete, but external push notifications (FCM/APNs) or Email notifications are not implemented.

**Features not started:**
- Gamification (badges, leaderboards, points beyond quiz scores).
- Real-time chat or discussion forums.
- Payment gateway integrations (currently free/admin-approved access).

---

## 2. TECHNOLOGY STACK

- **Backend framework:** Python 3.13 / Django 5.0 / Django REST Framework (DRF)
- **Frontend framework:** None in this repository (API only). Interacts with an external frontend (e.g., React/Next.js/Vite).
- **Database:** PostgreSQL (managed via `dj-database-url` in production), SQLite (for local development).
- **Authentication:** `djangorestframework-simplejwt` (JSON Web Tokens).
- **Storage:** Cloudinary (direct unsigned uploads via HTTP POST requests).
- **Deployment:** Render.com (Web Service connected to PostgreSQL via environment variables).
- **Third-party integrations:** Cloudinary SDK (removed for direct HTTP requests on upload, but still valid for retrieval/management if needed), `django-cors-headers`, `python-decouple` (environment variables).
- **Build tools:** Gunicorn, Whitenoise (for static file serving).
- **Testing tools:** Django Test Client (`run_all_tests.py` custom script for E2E integration testing).

---

## 3. PROJECT STRUCTURE

```text
fitna-backend/
├── manage.py                   # Django CLI entrypoint
├── render.yaml                 # Render deployment configuration
├── requirements.txt            # Python dependencies
├── .gitignore
├── db.sqlite3                  # Local database
├── TECHNICAL_HANDOFF.md        # This document
│
├── fitna_backend/              # Main Django configuration app
│   ├── settings/
│   │   ├── base.py             # Shared settings
│   │   └── production.py       # Production-specific settings (Whitenoise, dj-database-url)
│   ├── urls.py                 # Root URL routing
│   ├── wsgi.py                 # WSGI entrypoint for Gunicorn
│   └── asgi.py                 # ASGI entrypoint
│
├── core/                       # Global utilities & Super Admin features
│   ├── models.py               # (Empty - structural)
│   ├── permissions.py          # Custom DRF Permission classes
│   ├── views.py                # SuperAdmin stats/users, Cloudinary UploadMediaView
│   ├── urls.py                 # Super Admin routing
│   └── upload_urls.py          # Media upload routing
│
├── users/                      # Authentication & User Management
│   ├── models.py               # CustomUser, Notification
│   ├── serializers.py          # Registration, Login, User serialization
│   ├── views.py                # Auth flows, /me/ endpoint
│   ├── urls.py                 # Auth routing
│   └── management/commands/
│       └── create_super_admin.py # CLI command to bootstrap first admin
│
├── modules/                    # Module & Enrollment Engine
│   ├── models.py               # Module, Enrollment
│   ├── serializers.py          # Module and Enrollment serialization
│   ├── views.py                # Student mgmt, Dashboard, Settings, Analytics
│   ├── urls.py                 # Module routing
│   ├── signals.py              # Notification triggers for content/students
│   └── management/commands/
│       └── seed_modules.py     # CLI command to populate the 9 default modules
│
├── content/                    # Content Management (Materials)
│   ├── models.py               # ContentBlock (Polymorphic-like structure)
│   ├── serializers.py          
│   ├── views.py                # CRUD for documents, videos, etc.
│   └── urls.py                 
│
└── quizzes/                    # Assessment Engine
    ├── models.py               # Quiz, Question, AnswerChoice, QuizAttempt, StudentAnswer
    ├── serializers.py          
    ├── views.py                # Quiz CRUD, Start, Submit, Results Admin view
    └── urls.py                 
```

---

## 4. DATABASE

### `users.CustomUser`
- **Fields:** `email` (PK/Username), `full_name`, `role` (Choice), `is_active`, `is_approved`, `is_staff`, `date_joined`, `profile_picture`, `phone_number`, `age`, `module_note`.
- **Relationships:** None directly natively, referenced by many.
- **Constraints:** `email` is unique. `age` validated at serializer level (14-18).
- **Purpose:** Central user model. Replaces Django's default User.

### `users.Notification`
- **Fields:** `title`, `message`, `notification_type`, `is_read`, `created_at`.
- **Relationships:** `recipient` (FK to CustomUser).
- **Purpose:** In-app notification system.

### `modules.Module`
- **Fields:** `name`, `slug` (Unique), `description`, `icon`, `color_primary`.
- **Purpose:** Represents the 9 core learning areas (e.g., Quran, Memory).

### `modules.Enrollment`
- **Fields:** `enrolled_at`, `status` (PENDING, APPROVED, REJECTED).
- **Relationships:** `student` (FK to CustomUser), `module` (FK to Module).
- **Constraints:** Unique constraints on `(student, module)`.
- **Purpose:** Tracks which students belong to which modules and their approval state.

### `content.ContentBlock`
- **Fields:** `title`, `content_type` (DOCUMENT, VIDEO, VOICE, PHOTO, SESSION), `description`, `file_url`, `order`, `is_published`, `created_at`.
- **Relationships:** `module` (FK to Module).
- **Purpose:** Stores learning materials. The `file_url` points to Cloudinary assets.

### `quizzes.Quiz`
- **Fields:** `title`, `description`, `time_limit_minutes`, `passing_score` (default 70), `is_active`, `show_results_immediately`, `max_attempts`, `created_at`.
- **Relationships:** `module` (FK to Module).
- **Purpose:** Container for an assessment.

### `quizzes.Question`
- **Fields:** `text`, `question_type` (MCQ, MULTI, TRUE_FALSE), `points`, `order`.
- **Relationships:** `quiz` (FK to Quiz).
- **Purpose:** Individual questions inside a quiz.

### `quizzes.AnswerChoice`
- **Fields:** `text`, `is_correct`.
- **Relationships:** `question` (FK to Question).
- **Purpose:** Potential answers for a question.

### `quizzes.QuizAttempt`
- **Fields:** `score`, `passed`, `completed_at`, `time_taken_seconds`.
- **Relationships:** `quiz` (FK to Quiz), `student` (FK to CustomUser).
- **Purpose:** Tracks a student's execution of a quiz.

### `quizzes.StudentAnswer`
- **Fields:** `is_correct`, `points_earned`.
- **Relationships:** `attempt` (FK to QuizAttempt), `question` (FK to Question), `selected_choices` (ManyToMany to AnswerChoice).
- **Purpose:** Granular tracking of what a student answered for analytics.

---

## 5. AUTHENTICATION

- **User roles:**
  - `SUPER_ADMIN`: Full system access, views global stats.
  - `MODULE_ADMIN`: Can manage content, quizzes, and students for modules they govern.
  - `STUDENT`: Can view approved modules, consume content, and take active quizzes.
- **Permission system:** Implemented via custom DRF Permission classes in `core/permissions.py` (e.g., `IsSuperAdmin`, `IsModuleAdmin`, `IsContentReaderOrAdmin`, `IsQuizParticipant`).
- **JWT implementation:** Uses `djangorestframework-simplejwt`. `ACCESS_TOKEN_LIFETIME` is set to 7 days to keep students logged in seamlessly.
- **Login flow:** Standard POST to `/api/v1/auth/login/` returning `access` and `refresh` tokens.
- **Registration flow:** Custom `RegisterSerializer`. Automatically creates `Enrollment` records (status `PENDING`) for modules provided in the `module_slugs` array. Validates age (14-18).
- **Password reset:** Not currently implemented.

---

## 6. API

### Auth & Users (`/api/v1/auth/`)
- `POST /register/` - Public - Register new student (age, phone, modules).
- `POST /login/` - Public - JWT Token pair.
- `POST /refresh/` - Public - Refresh token.
- `GET /me/` - Authenticated - Returns current user, enrolled modules (with colors/icons), and unread notifications count.
- `PATCH /me/` - Authenticated - Update profile.

### Core & Uploads (`/api/v1/`)
- `POST upload/` - Admins only - Uploads raw files directly to Cloudinary using unsigned preset `fitna_uploads`.
- `GET admin/stats/` - SuperAdmin - Global platform stats.
- `GET admin/users/` - SuperAdmin - Global user list.

### Modules (`/api/v1/modules/`)
- `GET /` - Authenticated - List all modules.
- `GET /<slug>/` - Readers/Admins - Module details + published content.
- `GET /<slug>/dashboard/` - ModuleAdmin - Module stats.
- `GET /<slug>/analytics/` - ModuleAdmin - Detailed module analytics.
- `PATCH /<slug>/settings/` - ModuleAdmin - Update module config.
- `GET /<slug>/students/` - ModuleAdmin - List approved students.
- `GET /<slug>/students/pending/` - ModuleAdmin - List pending students.
- `POST /<slug>/students/<id>/approve/` - ModuleAdmin - Approve student + send notification.
- `POST /<slug>/students/<id>/reject/` - ModuleAdmin - Reject student + send notification.
- `DELETE /<slug>/students/<id>/` - ModuleAdmin - Remove student from module.

### Content (`/api/v1/modules/<slug>/content/`)
- `GET /` - Readers/Admins - List module content blocks.
- `POST /` - ModuleAdmin - Create content block + notifies students.
- `PATCH /<id>/` - ModuleAdmin - Update content block.
- `DELETE /<id>/` - ModuleAdmin - Delete content block.

### Quizzes (`/api/v1/modules/<slug>/quizzes/`)
- `GET /` - Readers/Admins - List quizzes.
- `POST /` - ModuleAdmin - Create quiz + notifies students.
- `GET /<id>/` - Readers/Admins - Retrieve quiz details.
- `PATCH /<id>/` - ModuleAdmin - Update quiz.
- `DELETE /<id>/` - ModuleAdmin - Delete quiz.
- `POST /<id>/start/` - Enrolled Students - Starts a `QuizAttempt` and returns the ID.
- `POST /<id>/submit/` - Enrolled Students - Submits answers, auto-grades, calculates score, and updates `QuizAttempt`.
- `GET /<id>/results/` - ModuleAdmin - Aggregated analytics, pass rate, student scores, and most common wrong answers per question.

---

## 7. ADMIN SYSTEM

- **Dashboard / Analytics:** Admins have a `/dashboard/` and `/analytics/` endpoint per module returning `content_summary`, `recent_students`, and `quiz_performance`.
- **Student management:** Admins view pending/approved students. They write private notes (`module_note`) hidden from the student. Approving/rejecting triggers automated DB Notifications.
- **Teacher/Class Admin management:** Super Admins can create Module Admins, but UI management of Admins is currently done via Django Admin or SuperAdmin API endpoints.
- **Quiz management:** Full CRUD over Quizzes, Questions, and AnswerChoices via nested JSON payloads.
- **Content management:** Upload files via `/api/v1/upload/`, take the resulting URL, and create a `ContentBlock`.

---

## 8. STUDENT FEATURES

- **Module Access:** Students only see content for modules they are explicitly approved for.
- **Notifications:** Receive instant alerts when approved/rejected, when a new quiz is published, or new content is added.
- **Assessments:** Can take timed quizzes. The system securely locks submissions to their `QuizAttempt` to prevent tampering.
- **Profile:** Manage basic profile data. (Note: `module_note` is explicitly sanitized from their view).

---

## 9. QUIZ SYSTEM

- **Quiz Architecture:** Highly modular. A `Quiz` has many `Question`s, each with many `AnswerChoice`s.
- **Question types:** `MCQ` (Single choice), `MULTI` (Multiple correct choices), `TRUE_FALSE`.
- **Submission flow:**
  1. Student requests `POST /start/` -> creates a blank `QuizAttempt`.
  2. Student submits `POST /submit/` with JSON array of `[{"question_id": X, "choice_ids": [Y, Z]}]`.
  3. Backend loops through questions, validates against `is_correct` flags, computes points per question, sums total, and updates `QuizAttempt`.
- **Scoring:** Strict boolean logic. For `MULTI` questions, the provided choices must exactly match the set of correct choices to earn points (no partial credit implemented).
- **Analytics:** `/results/` calculates average scores, highest/lowest scores, pass rate, and dynamically computes the `most_common_wrong` answer string per question using Django aggregations.

---

## 10. CONTENT MANAGEMENT

- Content is managed via a single polymorphic-style model `ContentBlock`.
- `content_type` determines how the frontend should render it (PDF, Video, etc.).
- `file_url` holds the Cloudinary URL.
- `is_published` allows admins to draft content.
- Creation of a new `ContentBlock` with `is_published=True` triggers a Django Signal (`modules/signals.py`) that generates a `NEW_CONTENT` notification for all approved students in that module.

---

## 11. DEPLOYMENT

- **Render configuration:** Defined in `render.yaml`. Single Web Service (`fitna-backend`).
- **Database configuration:** Expects a managed PostgreSQL database. Connected via the `DATABASE_URL` environment variable. 
- **Environment variables required:**
  - `DATABASE_URL` (e.g., postgres://user:pass@host/db)
  - `SECRET_KEY` (Django secret)
  - `ALLOWED_HOSTS` (e.g., fitna-backend.onrender.com)
  - `CORS_ALLOWED_ORIGINS` (Frontend URL)
  - `CLOUDINARY_CLOUD_NAME` (For the unsigned upload endpoint)
- **Static files:** Managed seamlessly by `Whitenoise`. `collectstatic` runs automatically on deployment.
- **Media files:** Hosted entirely on Cloudinary. The backend does not store media locally.

---

## 12. CURRENT STATUS

**What is fully working?**
- Complete RBAC, Registration, and JWT Auth.
- End-to-end Quiz execution and Analytics.
- Cloudinary Uploads.
- Automated Notifications.
- Module settings and student approval pipelines.

**What still needs work?**
- Password resets (emails).
- Refresh token rotation settings (if stricter security is desired).
- Pagination: Currently, list endpoints return all objects. Pagination should be added to `StudentListView` and `Notification` views as the platform grows.

**What known issues remain?**
- `UploadMediaView` directly uses the `requests` library to hit Cloudinary. Ensure `CLOUDINARY_CLOUD_NAME` is strictly set, otherwise the endpoint fails with 500.

**What technical debt exists?**
- Quiz submissions accept nested JSON and perform multiple DB hits (N+1) to validate `AnswerChoice`s. If quizzes become massive (100+ questions), this endpoint could be optimized using `select_related`/`prefetch_related` or batch ID queries.

---

## 13. NEXT RECOMMENDED STEPS

1. **Pagination:** Add `LimitOffsetPagination` or `PageNumberPagination` to the DRF settings to prevent payload bloat on student/content lists.
2. **Password Reset Flow:** Implement Django's `PasswordResetView` or custom DRF endpoints utilizing SendGrid/SMTP.
3. **Frontend Integration:** Provide the Swagger/Postman collection to the frontend team to begin consuming the APIs.
4. **Quiz Partial Credit:** Refactor `MULTI` question grading logic in `quizzes/views.py` if teachers request partial points for partially correct answers.
5. **Caching:** Implement Redis caching for heavily accessed endpoints like `/api/v1/modules/` and `/api/v1/auth/me/`.

---

## 14. ARCHITECTURAL DECISIONS

- **Unsigned Cloudinary Uploads:** Chosen to simplify backend secret management. The backend acts as a proxy, verifying the user is an admin before securely relaying the file to Cloudinary using a preset. This keeps API Secrets out of the backend entirely.
- **Fat Views for Quizzes:** The grading logic is encapsulated in `quizzes/views.py` (`SubmitQuizAttemptView`). This was chosen over model `save()` overrides to keep the HTTP request context (attempt_id, payloads) closely tied to the logic.
- **Polymorphic Content:** Instead of separate models for Videos, Documents, and Photos, a unified `ContentBlock` model was used to simplify sorting (`order` field) and frontend rendering logic.
- **Signals for Notifications:** Django Signals (`post_save`) were used to decouple Notification generation from the Views, keeping the codebase DRY when content is created via API or Django Admin.

---

## 15. IMPROVEMENT OPPORTUNITIES

If starting from the current codebase to add more features, I would improve the following:
1. **API Documentation:** Integrate `drf-spectacular` to automatically generate OpenAPI/Swagger schemas. This will make frontend collaboration significantly easier.
2. **Soft Deletes:** Implement soft-delete logic (a `deleted_at` field) on `CustomUser` and `QuizAttempt`. Currently, deleting a student wipes their analytics history due to `CASCADE`, which teachers might want to preserve.
3. **Background Tasks:** Shift the Django Signal notification generation (which creates hundreds of rows if a module has many students) to a background task queue like Celery or Django-Q to prevent HTTP request blocking during Content/Quiz publishing.
