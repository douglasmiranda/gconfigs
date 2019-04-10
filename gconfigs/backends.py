"""
Backends for gConfigs
~~~~~~~~~~~~~~~~~~~~~

Backends are just simple classes with at least two methods implemented:
`get` and `keys`.

Example:

    class RedisBackend:
        def keys(self):
            # return a iterable of all keys available
            return available_keys

        def get(self, key: str):
            # this method receive a key (identifier of a config)
            # and return its respective value
            return value

Notes:
    - If it's not possible to provide a `.keys` method, just declare with:
    raise NotImplementedError. Of course it will limit the goodies of gConfigs.
    - For errors on `.get` method just throw exceptions.
    (Config doesn't exists, you don't have permission, stuff like that)
    See `GConfigs.get` and you'll see that it has a `default` parameter,
    and of course if you provide a default value it will not throw a exception.
"""
from pathlib import Path
import os


class LocalEnv:
    def keys(self):
        return os.environ.keys()

    def get(self, key, **kwargs):
        value = os.environ.get(key)
        if value is None:
            raise KeyError(
                f"Environment variable '{key}' not set. Check for any "
                "misconfiguration or misspelling of the variable name."
            )

        return value


class LocalMountFile:
    def __init__(self, root_dir="/", pattern="*"):
        self.pattern = pattern
        self.root_dir = root_dir

    @property
    def root_dir(self):
        if not self._root_dir.exists():
            raise RootDirectoryNotFound(
                f"The root directory {self._root_dir} doesn't exist."
            )

        return self._root_dir

    @root_dir.setter
    def root_dir(self, root_dir):
        self._root_dir = Path(root_dir)

    def keys(self):
        for item in self.root_dir.glob(self.pattern):
            if item.is_file():
                yield item.name

    def get(self, key, **kwargs):
        file = self.root_dir / key
        if file.exists():
            return file.read_text()

        raise FileNotFoundError(
            f"Check if your files are mounted on {self.root_dir}. "
            "And remember to check if your system is case sensitive."
        )


class DotEnv:
    def keys(self):
        return self._data.keys()

    def get(self, key, **kwargs):
        if not hasattr(self, "_dotenv_file"):
            raise Exception("It seems like you didn't loaded the your dotenv file yet.")

        value = self._data.get(key)
        if value is None:
            raise KeyError(
                f"The config '{key}' is not set on {self._dotenv_file}. Check "
                "for any misconfiguration or misspelling of the variable name."
            )

        return value

    def load_file(self, filepath):
        self._dotenv_file = filepath
        self._data = {}
        with open(self._dotenv_file) as file:
            for line in file.readlines():
                # ignore comments, section title or invalid lines
                if line.startswith(("#", ";", "[")) or "=" not in line:
                    continue

                # split on the first =, allows for subsequent `=` in strings
                key, value = line.split("=", 1)
                key = key.strip()

                if not (key and value):
                    continue

                self._data[key] = value.rstrip("\r\n")


class RootDirectoryNotFound(FileNotFoundError):
    pass
