# Backend Setup

## Environment Variables

Create a `.env` file in the Back-end directory with the following variables:

```
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# PostgreSQL Database Configuration
DB_NAME=form_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Setup

1. **Install PostgreSQL** (if not already installed):
   - macOS: `brew install postgresql@15` or download from [PostgreSQL website](https://www.postgresql.org/download/)
   - Linux: `sudo apt-get install postgresql postgresql-contrib` (Ubuntu/Debian)
   - Windows: Download from [PostgreSQL website](https://www.postgresql.org/download/windows/)

2. **Create PostgreSQL database**:
   ```bash
   # Start PostgreSQL service
   # macOS: brew services start postgresql@15
   # Linux: sudo systemctl start postgresql
   # Windows: Start PostgreSQL service from Services
   
   # Create database
   psql -U postgres
   CREATE DATABASE form_db;
   \q
   ```

3. Create virtual environment: `python3 -m venv venv`
4. Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -r requirements.txt`
6. Run migrations: `python manage.py migrate`
7. Create superuser: `python manage.py createsuperuser`
8. Run server: 
   - For local access only: `python manage.py runserver`
   - For network access (mobile devices): `python manage.py runserver 0.0.0.0:8000`

