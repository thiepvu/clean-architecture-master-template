#  Clean Architecture with Domain-Driven Design (DDD)

A production-ready FastAPI application implementing Clean Architecture principles with Domain-Driven Design (DDD).

## 🏗️ Architecture

This project follows **Clean Architecture** with clear separation of concerns:

- **Domain Layer**: Pure business logic (entities, value objects, domain events)
- **Application Layer**: Use cases, DTOs, services
- **Infrastructure Layer**: Database, external services, ORM
- **Presentation Layer**: API controllers, routes, schemas

### Bounded Contexts (Modules)

- User Management
- File Management
- Project Management
- Notification System

## ✨ Features

- ✅ Clean Architecture with DDD
- ✅ Async/Await throughout
- ✅ PostgreSQL with SQLAlchemy
- ✅ Automatic module discovery
- ✅ OpenAPI documentation
- ✅ Type safety with Pydantic
- ✅ Repository pattern
- ✅ Unit of Work pattern
- ✅ Domain events
- ✅ Soft deletes
- ✅ Pagination
- ✅ Error handling
- ✅ Logging (JSON format)
- ✅ API versioning
- ✅ IoC Container
- ✅ CQRS Pattern
- ✅ Background Jobs (Celery/In-Memory)
- ✅ Pre-commit Hooks (Husky + isort + black + mypy)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching and Celery)
- Node.js 18+ (for Husky pre-commit hooks)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd clean-architecture

# Install Python dependencies
poetry install

source venv/bin/activate  # If you use VScode the settings.json auto added actived activateEnvironment on your terminal

# Install Node.js dependencies (for Husky)
npm install

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### Database Setup

```bash
# Start PostgreSQL via Docker
docker compose -f docker-compose.yml up --build -d

# First time setup (create initial migration)
python scripts/migrate.py --create "init" --force
python scripts/migrate.py --upgrade
python scripts/seed.py

# After pulling new code (apply pending migrations)
python scripts/migrate.py
python scripts/seed.py --check
```

### Running the Application

```bash
# Development mode

python src/main.py --env development

poetry run python src/main.py --env development

```

### Access the Application

- **API Documentation**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
.
├── src/
│   ├── contexts/               # Bounded contexts (User, File, Jobs)
│   ├── infrastructure/        # Database, logging, cache, storage
│   ├── shared/                # Shared utilities, Shared kernel
│   ├── bootstrapper/          # IoC, app factory
│   ├── presentation/          # HTTP controllers, routes
│   ├── config/                # Configuration
│   └── main.py               # Entry point
├── tests/                    # Tests
├── scripts/                  # Utility scripts
├── docs/                     # Documentation
├── .husky/                   # Git hooks (pre-commit)
├── package.json              # Node.js config (Husky)
├── pyproject.toml            # Python config (Poetry, Black, isort, mypy)
└── alembic.ini              # Alembic config
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific module
pytest tests/unit/modules/user_management/

# Run integration tests
pytest tests/integration/
```

## 📚 Documentation

- [Architecture Guide](docs/architecture/README.md)
- [API Documentation](docs/api/README.md)
- [Development Guide](docs/development/README.md)

## 🛠️ Development

### Pre-commit Hooks (Husky)

This project uses **Husky** for Git hooks with automatic code quality checks:

```bash
# Install npm dependencies (one-time setup)
npm install

# Hooks run automatically on git commit:
# - isort (import sorting)
# - black (code formatting)
# - mypy (type checking)
```

### Code Formatting

```bash
# Sort imports
isort src tests

# Format code
black src tests

# Type checking
mypy src

# Run all checks manually
sh .husky/pre-commit
```

### Creating a New Module

See [Development Guide](docs/development/creating-modules.md) for detailed instructions.

### Database Migrations

Smart migration script with auto-detection of model changes.

```bash
# Check migration status (no changes)
python scripts/migrate.py --check

# Apply pending migrations (smart - skips if up-to-date)
python scripts/migrate.py

# Create new migration (smart - skips if no model changes)
python scripts/migrate.py --create "add_user_avatar"

# Force create migration even without changes
python scripts/migrate.py --create "init" --force

# Force upgrade even if up-to-date
python scripts/migrate.py --upgrade --force

# Rollback migrations
python scripts/migrate.py --downgrade -1      # Rollback 1 migration
python scripts/migrate.py --downgrade base    # Rollback all

# Show migration info
python scripts/migrate.py --current           # Current revision
python scripts/migrate.py --history           # Migration history
```

### Database Seeding

Smart seeder with idempotent operations.

```bash
# Check what needs seeding (no changes)
python scripts/seed.py --check

# Seed all modules (smart - skips existing data)
python scripts/seed.py

# Force reseed (delete + recreate)
python scripts/seed.py --force

# Seed specific module
python scripts/seed.py --module user
python scripts/seed.py --module file

# Force reseed specific module
python scripts/seed.py --module user --force

# List available modules
python scripts/seed.py --list
```

**Available Seed Modules:**
- `user`: Sample users (admin, john_doe, jane_doe)
- `file`: Sample files (PDF document, JPEG image)

## 🔒 Security

- Change `SECRET_KEY` in production
- Use environment variables for sensitive data
- Enable HTTPS
- Implement authentication/authorization
- Keep dependencies updated

## 📊 API Standards

### Response Format

**Success:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Success message",
  "timestamp": "2024-01-01T00:00:00"
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "details": {}
  },
  "timestamp": "2024-01-01T00:00:00"
}
```

### Endpoints

- `GET /api/v1/resource` - List (paginated)
- `GET /api/v1/resource/{id}` - Get single
- `POST /api/v1/resource` - Create
- `PUT /api/v1/resource/{id}` - Update
- `DELETE /api/v1/resource/{id}` - Delete

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- FastAPI
- SQLAlchemy
- Clean Architecture by Robert C. Martin
- Domain-Driven Design by Eric Evans
