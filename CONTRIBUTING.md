# AegisPy Development Guidelines

## Code Style

- Python 3.11+
- Type hints required
- PEP 8 compliant
- Docstrings for all public functions/classes
- Logging with `logging` module

## Commit Messages

- Use imperative mood: "Add feature" not "Added feature"
- Keep subject line under 50 characters
- Reference issues when applicable

## Testing

Run tests before pushing:
```bash
pytest tests/ -v
```

## Linting

```bash
ruff check .
black --check .
mypy .
```

## Security

- Never commit secrets or credentials
- Always validate user input
- Use parameterized queries for databases
- Follow principle of least privilege
