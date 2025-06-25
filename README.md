# EduPulse Backend

EduPulse is a microlearning platform backend built with Django and Django REST Framework. It provides APIs for authentication, quiz management, mood/progress tracking, gamification, and offline sync. This repository is a starter scaffold for a modular, collaborative backend project.

---

## 🚀 Project Purpose

EduPulse enables:

- Quiz-based microlearning
- Mood and progress tracking
- Gamification (badges, points, leaderboards)
- Offline-first sync for mobile/web clients

This codebase is designed for rapid, independent development by multiple contributors.

---

## 🗂️ Folder Structure

```
edupulse-backend/
├── edupulse/         # Django project config (settings, URLs, WSGI/ASGI)
├── common/           # Shared permissions, helpers
├── core/             # Auth & user management (Dev 1)
├── quizzes/          # Quiz logic (Dev 2)
├── tracking/         # Mood, progress, gamification (Dev 3)
├── sync/             # Offline sync handling (Dev 3)
├── tests/            # Test files for all modules
├── docs/             # API spec, ERD, contribution guide
├── manage.py         # Django management script
├── requirements.txt  # Python dependencies
├── env.example       # Example environment variables
├── .gitignore        # Git ignore rules
└── README.md         # Project overview (this file)
```

---

## 👥 Developer Assignments

- **Dev 1:** `core/` (Authentication, user management, admin)
- **Dev 2:** `quizzes/` (Quiz models, logic, endpoints)
- **Dev 3:** `tracking/`, `sync/` (Mood, progress, gamification, offline sync)

Each module is self-contained with its own models, serializers, views, and URLs.

---

## 🛠️ Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone <repo-url>
   cd edupulse-backend
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   - Copy `env.example` to `.env` and fill in your secrets and DB credentials.

5. **Apply migrations:**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (for admin):**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**

   ```bash
   python manage.py runserver
   ```

8. **API Documentation:**
   - Swagger UI: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
   - Redoc: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

---

## 📚 Documentation

- **API Spec:** See [`docs/API_SPEC.md`](docs/API_SPEC.md)
- **ERD:** See [`docs/ERD.png`](docs/ERD.png) (add your ERD image here)
- **Contribution Guide:** Add guidelines to `docs/` as needed

---

## 📝 Notes

- All code is placeholder/stub for rapid parallel development.
- Each module has clear comments and TODOs for implementation.
- Use the provided test files in `tests/` to add your unit/integration tests.

---

## License

MIT License. See `LICENSE` file (add if needed).
