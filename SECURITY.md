# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### Private Disclosure

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please email us at: **security@bugninja.ai**

Include the following information:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 24 hours
- **Initial Assessment**: Within 72 hours
- **Status Updates**: Weekly until resolved
- **Resolution Timeline**: Depends on severity
  - Critical: 1-3 days
  - High: 1-2 weeks
  - Medium: 2-4 weeks
  - Low: Next major release

## Security Best Practices

### For Contributors

- Never commit secrets, API keys, or credentials
- Use environment variables for sensitive configuration
- Follow secure coding practices
- Keep dependencies updated
- Review code for potential security issues

### For Users

- Use strong, unique passwords
- Enable two-factor authentication
- Keep your installation updated
- Follow the principle of least privilege
- Regularly review access logs

## Security Features

- **Authentication**: Supabase Auth with RLS
- **Authorization**: Role-based access control
- **Data Protection**: Encryption at rest and in transit
- **API Security**: Rate limiting and input validation
- **Infrastructure**: Containerized deployment

## Scope

This security policy covers:
- The Bugninja platform codebase
- Official Docker images
- Documentation and examples

This policy does NOT cover:
- Third-party integrations
- User-deployed instances
- The separate engine library

## Attribution

For questions about this security policy, contact security@bugninja.ai. 