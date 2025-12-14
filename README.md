# DC Landscaping - Time Tracking System

Internal time and cost tracking system for DC Landscaping company.

## Features

- **Time Tracking**: Start/stop timer or manual entry
- **Worker Management**: Add/edit workers with hourly rates
- **Property Management**: Manage job sites with spring/fall cleanup flags
- **Reports**: Generate reports with Excel export (Admin only)
- **Two User Roles**: Admin (full access) and Worker (limited editing)

## Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, MySQL
- **Frontend**: Vue.js 3, Pinia, Tailwind CSS, Vite
- **Auth**: JWT tokens

## Quick Start with Docker

```bash
# Clone and navigate to project
cd dc-landscaping

# Start all services
docker-compose up -d

# Wait for MySQL to initialize (~30 seconds), then seed database
docker-compose exec backend python seed.py

# Access the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Manual Setup (Without Docker)

### Prerequisites

- Python 3.11+
- Node.js 18+
- MySQL 8.0+

### Database Setup

```sql
CREATE DATABASE dclandscaping;
CREATE USER 'dcland'@'localhost' IDENTIFIED BY 'dcland123';
GRANT ALL PRIVILEGES ON dclandscaping.* TO 'dcland'@'localhost';
FLUSH PRIVILEGES;
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional, defaults work for local dev)
export DATABASE_URL="mysql+pymysql://dcland:dcland123@localhost:3306/dclandscaping"
export SECRET_KEY="your-secret-key-here"

# Seed database with initial data
python seed.py

# Run backend
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## Login Credentials

| User   | Username | Password   | Access Level |
|--------|----------|------------|--------------|
| Admin  | admin    | admin123   | Full access  |
| Worker | worker   | worker123  | Limited      |

## User Permissions

| Feature | Admin | Worker |
|---------|-------|--------|
| View Dashboard | ✓ | ✓ |
| Start/Stop Timer | ✓ | ✓ |
| Manual Time Entry | ✓ | ✓ |
| Edit Today's Records | ✓ | ✓ |
| Edit Any Date Records | ✓ | ✗ |
| Add Workers | ✓ | ✓ |
| Edit Worker Rates | ✓ | ✗ |
| View Worker Rates | ✓ | ✓ |
| Manage Properties | ✓ | ✓ |
| View Reports | ✓ | ✗ |
| Export Excel | ✓ | ✗ |

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Workers
- `GET /api/workers` - List all workers
- `POST /api/workers` - Create worker
- `PUT /api/workers/{id}` - Update worker
- `DELETE /api/workers/{id}` - Deactivate worker (Admin)

### Properties
- `GET /api/properties` - List all properties
- `POST /api/properties` - Create property
- `PUT /api/properties/{id}` - Update property
- `DELETE /api/properties/{id}` - Deactivate property

### Time Records
- `GET /api/time-records` - List records (with filters)
- `GET /api/time-records/today` - Today's records
- `POST /api/time-records` - Create manual entry
- `POST /api/time-records/start` - Start timer
- `POST /api/time-records/stop` - Stop timer
- `PUT /api/time-records/{id}` - Update record
- `DELETE /api/time-records/{id}` - Delete record

### Reports (Admin only)
- `GET /api/reports/dashboard` - Dashboard statistics
- `GET /api/reports/summary` - Report summary
- `GET /api/reports/preview` - Preview report data
- `GET /api/reports/export` - Download Excel report

## Project Structure

```
dc-landscaping/
├── backend/
│   ├── app/
│   │   ├── auth/          # JWT authentication
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routers/       # API endpoints
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic (Excel export)
│   │   ├── config.py      # Settings
│   │   ├── database.py    # DB connection
│   │   └── main.py        # FastAPI app
│   ├── seed.py            # Database seeder
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # Vue components
│   │   ├── router/        # Vue Router
│   │   ├── stores/        # Pinia stores
│   │   ├── views/         # Page components
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
└── docker-compose.yml
```

## Production Deployment

1. Update `SECRET_KEY` in environment variables
2. Set proper `DATABASE_URL`
3. Build frontend: `npm run build`
4. Serve frontend with nginx
5. Run backend with gunicorn: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker`

## Currency

All monetary values are in CAD (Canadian Dollars). Numbers are displayed without currency symbol.
