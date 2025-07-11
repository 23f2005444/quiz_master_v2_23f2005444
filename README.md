# Quiz Master v2

A multi-user quiz application for exam preparation across multiple courses.

## Project Overview

Quiz Master is a comprehensive web application that serves as an exam preparation platform for various subjects. It features a dual-role system with administrator (quiz master) capabilities and regular user access.

### Key Features

- **Admin Dashboard**
  - Subject management (create, edit, delete)
  - Chapter management within subjects
  - Quiz creation with MCQ questions
  - User management
  - Reporting and analytics

- **User Features**
  - Self-registration and profile management
  - Subject/chapter-based quiz selection
  - Timed quiz attempts
  - Performance tracking and history
  - Personalized reports

- **Automated Systems**
  - Daily engagement reminders
  - Monthly activity reports
  - CSV exports of quiz data

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: Vue.js with Bootstrap
- **Database**: SQLite
- **Caching**: Redis
- **Task Queue**: Celery
- **Authentication**: Flask security Token