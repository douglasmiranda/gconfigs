from gconfigs.gconfigs import NOTSET


class DummyBackend:
    """DummyBackend for testing GConfigs
    I'm implementing a immutable dict to store configs.
    This is because I don't want `GConfigs` to ever change values into the
    backend, all the trimming or whatever must be done in `GConfigs` class.

    So if at some point we implement something that changes data in any backend,
    it will fail.
    """

    def __init__(self):
        # ref: https://www.python.org/dev/peps/pep-0351/

        class ImmutableDict(dict):

            def __hash__(self):
                return id(self)

            def _immutable(self, *args, **kws):
                raise TypeError("object is immutable")

            __setitem__ = _immutable
            __delitem__ = _immutable
            clear = _immutable
            update = _immutable
            setdefault = _immutable
            pop = _immutable
            popitem = _immutable

        self.data = ImmutableDict(
            {
                "CONFIG-1": "config-1",
                " white space key ": " white space value ",
                "empty-value": "",
                "space-only-value": "  ",
                "CONFIG-NONE": None,
                "CONFIG-TRUE": True,
                "CONFIG-FALSE": False,
                "CONFIG-INT": 1,
                "CONFIG-FLOAT": 1.1,
                "CONFIG-LIST": [1, 1.1, "a"],
                "CONFIG-TUPLE": (1, 1.1, "a"),
                "CONFIG-DICT": {"a": 1, "b": "b"},
                "CONFIG-TRUE-STRING": "True",
                "CONFIG-FALSE-STRING": "False",
                "CONFIG-LIST-STRING-JSON-STYLE": '[1, 1.1, "a"]',
                "CONFIG-LIST-STRING-JSON-STYLE-BROKEN": '[1, 1.1, "a]',
                "CONFIG-DICT-JSON-STYLE": '{"a": 1, "b": "b"}',
            }
        )

    def keys(self):
        """
        :returns: from iterable `self.data` (an immutable dict) return its keys.
        """
        return self.data

    def get(self, key, **kwargs):
        """ Return value given a key
        :returns: value or KeyError
        """
        value = self.data.get(key, NOTSET)
        if value is NOTSET:
            raise KeyError(
                f"Dummy Data '{key}' not set. Check for any "
                "misconfiguration or misspelling of the variable name."
            )

        return value
