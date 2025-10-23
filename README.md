# 🔧 Repair Requests CRM

Mini-CRM system for managing repair requests with role-based access control.

## 🌟 Features

- ✅ **Public API** for submitting repair requests (no auth required)
- 👥 **Role-based access**: Admin and Worker roles
- 🔐 **JWT Authentication** with secure password hashing
- 👨‍💼 **Admin**: Full CRUD for users, clients, and tickets
- 👷 **Worker**: View and update status of assigned tickets
- 🔍 **Search & Filter**: By title, status, assigned worker
- 📄 **Pagination** on all list endpoints
- 🐳 **Docker** ready with Docker Compose
- 🚀 **CI/CD** pipeline with GitHub Actions
- 📊 **PostgreSQL** database with async SQLAlchemy
- 🧪 **Full test coverage** with pytest

## 🏗️ Tech Stack

- **Python 3.13+**
- **FastAPI** - Modern web framework
- **Pydantic 2.0+** - Data validation
- **SQLAlchemy 2.0** (async) - ORM
- **PostgreSQL** - Database
- **Alembic** - Migrations
- **JWT** - Authentication
- **Docker & Docker Compose** - Containerization
- **GitHub Actions** - CI/CD
- **Pytest** - Testing

## 🚀 Quick Start with Docker

### Prerequisites

- Docker & Docker Compose installed
- Docker Hub account (for pulling the image)

### 1. Pull and Run
```bash
git clone <repository-url>
cd repair-requests-crm

cp .env.example .env

docker-compose up -d
```

### 2. Run Migrations
```bash
docker-compose exec api alembic upgrade head
```

### 3. Create Test Accounts
```bash
docker-compose exec api python scripts/seed_users.py
```

This creates:
- **Admin**: `admin@example.com` / `admin123`
- **Worker**: `worker@example.com` / `worker123`

### 4. Access the API

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

## 🛠️ Local Development Setup

### Prerequisites

- Python 3.13+
- PostgreSQL 16+
- Poetry (recommended) or pip

### 1. Install Dependencies
```bash
poetry install

pip install -r requirements.txt
```

### 2. Setup Database
```bash
createdb repair_crm_db

psql -U postgres
CREATE DATABASE repair_crm_db;
\q
```

### 3. Configure Environment
```bash
cp .env.example .env
```

### 4. Run Migrations
```bash
alembic upgrade head
```

### 5. Create Test Users
```bash
python scripts/seed_users.py
```

### 6. Run Application
```bash
uvicorn src.main:app --reload

poetry run uvicorn src.main:app --reload
```

## 📋 API Endpoints

### 🔓 Public Endpoints (No Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tickets/public` | Submit repair request |
| GET | `/health` | Health check |

### 🔐 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login and get JWT token |
| GET | `/auth/me` | Get current user info |

### 👥 Users (Admin Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users` | Create new user |
| GET | `/users` | List all users |
| GET | `/users/{id}` | Get user by ID |
| PATCH | `/users/{id}` | Update user |
| DELETE | `/users/{id}` | Delete user |

### 👤 Clients (Authenticated)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/clients` | Create client |
| GET | `/clients` | List all clients |
| GET | `/clients/{id}` | Get client by ID |
| PATCH | `/clients/{id}` | Update client (Admin) |
| DELETE | `/clients/{id}` | Delete client (Admin) |

### 🎫 Tickets (Repair Requests)

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/tickets` | List tickets | Admin: all, Worker: assigned |
| GET | `/tickets/{id}` | Get ticket details | Admin: all, Worker: assigned |
| PATCH | `/tickets/{id}` | Update ticket | Admin only |
| DELETE | `/tickets/{id}` | Delete ticket | Admin only |
| PATCH | `/tickets/{id}/status` | Update status | Admin: all, Worker: assigned |
| POST | `/tickets/{id}/assign` | Assign to worker | Admin only |

### Query Parameters for Listing

- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 10, max: 100)
- `status` - Filter by status (new, in_progress, done)
- `title` - Search by title (partial match)
- `assigned_worker_id` - Filter by assigned worker

## 📝 Usage Examples

### 1. Submit Repair Request (Public)
```bash
curl -X POST "http://localhost:8000/tickets/public" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Broken laptop screen",
    "description": "The screen is cracked and not displaying properly",
    "client_full_name": "John Doe",
    "client_email": "john@example.com",
    "client_phone": "+1234567890",
    "client_address": "123 Main St, City"
  }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"
