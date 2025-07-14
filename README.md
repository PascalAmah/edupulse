# EduPulse Backend

EduPulse is a feature-rich microlearning platform backend built with Django and Django REST Framework. It powers APIs for authentication, quiz management, mood and progress tracking, gamification, and offline synchronization.

---

## 🌟 Features

- **Quiz-based Microlearning:** Create, manage, and deliver quizzes.
- **Mood & Progress Tracking:** Monitor user mood and learning progress.
- **Gamification:** Badges, points, and leaderboards to boost engagement.
- **Offline Sync:** Reliable experience for mobile/web clients, even offline.
- **Comprehensive API Documentation:** Interactive docs via Swagger and Redoc.

---

## 🏗️ Project Structure

```
edupulse/
├── edupulse/         # Django project configuration
├── common/           # Shared utilities and permissions
├── core/             # Authentication & user management
├── quizzes/          # Quiz logic and endpoints
├── tracking/         # Mood, progress, and gamification
├── sync/             # Offline sync logic
├── tests/            # Unit and integration tests
├── docs/             # API specs, ERD, contribution guidelines
├── manage.py         # Django management script
├── requirements.txt  # Python dependencies
├── env.example       # Example environment variables
└── README.md         # Project overview
```

---

## 🚀 Getting Started

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd edupulse
   ```

2. **Set up a virtual environment**

   ```bash
   python -m venv venv
   # On Unix/macOS
   source venv/bin/activate
   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   - Copy `env.example` to `.env` and update with your secrets and database credentials.

5. **Apply database migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional, for admin access)**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**

   ```bash
   python manage.py runserver
   ```

8. **Access API Documentation**
   - Swagger UI: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
   - Redoc: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

---

## 📚 Documentation

- **API Reference:** [`docs/API_SPEC.md`](docs/API_SPEC.md)
- **Entity Relationship Diagram:** [`docs/ERD.png`](docs/ERD.png)
- **Contribution Guide:** See `docs/` for guidelines

---

## 🧪 Testing

Run all tests with:

```bash
python manage.py test
```

---

## 🤝 Contributing

Contributions are welcome! Please see the guidelines in the `docs/` directory.

---

## 📝 Notes

- All major features are implemented and production-ready.
- For support or questions, please refer to the documentation or contact the maintainers.

---
