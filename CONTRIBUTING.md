# Astronomy Calculator - Contributing Guide

## Branch Strategy

- **`main`** - Production-ready code, protected branch
- **`develop`** - Integration branch for features
- **`feature/*`** - New features (e.g., `feature/moon-api`)
- **`fix/*`** - Bug fixes (e.g., `fix/timezone-handling`)

## Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and commit:**
   ```bash
   git add .
   git commit -m "Add: description of your changes"
   ```

3. **Push to GitHub:**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub
   - The CI pipeline will automatically run
   - All checks must pass before merging

## What Gets Checked Automatically

Every pull request runs:
- ✅ **Test Suite** - All unit tests must pass
- ✅ **Coverage Report** - Code coverage analysis
- ✅ **Bandit** - Security vulnerability scanning
- ✅ **pip-audit** - Dependency vulnerability check
- ✅ **Pylint** - Code quality analysis
- ✅ **Radon** - Complexity metrics

## Running Checks Locally

Before creating a PR, run these locally:

```bash
# Run tests
pytest tests/ --cov=.

# Security scan
bandit -r . -x ./tests,./htmlcov,./__pycache__,./.venv

# Dependency check
pip-audit

# Code quality
pylint *.py
radon cc . -a
```

## Code Standards

- Python 3.14+ features encouraged
- Type hints preferred
- Docstrings required for public functions
- Test coverage for new features
- No security vulnerabilities tolerated

## For External Contributors

🎉 External contributions are welcome! If you're not the project owner:
- Fork the repository
- Create your feature branch
- Ensure all CI checks pass
- Submit a PR with clear description

Thank you for contributing to making astronomy calculations accessible! 🌙✨
