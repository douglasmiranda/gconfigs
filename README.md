# gConfigs

Configuration helper for Python applications.

gConfigs provides a unified API to read configuration values from different sources:

- Environment variables
- Dotenv files
- INI files
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
debug = envs("DEBUG", default=False, cast=bool)
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

# 5) INI file
ini = gconfigs.ini_file("./config/settings.ini")
app_name = ini("app.name", default="my-app")
```

## API Overview

The package exposes five factory functions:

- gconfigs.envs() -> reads from process environment variables
- gconfigs.dotenvs(filepath=".env") -> reads from dotenv files
- gconfigs.ini_file(filepath=".ini") -> reads from INI files using section.option keys
- gconfigs.local_files(path="/run/configs", pattern="*") -> reads from files in a directory
- gconfigs.local_file() -> reads from a single file path provided at call time

Each factory returns a GConfigs instance.

Main call signature:

```python
GConfigs.get(key, *, default=NOTSET, use_instead=NOTSET, strip=None, cast=None, list_sep=None, bool_values=None, **backend_kwargs)
```

## Usage

### Environment Variables

```python
import gconfigs

envs = gconfigs.envs()

home = envs("HOME")
workers = envs("WORKERS", default="2", cast=int)
debug = envs("DEBUG", default=False, cast=bool)
```

### Dotenv Files

```python
import gconfigs

dotenvs = gconfigs.dotenvs("./config/.env")
dsn = dotenvs("DATABASE_DSN")

# load another dotenv file with a different GConfigs instance
other = gconfigs.dotenvs("./config/another.env")
```

### INI Files

```python
import gconfigs

ini = gconfigs.ini_file("./config/settings.ini")

app_name = ini("app.name")
db_host = ini("database.host")
db_port = ini("database.port", cast=int)
```

INI parser behavior:

- Keys use section.option format
- Values are read as strings by default
- Use cast to convert values
- Missing section/option raises KeyError

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

Use cast in GConfigs.get (or by calling the instance directly) to convert values.

### Boolean

- Accepts native bool values
- Accepts case-insensitive string pairs from bool_values
- Default bool_values pairs:
  - ("true", "false")
  - ("1", "0")
  - ("yes", "no")
  - ("y", "n")
  - ("on", "off")

```python
debug = envs("DEBUG", default=False, cast=bool)
feature_enabled = envs(
    "FEATURE_X",
    cast=bool,
    bool_values=(("enabled", "disabled"),),
)
```

### list, tuple, and set

- Accepts native iterable values for conversion between list/tuple/set
- Accepts JSON-style list strings like "[1, 2, 3]"
- Accepts separator-delimited strings using list_sep

```python
hosts = envs("ALLOWED_HOSTS", cast=list)
hosts_csv = envs("ALLOWED_HOSTS_CSV", cast=list, list_sep=",")
hosts_pipe = envs("ALLOWED_HOSTS_PIPE", cast=list, list_sep="|")

coords = envs("COORDS", cast=tuple)
labels = envs("LABELS", cast=set)
```

### dict

- Accepts native dict values
- Accepts JSON-style object strings like "{\"workers\": 2}"

```python
options = envs("APP_OPTIONS", cast=dict)
```

### Custom cast function or type

```python
from decimal import Decimal

price = envs("PRICE", cast=Decimal)


def normalize_slug(value):
    return str(value).strip().lower().replace(" ", "-")


slug = envs("PROJECT_NAME", cast=normalize_slug)
```

## Output Formatting with ValueOutput

GConfigs delegates output conversion and strip behavior to ValueOutput.

Default behavior:

- strip=True
- list_sep=","
- bool_values as described in the casting section

You can pass a custom ValueOutput instance to GConfigs:

```python
from gconfigs.gconfigs import GConfigs, ValueOutput


class DictBackend:
    def __init__(self):
        self.data = {"DEBUG": "enabled", "HOSTS": "a|b|c"}

    def keys(self):
        return self.data.keys()

    def get(self, key, **backend_kwargs):
        if key not in self.data:
            raise KeyError(f"{key} not set")
        return self.data[key]


output_fmt = ValueOutput(list_sep="|", bool_values=(("enabled", "disabled"),))
configs = GConfigs(backend=DictBackend, output_fmt=output_fmt)

debug = configs("DEBUG", cast=bool)
hosts = configs("HOSTS", cast=list)
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

- get(key: str, **backend_kwargs)
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

    def get(self, key, **backend_kwargs):
        if key not in self.data:
            raise KeyError(f"{key} not set")
        return self.data[key]


configs = GConfigs(backend=DictBackend)
name = configs("NAME")
debug = configs("DEBUG", cast=bool)

# You can access the backend instance directly from GConfigs instance
assert configs.backend.additional_method
```

## License

MIT. See [LICENSE-MIT](LICENSE-MIT).
