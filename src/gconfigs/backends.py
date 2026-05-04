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

import configparser
import os
from fnmatch import fnmatch
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
        for item in self.path.iterdir():
            if item.is_file() and fnmatch(item.name, self.pattern):
                yield item.name

    def get(self, key, **kwargs):
        if Path(key).name != key:
            raise FileNotFoundError(
                f"The key '{key}' is not valid for LocalFiles. "
                "Only files directly inside the configured path are supported."
            )

        base_path = self.path.resolve()
        file = (base_path / key).resolve()

        try:
            file.relative_to(base_path)
        except ValueError as e:
            raise PermissionError(
                f"The key '{key}' resolves outside the allowed path {self.path}."
            ) from e

        if not file.exists() or not file.is_file():
            raise FileNotFoundError(
                f"Check if your files are mounted on {self.path}. "
                "And remember to check if your system is case sensitive."
            )

        if not os.access(file, os.R_OK):
            raise PermissionError(
                f"The file {file} is not readable. Check the file permissions."
            )

        return file.read_text()


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
            for _line in file.readlines():
                line = _line.lstrip()

                # ignore comments, section title or invalid lines
                if line.startswith(("#", ";", "[")) or "=" not in line:
                    continue

                # split on the first =, allows for subsequent `=` in strings
                key, value = line.split("=", 1)
                key = key.strip()

                if not key:
                    continue

                self._data[key] = value.rstrip("\r\n")


class INIFile:
    def __init__(self, filepath=".ini"):
        self._ini_file = None
        self._data = configparser.ConfigParser()
        self.load_file(filepath)

    def keys(self):
        for section in self._data.sections():
            for option in self._data[section]:
                yield f"{section}.{option}"

    def get(self, key, **kwargs):
        if "." not in key:
            raise KeyError(
                f"INIFile keys must use 'section.option' format. Received '{key}'."
            )

        section, option = key.split(".", 1)
        if not self._data.has_section(section) or not self._data.has_option(
            section, option
        ):
            raise KeyError(
                f"The config '{key}' is not set on {self._ini_file}. Check "
                "for any misconfiguration or misspelling of the variable name."
            )

        return self._data.get(section, option)

    def load_file(self, filepath):
        self._ini_file = filepath
        self._data = configparser.ConfigParser()
        loaded_files = self._data.read(self._ini_file)
        if not loaded_files:
            raise FileNotFoundError(f"The file {self._ini_file} doesn't exist.")


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
