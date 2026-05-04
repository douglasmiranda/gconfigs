from .backends import DotEnv, File, INIFile, LocalEnv, LocalFiles
from .gconfigs import GConfigs


def envs():
    """Provides access to environment variables available in the system.

    Returns:
        GConfigs: An instance of GConfigs with LocalEnv backend and object_type_name 'EnvironmentVariable'.

    Example:
        ```python
        import gconfigs
        envs = gconfigs.envs()
        home = envs("HOME")
        print("HOME:", home)
        ```
    """
    return GConfigs(backend=LocalEnv, object_type_name="EnvironmentVariable")


def dotenvs(filepath=".env"):
    """Provides access to environment variables defined in a .env file.

    Args:
        filepath (str): The path to the .env file. Defaults to ".env".
    Returns:
        GConfigs: An instance of GConfigs with DotEnv backend and object_type_name 'DotEnvConfig'.

    Example:
        ```python
        import gconfigs
        dotenvs = gconfigs.dotenvs("./path/to/.env")
        my_config = dotenvs("MY_CONFIG")
        print("MY_CONFIG:", my_config)
        ```
    """
    return GConfigs(backend=DotEnv(filepath=filepath), object_type_name="DotEnvConfig")


def local_files(path="/run/configs", pattern="*"):
    """Provides access to files in a local directory, which is useful for accessing mounted files in containerized environments.

    Args:
        path (str): The path to the directory containing the files. Defaults to "/run/configs".
        pattern (str): The glob pattern to match files. Defaults to "*", which matches all files.
    Returns:
        GConfigs: An instance of GConfigs with LocalFiles backend and object_type_name 'Config'.

    Example:
        ```python
        import gconfigs
        secrets = gconfigs.local_files("/run/secrets")
        secret_key = secrets("SECRET_KEY")
        print("SECRET_KEY:", secret_key)
        ```
    """
    return GConfigs(
        backend=LocalFiles(path=path, pattern=pattern),
        object_type_name="Config",
    )


def local_file():
    """Provides access to a single local file, which is useful for accessing mounted files in containerized environments.

    Returns:
        GConfigs: An instance of GConfigs with File backend and object_type_name 'FileConfig'.

    Example:
        ```python
        import gconfigs
        config = gconfigs.local_file()
        password = config("/path/to/config/PASSWORD")
        print("PASSWORD:", password)
        ```
    """
    return GConfigs(backend=File(), object_type_name="FileConfig")


def ini_file(filepath=".ini"):
    """Provides access to configuration values defined in an .ini file.

    Args:
        filepath (str): The path to the .ini file. Defaults to ".ini".
    Returns:
        GConfigs: An instance of GConfigs with INIFile backend and object_type_name 'INIConfig'.

    Example:
        ```python
        import gconfigs
        ini = gconfigs.ini_file("./path/to/config.ini")
        app_name = ini("app.name")
        print("app.name:", app_name)
        ```
    """
    return GConfigs(backend=INIFile(filepath=filepath), object_type_name="INIConfig")
