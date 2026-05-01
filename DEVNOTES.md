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

## Composite Backend

Thinking about a composite backend...

```python
class Composite:
    def __init__(self, backends):
        self.backends = [self._ensure_backend_instance(backend) for backend in backends]

    def _ensure_backend_instance(self, backend):
        instance = backend() if callable(backend) else backend
        if not (hasattr(instance, "get") and hasattr(instance, "keys")):
            raise AttributeError(
                "Each backend must have at least the methods 'get' and 'keys'."
            )

        return instance

    def keys(self):
        seen = set()
        for backend in self.backends:
            for key in backend.keys():
                if key in seen:
                    continue

                seen.add(key)
                yield key

    def get(self, key, **kwargs):
        last_error = None
        for backend in self.backends:
            try:
                return backend.get(key, **kwargs)
            except Exception as e:  # noqa: BLE001
                last_error = e

        raise KeyError(
            f"The config '{key}' is not set in any configured backend."
        ) from (last_error)


def composite(backends):
    """Provides access to multiple backends using ordered fallback precedence.

    Args:
        backends (iterable): Ordered backend instances/classes. Earlier backends
            have higher precedence on ``get`` and key iteration.
    Returns:
        GConfigs: An instance of GConfigs with Composite backend and object_type_name 'CompositeConfig'.
    """
    return GConfigs(
        backend=Composite(backends=backends), object_type_name="CompositeConfig"
    )


# Then test precedence and merge
```
