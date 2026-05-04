import json
from collections import namedtuple


class NoValue:
    def __repr__(self):  # pragma: no cover
        return f"<{self.__class__.__name__}>"


NOTSET = NoValue()


class GConfigs:
    def __init__(self, backend, output_fmt=None, object_type_name="KeyValue"):
        """
        Args:
            backend: Backend / parser of configs. A simple class implementing `get` and `keys` methods.
                `gconfigs.backends` for more information.
            object_type_name (str): Simply a nice name for our key value named tuple.
            output_fmt (class): An instance of
        """
        if not (hasattr(backend, "get") and hasattr(backend, "keys")):
            raise AttributeError(
                "'backend' class must have at least the methods 'get' and 'keys'."
            )

        self.backend = backend() if callable(backend) else backend
        if output_fmt is None:
            output_fmt = ValueOutput()
        self.output_fmt = output_fmt
        self.object_type_name = object_type_name
        self._iter_configs = self.iterator()

    def get(
        self,
        key,
        *,
        default=NOTSET,
        use_instead=NOTSET,
        strip=None,
        cast=None,
        list_sep=None,
        bool_values=None,
        **backend_kwargs,
    ):
        """Return value for given key.
        Args:
            key (str): Key (Name) of config.
            default (NOTSET|str): If backend doesn't return valid config, return this instead.
            use_instead (str): If `key` doesn't exist use the alternative key `use_instead`.
            strip (bool): Control the stripping of return value. Override the default
                `ValueOutput.strip` behavior with `True` or `False`. Will strip if is a string value.
            cast (type): If provided, will try to cast the value to the given type.
                For example, `int`, `float`, `bool` and so on.
            list_sep (str): Separator for list values when casting from string. Override the default `ValueOutput.list_sep`.
            bool_values (tuple): Tuple of tuples with true and false values for boolean casting.
                Override the default `ValueOutput.bool_values`. For example, (("true", "false"),) means that if the value
                is "true" (case insensitive) it will be casted to True.

        Returns:
            Parsed value or default. Or raises exceptions you implement in your backend.
        """

        try:
            value = self.backend.get(key, **backend_kwargs)
        # This may seem a generic try/except but I'm actually catching the
        # specific Exception that you will implement in your backend.
        except Exception as e:
            if use_instead is not NOTSET:
                return self.get(
                    use_instead,
                    default=default,
                    use_instead=NOTSET,
                    strip=strip,
                    cast=cast,
                    list_sep=list_sep,
                    bool_values=bool_values,
                    **backend_kwargs,
                )

            if default is NOTSET:
                raise e

            value = default

        value = self.output_fmt.format_value(value, strip, cast, list_sep, bool_values)

        return value

    def json(self):
        """Returns json parsed data of all available data."""

        def set_default(obj):
            if isinstance(obj, set):
                return list(obj)
            raise TypeError

        return json.dumps(
            {item.key: item.value for item in self.iterator()}, default=set_default
        )

    def iterator(self):
        kv = namedtuple(self.object_type_name, ["key", "value"])
        for key in self.backend.keys():
            yield kv(key=key, value=self.get(key))

    def __call__(self, key, **kwargs):
        return self.get(key, **kwargs)

    def __next__(self):
        return next(self._iter_configs)

    def __iter__(self):
        self._iter_configs = self.iterator()
        return self

    def __contains__(self, key):
        return key in self.backend.keys()

    def __len__(self):
        return len(self.backend.keys())

    def __repr__(self):  # pragma: no cover
        return f"<GConfigs backend={self.backend.__class__.__name__}>"


BOOL_VALUES = (
    ("true", "false"),
    ("1", "0"),
    ("yes", "no"),
    ("y", "n"),
    ("on", "off"),
)


class ValueOutput:
    def __init__(self, strip=True, list_sep=",", bool_values=BOOL_VALUES):
        """This class is responsible for formatting the output of the configs.
        It is used in `GConfigs` to format the output of the configs.

        Args:
            strip (bool): Control the stripping of return value. Will strip if is a string value.
            list_sep (str): Separator for list values when casting from string.
            bool_values (tuple): Tuple of tuples with true and false values for boolean casting.

        About `BOOL_VALUES`:
        This is a tuple of tuples, where each inner tuple has the true and false values for that type.
        For example, ("true", "false") means that if the value is "true" (case insensitive) it will be casted to True,
        and if it's "false" it will be casted to False.

        The built-in types `True` and `False` do not need to be in `BOOL_VALUES` because they are already
        recognized as boolean values.
        """
        self.strip = strip
        self.list_sep = list_sep
        self.bool_values = bool_values

    def format_value(
        self, value, strip=None, cast=None, list_sep=None, bool_values=None
    ):
        strip = self.strip if strip is None else strip
        list_sep = self.list_sep if list_sep is None else list_sep
        bool_values = self.bool_values if bool_values is None else bool_values

        if cast is not None:
            value = self._try_cast(value, cast, list_sep, bool_values)

        if strip and isinstance(value, str):
            return value.strip()

        return value

    def _try_cast(self, value, cast, list_sep, bool_values):
        try:
            # some backends may return the value in the correct type already
            if isinstance(value, cast):
                return value
        except TypeError:
            # custom functions for casting may raise TypeError
            # so we continue to try to cast the value below
            pass

        if cast is bool:
            return self._cast_bool(value, bool_values=bool_values)
        if cast is list:
            return self._cast_list(value, list_sep=list_sep)
        if cast is tuple:
            return self._cast_tuple(value, list_sep=list_sep)
        if cast is set:
            return self._cast_set(value, list_sep=list_sep)
        if cast is dict:
            return self._cast_dict(value)

        try:
            return cast(value)
        except Exception as e:
            raise ValueError(
                f"Could not cast the value '{value}' to {cast}. Error: {e}"
            ) from e

    def _cast_bool(self, value, bool_values):
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            val = value.lower()
            for true_val, false_val in bool_values:
                if val == str(true_val).lower():
                    return True
                if val == str(false_val).lower():
                    return False

        raise ValueError(f"Could not cast the value '{value}' to boolean.")

    def _cast_list(self, value, list_sep):
        if isinstance(value, (tuple, set)):
            return list(value)

        if not isinstance(value, str):
            raise ValueError(f"Could not cast the value '{value}' to list.")

        if value.startswith("[") and value.endswith("]"):
            return json.loads(value)

        if list_sep in value:
            return [item.strip() for item in value.split(list_sep)]

        raise ValueError(f"Could not cast the value '{value}' to list.")

    def _cast_tuple(self, value, list_sep):
        if isinstance(value, (list, set)):
            return tuple(value)

        if not isinstance(value, str):
            raise ValueError(f"Could not cast the value '{value}' to tuple.")

        if value.startswith("[") and value.endswith("]"):
            return tuple(json.loads(value))

        if list_sep in value:
            return tuple(item.strip() for item in value.split(list_sep))

        raise ValueError(f"Could not cast the value '{value}' to tuple.")

    def _cast_set(self, value, list_sep):
        if isinstance(value, (list, tuple)):
            return set(value)

        if not isinstance(value, str):
            raise ValueError(f"Could not cast the value '{value}' to set.")

        if value.startswith("[") and value.endswith("]"):
            return set(json.loads(value))

        if list_sep in value:
            return set(item.strip() for item in value.split(list_sep))

        raise ValueError(f"Could not cast the value '{value}' to set.")

    def _cast_dict(self, value):
        if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
            return json.loads(value)

        raise ValueError(f"Could not cast the value '{value}' to dict.")
