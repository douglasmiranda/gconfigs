"""
Backends for gConfigs

Backends are just simple classes with at least two methods implemented:
`get` and `keys`.

Example:
    ```python
    class XYZBackend:
        def keys(self):
            # return a iterable of all keys available
            return available_keys

        def get(self, key: str):
            # this method receive a key (identifier of a config)
            # and return its respective value
            return value
    ```
Notes:
    - If it's not possible to provide a `.keys` method, just declare with
    an empty tuple for example, but the `.get` method is mandatory.
    - For errors on `.get` method just throw exceptions.
    (Config doesn't exists, you don't have permission, stuff like that)
    See `GConfigs.get` and you'll see that it has a `default` parameter,
    and of course if you provide a default value it will not throw a exception.
"""

import os
from pathlib import Path


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


class LocalFiles:
    def __init__(self, path="/", pattern="*"):
        self.pattern = pattern
        self.path = path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"The path {path} doesn't exist.")
        if not path.is_dir():
            raise NotADirectoryError(f"The path {path} is not a directory.")

        self._path = path

    def keys(self):
        for item in self.path.glob(self.pattern):
            if item.is_file():
                yield item.name

    def get(self, key, **kwargs):
        file = self.path / key
        if file.exists():
            return file.read_text()

        raise FileNotFoundError(
            f"Check if your files are mounted on {self.path}. "
            "And remember to check if your system is case sensitive."
        )


class DotEnv:
    def __init__(self, filepath=".env"):
        self._dotenv_file = None
        self._data = {}
        self.load_file(filepath)

    def keys(self):
        return self._data.keys()

    def get(self, key, **kwargs):
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


class File:
    def keys(self):
        return tuple()

    def get(self, key, **kwargs):
        filepath = Path(key)
        if not filepath.exists():
            raise FileNotFoundError(
                f"The file {filepath} doesn't exist. Check if the file is mounted correctly."
            )

        if not os.access(filepath, os.R_OK):
            raise PermissionError(
                f"The file {filepath} is not readable. Check the file permissions."
            )

        return filepath.read_text()
