"""
gConfigs - Config and Secret parser for Python applications.

Nothing shows better than some snippets:

    ```python
    import gconfigs

    envs = gconfigs.envs()
    HOME = envs('HOME')
    DEBUG = envs.as_bool('DEBUG', default=False)
    DATABASE_USER = envs('DATABASE_USER')
    secrets = gconfigs.local_file()
    DATABASE_PASS = secrets('/run/secrets/DATABASE_PASS')

    >>> import gconfigs
    >>> envs = gconfigs.envs()
    >>> HOME = envs('HOME')
    >>> HOME
    '/root'
    >>> for env in envs:
    ...     print(env)
    ...     print(env.key)
    ...     print(env.value)
    ...
    EnvironmentVariable(key='ENV_TEST', value='env-test-1')
    ENV_TEST
    env-test-1
    ...

    >>> 'ENV_TEST' in envs
    True

    >>> envs.json()
    '{"ENV_TEST": "env-test-1", "HOME": "/root", ...}'
    ```
"""

from importlib.metadata import version

from .api import (  # noqa: F401
    dotenvs,
    envs,
    ini_file,
    local_file,
    local_files,
    toml_file,
)

__version__ = version("gconfigs")
