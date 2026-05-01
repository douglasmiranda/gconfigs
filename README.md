# gConfigs

Configuration helper for Python applications.

gConfigs provides a unified API to read configuration values from different sources:

- Environment variables
- Dotenv files
- Local mounted files in a directory
- Individual local files

Why another config library?
> I made it for myself. That's it.

## Installation

Python 3.10+

```bash
pip install gconfigs
```

or with uv:

```bash
uv add gconfigs
```

Or even better. It's small enough, avoid the dependency entirely, and copy [gconfigs/](src/gconfigs/) into your project.

Extra effort to convince you to avoid dependencies: maybe all you need is just [os.environ](https://docs.python.org/3/library/os.html#os.environ).

## Quick Start

```python
import gconfigs

# 1) Environment variables
envs = gconfigs.envs()
debug = envs.as_bool("DEBUG", default=False)
home = envs("HOME", default="/")

# 2) Mounted directory (for configs or secrets)
configs = gconfigs.local_files("/run/configs")
language_code = configs("LANGUAGE_CODE", default="en-us")

# 3) Single local file
secrets = gconfigs.local_file()
db_password = secrets("/run/secrets/DB_PASSWORD")

# 4) Dotenv file
dotenvs = gconfigs.dotenvs(".env")
project_name = dotenvs("PROJECT_NAME", default="my-app")
```

## API Overview

The package exposes four factory functions:

- gconfigs.envs() -> reads from process environment variables
- gconfigs.dotenvs(filepath=".env") -> reads from dotenv files
- gconfigs.local_files(path="/run/configs", pattern="*") -> reads from files in a directory
- gconfigs.local_file() -> reads from a single file path provided at call time

Each factory returns a GConfigs instance.

## Usage

### Environment Variables

```python
import gconfigs

envs = gconfigs.envs()

home = envs("HOME")
workers = int(envs("WORKERS", default="2"))
debug = envs.as_bool("DEBUG", default=False)
```

### Dotenv Files

```python
import gconfigs

dotenvs = gconfigs.dotenvs("./config/.env")
dsn = dotenvs("DATABASE_DSN")

# load another dotenv file with a different GConfigs instance
other = gconfigs.dotenvs("./config/another.env")
```

Dotenv parser behavior:

- Ignores lines starting with #, ;, and [section]
- Ignores lines without =
- Splits at the first = so values can contain =
- Strips key whitespace
- Preserves value whitespace (except trailing newline characters)
- Last duplicated key wins

### Local Mounted Files (Directory)

```python
import gconfigs

configs = gconfigs.local_files("/run/configs")
secrets = gconfigs.local_files("/run/secrets")

api_url = configs("API_URL")
api_key = secrets("API_KEY")
```

How it works:

- Relative file path is the config key
- File content is the config value
- Optional pattern argument filters which files are considered
- Keys are file names directly inside the configured base path
- Reads are restricted to the configured base path (path traversal like `../secret` is blocked)
- Recursive access is intentionally not supported (nested paths like `nested/key.txt` are rejected)

```python
only_app = gconfigs.local_files("/run/configs", pattern="APP_*")
```

\* Uses fnmatch for pattern matching. [fnmatch docs](https://docs.python.org/3/library/fnmatch.html)

### Single Local File

```python
import gconfigs

secrets = gconfigs.local_file()
token = secrets("/run/secrets/SERVICE_TOKEN")
```

## Common Patterns

### Default Value

```python
port = envs("PORT", default="8000")
```

### Fallback Key with use_instead

```python
host = envs("SERVICE_HOST", use_instead="HOST", default="127.0.0.1")
```

### Strip Control

By default, returned string values are stripped.

```python
value = envs("MY_KEY")  # strip=True by default
raw_value = envs("MY_KEY", strip=False)
```

## Type Casting

`GConfigs` provides strict casting helpers.

### as_bool

- Accepts native bool values
- Accepts strings "true" and "false" (case-insensitive)
- Raises ValueError for other values

```python
debug = envs.as_bool("DEBUG", default=False)
```

### as_list

- Accepts native list and tuple values
- Accepts JSON-style list strings like "[1, 2, 3]"
- Raises ValueError otherwise

```python
hosts = envs.as_list("ALLOWED_HOSTS")
```

### as_dict

- Accepts native dict values
- Accepts JSON-style object strings like "{\"workers\": 2}"
- Raises ValueError otherwise

```python
options = envs.as_dict("APP_OPTIONS")
```

## Iteration and Utilities

`GConfigs` implements container and iterator protocols.

```python
import gconfigs

envs = gconfigs.envs()

if "HOME" in envs:
    print("HOME exists")

print(len(envs))

for item in envs:
    print(item.key, item.value)

print(envs.json())
```

Notes:

- Iteration yields namedtuples with key and value fields
- Use .iterator() when you need a fresh independent iterator

## Error Behavior

Typical exceptions you may see:

- KeyError for missing environment variable or missing dotenv key
- FileNotFoundError for missing paths/files in file backends
- PermissionError for unreadable files in local_file backend
- ValueError for invalid cast values

Use default=... to avoid exceptions for missing keys when appropriate.

## Custom Backend

You can plug your own backend into `GConfigs`.

Required backend methods:

- get(key: str)
- keys()

Example:

```python
from gconfigs.gconfigs import GConfigs


class DictBackend:
    def __init__(self):
        self.data = {"NAME": "my-app", "DEBUG": "false"}

    def additional_method(self):
        return "This is an additional method in the backend class."

    def keys(self):
        return self.data.keys()

    def get(self, key):
        if key not in self.data:
            raise KeyError(f"{key} not set")
        return self.data[key]


configs = GConfigs(backend=DictBackend)
name = configs("NAME")
debug = configs.as_bool("DEBUG")

# You can access the backend instance directly from GConfigs instance
assert configs.backend.additional_method
```

## License

MIT. See [LICENSE-MIT](LICENSE-MIT).
