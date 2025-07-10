# Bugninja Platform

> Fully automated AI-based testing that never sleeps

## ⚠️ **CONSTRUCTION WARNING** ⚠️

> **🚧 THIS PROJECT IS CURRENTLY UNDER ACTIVE DEVELOPMENT 🚧**
> 
> **This is an early-stage development version and is NOT ready for production use.**
> - Features are incomplete and may not work as expected
> - Database schemas and APIs are subject to breaking changes
> - Documentation may be outdated or incomplete
> - Use for development and testing purposes only
> 
> **We are actively working on making this production-ready. Stay tuned!**

---

Bugninja is an AI-powered end-to-end testing platform that simulates real users to find bugs in your product before they cost you money. This repository contains the platform components including the frontend dashboard, API, and engine interface.

## 🏗️ Architecture

The platform consists of several key components:

- **Frontend** (Vite + React + TailwindCSS) - Dashboard for test management and visualization
- **API** (FastAPI) - RESTful API with real-time communication
- **Engine Interface** (Python) - Orchestration layer for test execution
- **Database** (Supabase) - Data storage with RLS security
- **Queue** (Redis) - Real-time communication and job queuing

> **Note**: The core testing engine is maintained as a separate installable Python library.

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (required)
- **Node.js 18+** (for local development)

### 🐳 Launch Development Environment

1. **Clone the repository**
```bash
git clone https://github.com/your-org/bugninja-platform.git
cd bugninja-platform
```

2. **Set up environment variables**
```bash
cp .env.example .env
# The default values should work for local development
```

3. **Start all services with Docker Compose**
```bash
docker-compose up --build
```

4. **Access the services**
- 🌐 **Frontend**: http://localhost:3000
- 🔗 **Supabase API**: http://localhost:3001
- 🔐 **Supabase Auth**: http://localhost:9999
- ⚡ **Supabase Realtime**: http://localhost:4000
- 🔴 **Redis**: localhost:6379
- 🐘 **PostgreSQL**: localhost:54322

### 🛑 Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## 📁 Project Structure

```
bugninja-platform/
├── frontend/           # React frontend application
├── api/               # FastAPI backend
├── engine-interface/  # Python orchestration layer
├── supabase/          # Database migrations and config
├── infrastructure/    # Docker, Terraform, K8s configs
└── docs/              # Documentation
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 🔒 Security

For security concerns, please see our [Security Policy](SECURITY.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- [Documentation](docs/)
- [GitHub Issues](https://github.com/your-org/bugninja-platform/issues)
- [Community Discussions](https://github.com/your-org/bugninja-platform/discussions) 