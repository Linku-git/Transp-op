---
name: security-check
description: Run security scanning tools and OWASP checklist. Use before merging security-sensitive code or during Phase 4/7 sessions.
arguments:
  - name: scope
    description: "Scope: all, backend, frontend, or mobile (default: all)"
    required: false
---

# Security Check

Based on scope (default: all):

## Backend (Python)
```bash
cd backend && python -m bandit -r app/ -f json -o bandit-report.json
cd backend && pip-audit
```

## Frontend (Node)
```bash
cd frontend && npm audit --audit-level=moderate
```

## Mobile (Flutter)
```bash
cd mobile && flutter pub outdated
```

## Cross-Stack Checks
1. **Secrets scan**: Search for hardcoded secrets, API keys, passwords
   ```bash
   grep -rn "password\|secret\|api_key\|token" --include="*.py" --include="*.ts" --include="*.dart" backend/ frontend/ mobile/ | grep -v "test" | grep -v "node_modules"
   ```
2. **Env file check**: Verify `.env` is in `.gitignore` and never committed
   ```bash
   git log --all --diff-filter=A -- "*.env" ".env*"
   ```
3. **Debug mode check**: Ensure DEBUG=False patterns in production configs
4. **CORS check**: Verify CORS origins are restricted (not `*`)

## Report
- Vulnerabilities found (critical/high/medium/low)
- Hardcoded secrets detected
- Outdated dependencies with known CVEs
- OWASP checklist items that need attention