```

### Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. List Tickets (with filters)
```bash
curl -X GET "http://localhost:8000/tickets?status=new&page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Assign Ticket to Worker (Admin)
```bash
curl -X POST "http://localhost:8000/tickets/1/assign" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "worker_id": 2
  }'
```

### 5. Update Ticket Status (Worker)
```bash
curl -X PATCH "http://localhost:8000/tickets/1/status" \
  -H "Authorization: Bearer WORKER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

### 6. Create New Worker (Admin)
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newworker@example.com",
    "password": "securepass123",
    "full_name": "Jane Smith",
    "role": "worker"
  }'
```

## 🧪 Testing

### Run All Tests
```bash
poetry run pytest

pytest
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html --cov-report=term
```

### View Coverage Report
```bash
open htmlcov/index.html
```

### Run Specific Tests
```bash
pytest tests/tickets/

pytest tests/auth/test_router.py

pytest tests/auth/test_router.py::test_login_success
```

## 🔄 Database Migrations

### Create New Migration
```bash
alembic revision --autogenerate -m "description"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1
```

### View Migration History
```bash
alembic history
```

## 🐳 Docker Hub Image

The application is available on Docker Hub:
```bash
docker pull YOUR_USERNAME/repair-requests-crm:latest
```

## 🚀 CI/CD Pipeline

The project uses GitHub Actions for CI/CD:

1. **On Pull Request**: Run tests and linters
2. **On Push to Main**: Run tests, build Docker image, push to Docker Hub
3. **On Tag (v*)**: Same as above with version tag

### Setup Secrets

Add these secrets to your GitHub repository:

- `DOCKER_HUB_USERNAME` - Your Docker Hub username
- `DOCKER_HUB_TOKEN` - Your Docker Hub access token

## 📂 Project Structure
```
repair-requests-crm/
├── src/
│   ├── auth/              # Authentication module
│   ├── users/             # User management (admin/worker)
│   ├── clients/           # Client management
│   ├── tickets/           # Ticket (repair requests) management
│   ├── core/              # Core configurations
│   ├── database/          # Database setup
│   ├── middleware/        # Custom middleware
│   └── main.py            # FastAPI application
├── tests/                 # Test suite
├── alembic/               # Database migrations
├── scripts/               # Utility scripts
├── .github/workflows/     # CI/CD configuration
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
└── README.md              # This file
```

## 🔒 Security

- Passwords hashed with bcrypt
- JWT tokens with expiration
- Role-based access control
- SQL injection prevention via SQLAlchemy
- Input validation with Pydantic
- CORS configured

## 📊 Database Schema

### Users Table
- `id` (PK)
- `email` (unique)
- `password` (hashed)
- `full_name`
- `role` (admin|worker)
- `is_active`

### Clients Table
- `id` (PK)
- `full_name`
- `email`
- `phone`
- `address`

### Tickets Table
- `id` (PK)
- `title`
- `description`
- `status` (new|in_progress|done)
- `client_id` (FK)
- `assigned_worker_id` (FK, nullable)
- `created_at`
- `updated_at`

## 🌐 Environment Variables
```env
# Environment
ENVIRONMENT=dev  # dev or prod

# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=repair_crm_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_HOURS=24

# API
PROJECT_NAME=Repair Requests CRM

# Docker Hub (for CI/CD)
DOCKER_HUB_USERNAME=your_username
DOCKER_HUB_TOKEN=your_token
```

## 👥 Test Accounts

After running `python scripts/seed_users.py`:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | admin123 |
| Worker | worker@example.com | worker123 |
