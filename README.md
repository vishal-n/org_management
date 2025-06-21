# Organization Management API

A comprehensive FastAPI-based system for managing organizations with dynamic database creation. Each organization gets its own PostgreSQL database, providing complete data isolation and multi-tenancy.

## 🏗️ Architecture

This project implements a **multi-tenant database architecture**:

- **Master Database**: Stores organization metadata and user authentication
- **Organization Databases**: Each organization has its own isolated PostgreSQL database
- **Dynamic Database Creation**: New databases are created automatically when organizations are registered

## 🚀 Features

- ✅ Multi-tenant organization management
- ✅ Dynamic database creation per organization
- ✅ JWT-based authentication
- ✅ Admin user management
- ✅ RESTful API with automatic documentation
- ✅ PostgreSQL database support
- ✅ Password hashing and security

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 12+
- pip (Python package manager)

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd org_management
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

#### Option A: Using Homebrew (macOS)
```bash
brew install postgresql
brew services start postgresql
```

#### Option B: Using Docker
```bash
docker run --name postgres-org \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=master_org_db \
  -p 5432:5432 \
  -d postgres:15
```

### 5. Configure database permissions
```bash
# Connect to PostgreSQL as superuser
psql -U postgres

# Grant CREATEDB permission to postgres user
ALTER USER postgres CREATEDB;

# Create the master database
CREATE DATABASE master_org_db;

# Exit psql
\q
```

### 6. Create environment file (optional)
```bash
cp .env.example .env
# Edit .env with your database credentials
```

## 🏃‍♂️ Running the Application

### Start the server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access the API documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Organization Management

#### Create Organization
```bash
POST /org/create
```
**Request Body:**
```json
{
  "email": "admin@company.com",
  "password": "securepassword123",
  "organization_name": "MyCompany"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "MyCompany",
  "admin_email": "admin@company.com",
  "created_at": "2024-01-15T10:30:00"
}
```

#### Get Organization
```bash
POST /org/get
```
**Request Body:**
```json
{
  "organization_name": "MyCompany"
}
```

### Authentication

#### Admin Login
```bash
POST /admin/login?organization_name=MyCompany
```
**Request Body:**
```json
{
  "email": "admin@company.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@company.com",
    "is_admin": true,
    "is_active": true
  }
}
```

### Health Check
```bash
GET /health
```

## 🗄️ Database Schema

### Master Database (`master_org_db`)

#### Organizations Table
```sql
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    admin_email VARCHAR(255) NOT NULL,
    database_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Organization Databases (`org_<organization_name>`)

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Configuration

The application uses `pydantic-settings` for configuration management. Default settings are in `app/core/config.py`:

```python
class Settings(BaseSettings):
    # Master Database
    master_db_host: str = "localhost"
    master_db_port: int = 5432
    master_db_name: str = "master_org_db"
    master_db_user: str = "postgres"
    master_db_password: str = "postgres"
    
    # JWT
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # App
    debug: bool = True
```

### Environment Variables
You can override these settings using environment variables or a `.env` file:

```bash
MASTER_DB_HOST=localhost
MASTER_DB_PORT=5432
MASTER_DB_NAME=master_org_db
MASTER_DB_USER=postgres
MASTER_DB_PASSWORD=postgres
SECRET_KEY=your-super-secret-key-change-this-in-production
```

## 🐛 Troubleshooting

### Common Issues

#### 1. "permission denied to create database"
**Solution**: Grant CREATEDB permission to your PostgreSQL user
```sql
ALTER USER postgres CREATEDB;
```

#### 2. "ModuleNotFoundError: No module named 'pydantic_settings'"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

#### 3. "Connection refused" to PostgreSQL
**Solution**: Ensure PostgreSQL is running
```bash
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql

# Docker
docker start postgres-org
```

#### 4. "CREATE DATABASE cannot run inside a transaction block"
**Solution**: This is fixed in the current codebase using direct psycopg2 connections.

## 🔒 Security Considerations

- Change the default `SECRET_KEY` in production
- Use strong passwords for database users
- Enable SSL for database connections in production
- Implement rate limiting for API endpoints
- Use environment variables for sensitive configuration
- Regularly update dependencies

## 🧪 Testing

### Using curl
```bash
# Create organization
curl -X POST "http://localhost:8000/org/create" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "testpass123",
    "organization_name": "TestOrg"
  }'

# Login
curl -X POST "http://localhost:8000/admin/login?organization_name=TestOrg" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "testpass123"
  }'
```

### Using Python requests
```python
import requests

# Create organization
response = requests.post(
    "http://localhost:8000/org/create",
    json={
        "email": "admin@test.com",
        "password": "testpass123",
        "organization_name": "TestOrg"
    }
)
print(response.json())
```

## 📁 Project Structure

```
org_management/
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── auth.py
│   │       └── organization.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── organization.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── organization.py
│   │   └── user.py
│   ├── services/
│   │   ├── auth_service.py
│   │   └── organization_service.py
│   └── main.py
├── requirements.txt
├── Dockerfile
└── README.md
```
