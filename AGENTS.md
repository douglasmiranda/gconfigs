# AGENTS.md

This is a Python project that provides a unified API to access configuration values from different sources (env vars, dotenv files, local mounted files, etc).

## Repo Layout (Important)

- `gconfigs/`: The main package containing the core functionality of the library.
- `tests/`: Contains unit tests for the library. Uses `pytest` for testing.
- `pyproject.toml`: Contains project metadata and dependencies.
- `gconfigs/api.py`: Contains the main user API for accessing configuration values.
- `gconfigs/backends.py`: Contains the implementation of different backends for loading configuration values.
- `gconfigs/gconfigs.py`: Contains the main `GConfigs` class that provides the unified API.

## Agent working rules

- Use uv to run the project and tests.

## Testing

To run the tests, you can use `pytest`:

```bash
uv run pytest
```
