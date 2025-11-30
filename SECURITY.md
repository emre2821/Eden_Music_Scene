# Security Policy

## Reporting a Vulnerability

We take the security of Eden Music Scene seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please report security issues by emailing:

📧 **[eden@example.com](mailto:eden@example.com)**

Include the following information in your report:
- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Any suggested fixes (if you have them)

### What to Expect

1. **Acknowledgment**: We will acknowledge receipt of your report within **48 hours**
2. **Assessment**: We will investigate and assess the severity of the issue within **7 days**
3. **Resolution**: We aim to resolve critical vulnerabilities within **30 days**
4. **Disclosure**: Once fixed, we will coordinate with you on public disclosure timing

### What We Commit To

- Treating your report confidentially
- Keeping you informed of our progress
- Crediting you in our security acknowledgments (unless you prefer anonymity)
- Not taking legal action against security researchers who follow this policy

## Supported Versions

We currently provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | ✅ Yes             |

## Security Best Practices

When contributing to or deploying Eden Music Scene, please follow these practices:

### For Contributors

- **Never commit secrets** – Don't commit API keys, passwords, or tokens to the repository
- **Use environment variables** – Store sensitive configuration in environment variables
- **Validate inputs** – Always validate and sanitize user inputs
- **Keep dependencies updated** – Regularly update dependencies to patch known vulnerabilities
- **Review before merging** – Carefully review code changes for security implications

### For Deployers

- **Use HTTPS** – Always deploy services behind HTTPS in production
- **Restrict access** – Use firewall rules and access controls appropriately
- **Monitor logs** – Watch for unusual activity in application logs
- **Regular updates** – Keep the application and its dependencies up to date
- **Secure credentials** – Use a secrets manager for sensitive configuration

## Known Security Considerations

### Emotion Service

The `emotion_service.py` REST API is designed for local development and testing. When deploying to production:

- Add authentication/authorization
- Use HTTPS
- Configure appropriate CORS settings
- Consider rate limiting

### Database

The default SQLite database (`EMOTION_DB_URL`) is suitable for development but for production consider:

- Using PostgreSQL or another production database
- Implementing proper backup procedures
- Encrypting sensitive data at rest

## Dependency Security

We use the following tools to maintain dependency security:

- **Dependabot** – Automated dependency updates
- **pip-audit** – Python dependency vulnerability scanning
- **npm audit** – Node.js dependency vulnerability scanning

Run security audits locally:

```bash
# Python dependencies
pip install pip-audit
pip-audit

# Node.js dependencies (in apps/frontend)
cd apps/frontend
npm audit
```

## Security Acknowledgments

We would like to thank the following individuals for responsibly disclosing security issues:

*No acknowledgments yet. Be the first to help us improve our security!*

---

Thank you for helping keep Eden Music Scene secure! 🔒
