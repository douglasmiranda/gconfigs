# -*- coding: utf-8 -*-
from collections import namedtuple
from functools import lru_cache
import json


class NoValue:
    def __repr__(self):  # pragma: no cover
        return f"<{self.__class__.__name__}>"


NOTSET = NoValue()


class GConfigs:
    def __init__(self, backend, strip=True, object_type_name="KeyValue"):
        """
        :param backend: Backend / parser of configs. A simple class implementing `get` and `keys` methods. `gconfigs.backends` for more information.
        :param strip: Control the stripping of return value of `self.get` method.
        :param object_type_name: Simply a nice name for our key value named tuple.
        """
        if hasattr(backend, "get") or hasattr(backend, "keys"):
            self._backend = backend() if callable(backend) else backend
        else:
            raise AttributeError(
                "'backend' class must have at least the methods 'get' and 'keys'."
            )

        self.strip = strip
        self.object_type_name = object_type_name

        if hasattr(self._backend, "load_file") and callable(self._backend.load_file):
            self.load_file = self._load_file

        self._iter_configs = self.iterator()

    def get(self, key, default=NOTSET, use_instead=NOTSET, strip=None, **kwargs):
        """Return value for given key.
        :param var: Key (Name) of config.
        :param default: If backend doesn't return valid config, return this instead.
        :param use_instead: If `key` doesn't exist use the alternative key `use_instead`.
        :param strip: Control the stripping of return value. Override the default `self.strip` with `True` or `False`. Will strip if is a string value.

        :returns: Parsed value or default. Or raises exceptions you implement in your backend.
        """

        try:
            value = self._backend.get(key)
        # This may seem a generic try/except but I'm actually catching the
        # specific Exception that you will implement in your backend.
        except Exception as e:
            if use_instead is not NOTSET:
                return self.get(use_instead, default, NOTSET, strip, **kwargs)

            if default is NOTSET:
                raise e

            value = default

        strip_ = self.strip if strip is None else strip
        if strip_ and isinstance(value, str):
            return value.strip()

        return value

    def as_bool(self, key, **kwargs):
        value = self.get(key, **kwargs)
        if isinstance(value, bool):
            return value

        if isinstance(value, str) and value.lower() in ("true", "false"):
            return self._cast(value.lower())

        raise ValueError(f"Could not cast the value '{value}' to boolean.")

    def as_list(self, key, **kwargs):
        value = self.get(key, **kwargs)
        if isinstance(value, list) or isinstance(value, tuple):
            return list(value)

        if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            return self._cast(value)

        raise ValueError(f"Could not cast the value '{value}' to list.")

    def as_dict(self, key, **kwargs):
        value = self.get(key, **kwargs)
        if isinstance(value, dict):
            return value

        if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
            return self._cast(value)

        raise ValueError(f"Could not cast the value '{value}' to dict.")

    def _cast(self, value):
        try:
            return json.loads(value)

        except json.decoder.JSONDecodeError as e:
            raise ValueError(
                f"Could not cast the value {value}. Tried to cast with json module, so it must be a valid json value."
            )

    def json(self):
        """Returns json parsed data of all available data.
        """
        return json.dumps({item.key: item.value for item in self.iterator()})

    def _load_file(self, filepath):
        self._backend.load_file(filepath)

    @property
    @lru_cache()
    def _cached_namedtuple(self):
        return namedtuple(self.object_type_name, ["key", "value"])

    def iterator(self):
        for key in self._backend.keys():
            yield self._cached_namedtuple(key, self.get(key))

    def __next__(self):
        return next(self._iter_configs)

    def __iter__(self):
        return self

    def __call__(self, key, **kwargs):
        return self.get(key, **kwargs)

    def __contains__(self, key):
        return key in self._backend.keys()

    def __len__(self):
        return len(self._backend.keys())

    def __repr__(self):  # pragma: no cover
        return f"<GConfigs backend={self._backend.__class__.__name__}>"
