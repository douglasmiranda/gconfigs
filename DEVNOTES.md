# Dev Notes

Random notes about development of gconfigs.

## Publishing to Test PyPI

pyproject.toml:

```toml
[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
explicit = true
```

```
uv version <NEW_VERSION> --frozen
uv build --no-sources
uv publish --token=<PYPI_TOKEN> --index=testpypi
```

Testing:

```
uv run --with "gconfigs==<NEW_VERSION>" --no-project --refresh-package gconfigs -- python -c "import gconfigs; print(gconfigs.__version__)"
```
