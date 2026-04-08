# Developer Guidelines

## Getting Started

### Prerequisites

- Python 3.12
- [Poetry](https://python-poetry.org/) (dependency management for Python)
- Node.js 22.18.0 and Yarn (check `ui/package.json` for exact node version)
- Git LFS (required when cloning knowledge packs)

### macOS Setup (automated)

Run the install script from the repo root to install all dev dependencies:

```bash
./install_dev_dependencies.sh
```

This installs Python 3.12, Poetry, nvm, Node 22.18.0, Yarn, the Haiven CLI, pre-commit hooks, and Gitleaks.

### Manual Setup

```bash
# From repo root: install app dependencies
poetry run init
# Equivalent to:
cd app && poetry install --no-root
cd ../ui && yarn install
```

### Environment Configuration

Copy a `.env` template to `app/.env` based on your LLM provider:

```bash
cp app/.env.azure.template app/.env      # Azure OpenAI
cp app/.env.ollama.template app/.env     # Ollama (local)
# Edit app/.env and fill in your API credentials
```

Set `AUTH_SWITCHED_OFF=true` in `.env` to skip OAuth setup during local development.

---

## Running the App

### Backend (FastAPI)

From the repo root:

```bash
poetry run app
# Equivalent to: cd app && poetry run python main.py
```

The backend starts on `http://localhost:8080`.

### Frontend (Next.js / hot reload)

In a separate terminal:

```bash
cd ui
yarn install
yarn dev
```

The UI starts on `http://localhost:3000` and connects to the backend at `localhost:8080`.

### Build the UI for Production

```bash
cd ui
yarn run build
cp -rf out ../app/resources/static/
```

Or via the script: `poetry run build` from the repo root.

---

## Running Tests

### Standard Test Run

```bash
poetry run test
# Equivalent to: cd app && poetry run pytest -m 'not integration and not slow_integration'
```

This excludes slow integration tests for fast development feedback. Expected run time: ~1–2 minutes.

### With Coverage

```bash
cd app && poetry run pytest --cov=. --cov-report=term -m 'not integration and not slow_integration'
```

### Frontend Tests

```bash
cd ui && yarn vitest run
```

### Slow Integration Tests

Some tests are marked as slow integration tests and are skipped during regular test runs. These tests perform real operations (like Firestore database calls).

#### Skipped Tests
- `test_firestore_integration.py` — Tests complete Firestore integration
- `test_json_serialization.py` — Tests JSON serialization with real Firestore operations

#### Running Slow Tests

```bash
# Run Firestore integration test
cd app && poetry run pytest test_firestore_integration.py -v

# Run JSON serialization test
cd app && poetry run pytest test_json_serialization.py -v

# Run all slow integration tests
cd app && poetry run pytest -m "slow_integration"

# Run all tests (including slow ones) - not recommended for regular development
cd app && poetry run pytest
```

**Note:** The regular `poetry run test` command automatically excludes slow integration tests for faster development feedback.

#### When to Run Slow Tests

Run these tests when:
- Making changes to Firestore integration code
- Modifying API key authentication logic
- Testing JSON serialization fixes
- Before deploying to production
- When debugging Firestore-related issues

#### Test Performance

Regular test suite: ~1-2 minutes
With slow tests: ~3-5 minutes

The slow tests are skipped by default to maintain fast feedback during development.

### Test Best Practices

1. **Unit tests should be fast** - Use mocks for external dependencies
2. **Integration tests can be slow** - But should be clearly marked
3. **Use `@pytest.mark.skip`** for tests that shouldn't run in CI
4. **Add clear skip reasons** with instructions on how to run manually

---

## Code Standards

Standards are defined in `CHARTER.yaml` per zone. Key rules:

### Python (app-api, app-services, app-core, cli)

- Type hints on all function parameters and return types
- Constructor dependency injection (no global state)
- Abstract base classes for provider-agnostic interfaces
- Functions under 20 lines where possible
- Max 300 lines per file
- No hardcoded credentials or secrets
- No `eval()` or `exec()` on user-controlled input

### TypeScript / React (ui-components)

- Functional components with hooks only (no class-based components)
- Remix icons exclusively — no other icon libraries
- Tailwind CSS for styling; no inline CSS
- Ant Design component library
- Client-only mode (no Next.js server-side rendering features)
- No JSDoc comments
- Max 300 lines per file

### General

- Target test coverage: 80% for backend zones, 70% for UI components
- Do not directly embed business logic in API endpoint handlers
- Pydantic models for request/response validation

---

## Git Workflow

1. **Branch from `main`** — create a feature or fix branch:
   ```bash
   git checkout -b fix/description-of-change
   # or
   git checkout -b feat/description-of-feature
   ```

2. **Make focused commits** — one logical change per commit with a descriptive message.

3. **Run tests before pushing**:
   ```bash
   poetry run test
   ```

4. **Open a pull request against `main`** — include a clear description of what changed and why.

5. **Do not force push to `main`** — protected branch.

Pre-commit hooks run Gitleaks to prevent accidental secret commits. If a hook fails, fix the issue before committing.
