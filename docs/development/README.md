# Development Guide

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Git
- Node.js 18+ (for Husky pre-commit hooks)
- Virtual environment tool (venv, virtualenv, or poetry)

### Setup Development Environment

1. **Clone Repository**
```bash
git clone <repository-url>
cd clean-architecture
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
# Python dependencies
pip install -r requirements.txt
# Or with poetry
poetry install

# Node.js dependencies (for Husky pre-commit hooks)
npm install
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Setup Database**
```bash
createdb modular_db
python scripts/migrate.py --upgrade
python scripts/seed.py
```

6. **Run Application**
```bash
python src/main.py
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow the coding standards and architecture guidelines.

### 3. Run Tests

```bash
pytest
```

### 4. Format Code

```bash
black src tests
isort src tests
```

### 5. Type Check

```bash
mypy src
```

### 6. Run Pre-commit Checks (Optional)

Pre-commit hooks run automatically on `git commit`, but you can run manually:

```bash
sh .husky/pre-commit
```

### 7. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
# Husky pre-commit hooks will run automatically:
# - isort (import sorting)
# - black (code formatting)
# - mypy (type checking)
```

### 8. Push and Create PR

```bash
git push origin feature/your-feature-name
```

## Creating a New Bounded Context

### Step 1: Create Directory Structure

```bash
# Create bounded context structure
mkdir -p src/contexts/your_context/{domain,application,infrastructure}
mkdir -p src/contexts/your_context/domain/{entities,value_objects,events,exceptions}
mkdir -p src/contexts/your_context/application/{commands,queries,dto,ports,facades}

# Create infrastructure models and repositories
mkdir -p src/infrastructure/database/orm/adapters/sqlalchemy/contexts/your_context/{models,repositories}

# Create presentation layer
mkdir -p src/presentation/http/contexts/your_context/{controllers,schemas}
```

### Step 2: Create Domain Layer

```python
# src/contexts/your_context/domain/entities/your_entity.py
from shared.domain.base_aggregate import AggregateRoot

class YourEntity(AggregateRoot):
    def __init__(self, name: str, id: Optional[UUID] = None):
        super().__init__(id)
        self._name = name

    @property
    def name(self) -> str:
        return self._name
```

### Step 3: Create Infrastructure Layer

```python
# src/infrastructure/database/orm/adapters/sqlalchemy/contexts/your_context/models/your_model.py
from sqlalchemy import Column, String
from infrastructure.database.base import register_module_base
from config.settings import get_settings

settings = get_settings()
module_base = register_module_base("your_context", settings.MODULE_SCHEMAS["your_context"])

class YourEntityModel(module_base.BaseModel):
    __tablename__ = "your_entities"
    name = Column(String(255), nullable=False)
```

### Step 4: Implement Repository

```python
# src/infrastructure/database/orm/adapters/sqlalchemy/contexts/your_context/repositories/your_repository.py
from shared.infrastructure.base_repository import BaseRepository

class YourRepository(BaseRepository[YourEntity, YourEntityModel]):
    def _to_entity(self, model: YourEntityModel) -> YourEntity:
        return YourEntity(name=model.name, id=model.id)

    def _to_model(self, entity: YourEntity) -> YourEntityModel:
        return YourEntityModel(id=entity.id, name=entity.name)
```

### Step 5: Create Application Facade

```python
# src/contexts/your_context/application/facades/your_facade.py
class YourFacade:
    def __init__(self, repository: YourRepository):
        self._repository = repository

    async def create(self, dto: CreateDTO) -> ResponseDTO:
        entity = YourEntity.create(dto.name)
        saved = await self._repository.add(entity)
        return self._mapper.to_dto(saved)
```

### Step 6: Create Presentation Layer

```python
# src/presentation/http/contexts/your_context/routes.py
from fastapi import APIRouter

router = APIRouter(prefix="/your-resource", tags=["Your Resource"])

@router.post("/")
async def create(dto: CreateDTO):
    return await controller.create(dto)
```

### Step 7: Create Migration

```bash
python scripts/migrate.py --create "Add your_module tables"
python scripts/migrate.py --upgrade
```

## Pre-commit Hooks (Husky)

This project uses **Husky** for Git hooks with automatic code quality checks.

### How It Works

When you run `git commit`, Husky automatically runs:
1. **isort** - Sorts and organizes imports
2. **black** - Formats code to PEP 8 standard
3. **mypy** - Checks type annotations

If any check fails, the commit is blocked until you fix the issues.

### Configuration Files

| File | Purpose |
|------|---------|
| `package.json` | Husky configuration |
| `.husky/pre-commit` | Pre-commit hook script |
| `pyproject.toml` | isort, black, mypy configuration |
| `.pre-commit-config.yaml` | Alternative pre-commit framework config |

### Manual Check

```bash
# Run all checks manually
sh .husky/pre-commit

# Or run individually
isort --check-only src tests
black --check src tests
mypy src
```

## Code Style Guide

### Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 100
- Use Black for formatting
- Use isort for imports
- Use mypy for type checking

### Naming Conventions

- **Classes**: PascalCase (`UserService`)
- **Functions**: snake_case (`create_user`)
- **Variables**: snake_case (`user_id`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_UPLOAD_SIZE`)
- **Private**: Leading underscore (`_internal_method`)

### Import Order

1. Standard library
2. Third-party packages
3. Local application

```python
import asyncio
from typing import Optional

from fastapi import FastAPI
from sqlalchemy import select

from shared.domain import BaseEntity
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_total(items: List[Item]) -> Decimal:
    """Calculate total price of items.
    
    Args:
        items: List of items to calculate
        
    Returns:
        Total price as Decimal
        
    Raises:
        ValueError: If items list is empty
    """
    pass
```

## Testing

### Unit Tests

```python
# tests/unit/contexts/your_module/test_entity.py
import pytest
from contexts.your_module.domain.entities import YourEntity

def test_create_entity():
    entity = YourEntity.create(name="Test")
    assert entity.name == "Test"
    assert len(entity.domain_events) == 1
```

### Integration Tests

```python
# tests/integration/test_your_repository.py
@pytest.mark.asyncio
async def test_create_and_retrieve(db_session):
    repository = YourRepository(db_session)
    
    entity = YourEntity.create("Test")
    saved = await repository.add(entity)
    
    retrieved = await repository.get_by_id(saved.id)
    assert retrieved.name == "Test"
```

### API Tests

```python
# tests/integration/test_your_api.py
@pytest.mark.asyncio
async def test_create_endpoint(client):
    response = await client.post("/api/v1/your-resource", json={
        "name": "Test"
    })
    assert response.status_code == 201
```

## Database Migrations

### Create Migration

```bash
python scripts/migrate.py --create "Description of changes"
```

### Apply Migrations

```bash
python scripts/migrate.py --upgrade
```

### Rollback

```bash
python scripts/migrate.py --downgrade -1
```

### Migration Best Practices

1. One logical change per migration
2. Test migrations up and down
3. Never modify applied migrations
4. Include data migrations if needed
5. Document complex migrations

## Debugging

### Using debugger

```python
import pdb; pdb.set_trace()
# or
import ipdb; ipdb.set_trace()
```

### VS Code launch.json

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload"],
      "jinja": true
    }
  ]
}
```

## Common Issues

### Issue: Database Connection Error

**Solution**: Check DATABASE_URL in .env

### Issue: Migration Conflicts

**Solution**: 
```bash
python scripts/migrate.py --downgrade base
python scripts/migrate.py --upgrade
```

### Issue: Import Errors

**Solution**: Ensure you're in the project root and venv is activated

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)