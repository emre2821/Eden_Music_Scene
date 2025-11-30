# Contributing to Eden Music Scene

Welcome to the Eden Music Scene! We're thrilled that you're interested in contributing to this project. Whether you're fixing bugs, adding features, improving documentation, or sharing ideas, your contribution makes the resonance lab stronger.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Making Changes](#making-changes)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/Eden_Music_Scene.git
   cd Eden_Music_Scene
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/emre2821/Eden_Music_Scene.git
   ```

## Development Environment Setup

This repository is a monorepo containing both Python backend services and a React/TypeScript frontend. You'll need to set up both environments depending on what you're working on.

### Python Backend Setup

**Requirements**: Python 3.10 or higher

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# (Optional) Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### Frontend Setup

**Requirements**: Node.js 18+ and npm

```bash
cd apps/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Environment Variables

Copy the example environment file and configure as needed:

```bash
cp .env.example .env
```

Key environment variables:
- `EMOTION_DB_URL`: Database URL for the emotion tag service (default: SQLite)
- `EMOTION_SERVICE_URL`: Base URL for the emotion service API

## Project Structure

```
/
├── apps/
│   ├── backend/          # Python services and agents
│   │   ├── EchoDJ/       # DJ/curation agent
│   │   ├── EchoPlay/     # Playback client
│   │   └── emotion_*.py  # Emotion tag services
│   └── frontend/         # React/TypeScript web app (EchoSplit)
├── tests/                # Root-level tests
├── docs/                 # Documentation
└── scripts/              # Build and release scripts
```

## Making Changes

1. **Create a feature branch** from `main`:
   ```bash
   git checkout main
   git pull upstream main
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our code style guidelines

3. **Write or update tests** for your changes

4. **Run the test suite** to ensure nothing is broken:
   ```bash
   pytest
   ```

5. **Commit your changes** with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: brief description of change"
   ```

## Code Style

We value consistent, readable code. Please follow these guidelines:

### Python (Backend)

- **Formatter**: We use [Black](https://black.readthedocs.io/) with a line length of 88
- **Linter**: We use [Ruff](https://github.com/astral-sh/ruff) for linting
- **Type hints**: Use type annotations where practical
- **Docstrings**: Use Google-style docstrings for public functions and classes

```bash
# Format code
black .

# Lint code
ruff check .

# Auto-fix linting issues
ruff check --fix .
```

### TypeScript/React (Frontend)

- **Formatter**: We use [Prettier](https://prettier.io/) for formatting
- **TypeScript**: Enable strict mode; avoid `any` types where possible
- **Components**: Use functional components with hooks
- **Naming**: Use PascalCase for components, camelCase for functions and variables

```bash
cd apps/frontend

# Format code
npm run format  # if available, or: npx prettier --write .

# Type check
npm run typecheck  # if available, or: npx tsc --noEmit
```

### General Guidelines

- Keep functions focused and small
- Write self-documenting code with clear variable names
- Add comments only when the "why" isn't obvious from the code
- Remove dead code rather than commenting it out

## Testing

We use [pytest](https://pytest.org/) for Python testing. All new features and bug fixes should include tests.

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_emotion_service.py

# Run tests with coverage
pytest --cov=apps/backend
```

### Writing Tests

- Place tests in the `tests/` directory or alongside the code in `*_test.py` files
- Use descriptive test names that explain what's being tested
- Follow the Arrange-Act-Assert pattern
- Use fixtures for common setup

Example:
```python
def test_emotion_tag_validation_rejects_invalid_intensity():
    """Intensity values outside 0-1 range should be rejected."""
    invalid_tag = {"track_id": "123", "emotion": "joy", "intensity": 1.5}
    
    with pytest.raises(ValueError, match="intensity must be between 0 and 1"):
        validate_tag(invalid_tag)
```

## Pull Request Process

1. **Update your branch** with the latest changes from `main`:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Open a Pull Request** on GitHub with:
   - A clear title describing the change
   - A description explaining what changed and why
   - Reference to any related issues (e.g., "Fixes #123")

4. **Address review feedback** - We review all PRs and may request changes. This is a collaborative process!

5. **CI checks must pass** - Your PR must pass all automated tests and linting checks

### What We Look For in PRs

- Does the code work as intended?
- Are there adequate tests?
- Is the code readable and maintainable?
- Does it follow our style guidelines?
- Is the commit history clean and logical?

## Community

### Getting Help

- **Questions?** Open a GitHub Discussion or Issue
- **Found a bug?** Please open an Issue with reproduction steps
- **Security concerns?** See [SECURITY.md](SECURITY.md)

### Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md). We're building a welcoming, inclusive community.

---

Thank you for contributing to Eden Music Scene! Every contribution, no matter how small, helps make this project better. We're grateful for your time and effort. 💜
