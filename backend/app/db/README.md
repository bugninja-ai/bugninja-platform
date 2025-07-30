# SQLModel Database Models

This directory contains SQLModel-based database models that provide type-safe database operations with seamless FastAPI integration.

## Overview

The SQLModel library combines SQLAlchemy and Pydantic, providing:
- **Type Safety**: Full type checking and validation through Pydantic
- **Database ORM**: Complete SQLAlchemy ORM capabilities
- **API Integration**: Automatic OpenAPI schema generation for FastAPI
- **Single Source of Truth**: One model definition for both database and API operations

## Model Architecture

### Base Classes
- **`TimestampedModel`**: Base class providing `created_at` and `updated_at` timestamp fields
- **`SQLModel`**: Direct inheritance for models that don't need timestamps (e.g., `TestRun`)

### Core Patterns
1. **CUID Primary Keys**: All primary keys use CUID for unique, collision-resistant IDs
2. **Type Safety**: Full type hints with proper `TYPE_CHECKING` imports to avoid circular dependencies
3. **Enumeration Support**: Proper enum implementation with database constraints
4. **JSON Fields**: Native support for JSON and complex data types
5. **Relationship Management**: Bidirectional relationships with proper back-population

## Models

### Core Entities

- **`Project`**: Root entity representing testing initiatives and containing all related resources
- **`Document`**: Stores project documentation and test case content
- **`TestCase`**: Defines specific testing scenarios with goals, rules, and domain restrictions
- **`BrowserConfig`**: Stores browser-specific settings as JSON configuration
- **`TestTraversal`**: Combines test cases with browser configurations for execution
- **`TestRun`**: Tracks actual test executions with detailed outcomes and timing

### Execution Tracking

- **`BrainState`**: AI agent's cognitive state during test execution
- **`Action`**: Specific UI interactions performed by the AI agent (stored as JSON)
- **`HistoryElement`**: Individual action outcomes with timing and visual evidence
- **`Cost`**: AI model usage costs and token consumption tracking

### Configuration & Relationships

- **`SecretValue`**: Sensitive configuration data (API keys, passwords)
- **`TestCaseBrowserConfig`**: Many-to-many relationship between test cases and browser configs
- **`SecretValueTestCase`**: Many-to-many relationship between secrets and test cases

## Enumeration System

The models implement a comprehensive enumeration system for type safety:

### TestRun Enumerations
```python
class RunType(str, enum.Enum):
    AGENTIC = "AGENTIC"
    REPLAY = "REPLAY"
    REPLAY_WITH_HEALING = "REPLAY_WITH_HEALING"

class RunOrigin(str, enum.Enum):
    USER = "USER"
    CICD = "CICD"

class RunState(str, enum.Enum):
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
```

### HistoryElement Enumerations
```python
class HistoryElementState(str, enum.Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
```

### Cost Enumerations
```python
class ModelType(str, enum.Enum):
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    CLAUDE_3 = "claude-3"
```

## Field Types and Patterns

### 1. Basic Fields
```python
# Primary key with CUID
id: str = Field(default=CUID().generate(), primary_key=True, max_length=255)

# String fields with constraints
name: str = Field(max_length=255, nullable=False)
description: str = Field(nullable=False)
```

### 2. Enumeration Fields
```python
# Enum with database constraint
run_type: RunType = Field(
    default=RunType.AGENTIC,
    sa_column=Column(SQLModelEnum(RunType, name="runtype")),
)
```

### 3. JSON Fields
```python
# JSON configuration storage
browser_config: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
action: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
```

### 4. Array Fields
```python
# PostgreSQL array support
allowed_domains: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
```

### 5. Foreign Keys
```python
# Foreign key relationships
project_id: str = Field(max_length=255, nullable=False, foreign_key="project.id")
test_run_id: Optional[str] = Field(default=None, max_length=255, foreign_key="testrun.id")
```

### 6. Relationships
```python
# One-to-many relationships
documents: List["Document"] = Relationship(back_populates="project")
test_cases: List["TestCase"] = Relationship(back_populates="project")

# Many-to-many relationships
browser_configs: List["BrowserConfig"] = Relationship(
    back_populates="test_cases", link_model=TestCaseBrowserConfig
)
```

## Usage Examples

### Creating a New Project
```python
from app.db.sql_models import Project

# Create project with required fields
project = Project(
    name="E-commerce Test Suite",
    default_start_url="https://example.com"
)
```

### Creating a Test Run with Enumerations
```python
from app.db.sql_models import TestRun, RunType, RunOrigin, RunState

# Create test run with proper enum values
test_run = TestRun(
    test_traversal_id="traversal_id",
    browser_config_id="browser_config_id",
    run_type=RunType.AGENTIC,
    origin=RunOrigin.USER,
    current_state=RunState.STARTING,
    repair_was_needed=False,
    run_gif="path/to/animation.gif",
    started_at=datetime.now(timezone.utc),
    finished_at=datetime.now(timezone.utc)
)
```

### Working with JSON Fields
```python
from app.db.sql_models import Action

# Create action with JSON data
action = Action(
    brain_state_id="brain_state_id",
    idx_in_brain_state=0,
    action={
        "type": "click",
        "target": "submit-button",
        "coordinates": {"x": 100, "y": 200}
    },
    dom_element_data={
        "tag": "button",
        "id": "submit-btn",
        "class": "primary-button"
    },
    valid=True
)
```

### Querying with Relationships
```python
from sqlmodel import Session, select

with Session(engine) as session:
    # Get project with all related test cases
    statement = select(Project).where(Project.id == project_id)
    project = session.exec(statement).first()
    
    # Access relationships
    for test_case in project.test_cases:
        print(f"Test case: {test_case.test_name}")
        print(f"Goal: {test_case.test_goal}")
```

### Updating Enumeration Fields
```python
# Update test run state
test_run.current_state = RunState.RUNNING
test_run.repair_was_needed = True
session.add(test_run)
session.commit()
```

## Database Configuration

### Engine Setup
```python
from sqlmodel import create_engine
from app.config import settings

db_engine = create_engine(
    settings.DATABASE_URL, 
    pool_size=50, 
    max_overflow=50
)
```

### Session Management
```python
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=db_engine, 
    class_=Session
)
```

## Benefits

1. **Type Safety**: Full type checking prevents runtime errors
2. **Data Validation**: Automatic validation through Pydantic
3. **API Integration**: Seamless FastAPI integration with automatic schema generation
4. **Enumeration Support**: Type-safe enums with database constraints
5. **JSON Support**: Native JSON field support for complex data
6. **Relationship Management**: Proper bidirectional relationships
7. **Migration Friendly**: Compatible with Alembic for database migrations

## Dependencies

- **`sqlmodel`**: Combines SQLAlchemy and Pydantic
- **`pydantic`**: Data validation and serialization
- **`sqlalchemy`**: Database ORM (used by SQLModel)
- **`cuid2`**: Collision-resistant unique ID generation
- **`enum`**: Python standard library for enumerations

## Notes

- All models maintain consistent table names and relationships
- Foreign key constraints are explicitly defined using the `foreign_key` parameter
- Timestamps use UTC timezone consistently across all models
- Many-to-many relationships use link models for explicit control
- JSON fields provide flexibility for complex configuration storage
- Enumeration fields ensure data integrity and type safety
- Type checking imports prevent circular dependencies
- All primary keys use CUID for unique, collision-resistant IDs 