# Contributing to Bugninja Platform

Thank you for your interest in contributing to Bugninja! This guide will help you get started.

## Development Setup

### Prerequisites

- Node.js 18+
- Python 3.9+
- Docker & Docker Compose
- Supabase CLI
- Git

### Local Development

1. Fork the repository and clone your fork
2. Copy `.env.example` to `.env` and configure
3. Start the development environment:
   ```bash
   docker-compose -f infrastructure/docker/docker-compose.dev.yml up
   ```

## Contribution Workflow

1. **Create an Issue** - For bugs or feature requests
2. **Fork & Branch** - Create a feature branch from `main`
3. **Develop** - Make your changes with tests
4. **Test** - Ensure all tests pass
5. **Commit** - Use conventional commit messages
6. **Pull Request** - Submit for review

## Commit Message Format

We use [Conventional Commits](https://conventionalcommits.org/):

```
type(scope): description

feat(api): add user authentication endpoint
fix(frontend): resolve dashboard loading issue
docs: update installation guide
```

## Code Standards

- **Frontend**: ESLint + Prettier configuration
- **Backend**: Black + isort for Python formatting
- **Tests**: Required for new features
- **Documentation**: Update relevant docs

## Project Structure

- `frontend/` - React application with Vite
- `api/` - FastAPI backend services
- `engine-interface/` - Python orchestration layer
- `supabase/` - Database migrations and config
- `infrastructure/` - Deployment configurations

## Testing

```bash
# Frontend tests
cd frontend && npm test

# Backend tests  
cd api && pytest

# Integration tests
docker-compose -f infrastructure/docker/docker-compose.test.yml up
```

## Getting Help

- Check existing [Issues](https://github.com/your-org/bugninja-platform/issues)
- Join our [Discussions](https://github.com/your-org/bugninja-platform/discussions)
- Review our [Documentation](docs/)

## Code of Conduct

Please review our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing. 