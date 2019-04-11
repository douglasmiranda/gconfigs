# -*- coding: utf-8 -*-

"""
gConfigs - Config and Secret parser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Nothing shows better than some snippets:

    from gconfigs import envs, configs, secrets

    HOME = envs('HOME')
    DEBUG = configs.as_bool('DEBUG', default=False)
    DATABASE_USER = configs('DATABASE_USER')
    DATABASE_PASS = secrets('DATABASE_PASS')

    >>> # envs, configs and secrets are iterables
    >>> from gconfigs import envs
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
"""

__author__ = """Douglas Miranda"""
__email__ = "douglascoding@gmail.com"
__version__ = "0.1.5"


from .gconfigs import GConfigs
from .backends import LocalEnv, DotEnv, LocalMountFile


envs = GConfigs(backend=LocalEnv, object_type_name="EnvironmentVariable")
dotenvs = GConfigs(backend=DotEnv, object_type_name="DotEnvConfig")
configs = GConfigs(
    backend=LocalMountFile(root_dir="/run/configs"), object_type_name="Config"
)
secrets = GConfigs(
    backend=LocalMountFile(root_dir="/run/secrets"), object_type_name="Secret"
)
