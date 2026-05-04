"""Tests for `gconfigs` package.
- There are some asserts that may seem obvious, that's just because they
act like a restriction to things I think, at the moment, that we may have to
talk before changing the way it's implemented.
"""

import json

import pytest

import gconfigs as gconfigs
from gconfigs.gconfigs import GConfigs, ValueOutput

from . import DummyBackend


def test_bad_instatiation():
    class MissingGet:
        pass

    class MissingKeys:
        pass

    with pytest.raises(AttributeError):
        GConfigs(backend=MissingGet)
    with pytest.raises(AttributeError):
        GConfigs(backend=MissingKeys)

    with pytest.raises(TypeError, match=r".*required positional argument: 'backend'.*"):
        GConfigs()


def test_defaults():
    # api main endpoints
    gconfigs.envs
    gconfigs.dotenvs
    gconfigs.ini_file
    gconfigs.toml_file
    gconfigs.local_files
    gconfigs.local_file
    # basic expected
    configs = GConfigs(backend=DummyBackend)
    configs.object_type_name
    configs.get
    configs.__call__
    configs.backend
    configs.output_fmt
    # iterator
    configs.iterator
    configs.__next__
    configs.__iter__
    # utilities
    configs.json
    configs.__contains__
    configs.__len__
    configs.__repr__

    assert configs.object_type_name == "KeyValue", (
        "'object_type_name' default value should be 'KeyValue'"
    )


def test_object_type_name():
    configs = GConfigs(backend=DummyBackend, object_type_name="DummyConfig")
    assert configs.object_type_name == "DummyConfig"
    configs.object_type_name = "DummyConfigChanged"
    assert configs.object_type_name == "DummyConfigChanged"


def test_get_configs_info():
    configs = GConfigs(backend=DummyBackend)
    # if given key is in configs (backend.keys())
    assert "CONFIG-1" in configs
    assert "NON-EXISTENT-CONFIG" not in configs
    assert len(configs) == len(configs.backend.data)
    assert configs("CONFIG-1") == "config-1"

    # Non existent config
    with pytest.raises(KeyError):
        configs("NON-EXISTENT-CONFIG")

    # Non existent config - return default instead
    assert configs("NON-EXISTENT-CONFIG", default="default") == "default"
    # default argument can be anything
    # achieved by using the `gconfigs.gconfigs.NOTSET`
    assert configs("NON-EXISTENT-CONFIG", default=None) is None
    assert configs("NON-EXISTENT-CONFIG", default=True) is True
    assert configs("NON-EXISTENT-CONFIG", default=False) is False


def test_get_is_keyword_only_for_default_and_options():
    """Check if `get` method is properly enforcing the keyword only arguments
    after the `key` argument."""
    configs = GConfigs(backend=DummyBackend)

    with pytest.raises(TypeError):
        configs.get("NON-EXISTENT-CONFIG", "default")


def test_get_formats_default_value_when_key_is_missing():
    configs = GConfigs(backend=DummyBackend)

    value = configs.get("NON-EXISTENT-CONFIG", default=" 1 ", cast=int, strip=True)

    assert value == 1


def test_get_propagates_format_options_to_use_instead_fallback():
    class FallbackBackend:
        def keys(self):
            return ["ALT"]

        def get(self, key, **kwargs):
            if key == "ALT":
                return " 1 "
            raise KeyError(f"'{key}' not set")

    configs = GConfigs(backend=FallbackBackend)

    value = configs.get("PRIMARY", use_instead="ALT", cast=int, strip=True)

    assert value == 1


def test_get_propagates_backend_kwargs_to_use_instead_fallback():
    class BackendWithFallbackKwargs:
        def __init__(self):
            self.calls = []

        def keys(self):
            return ["SECONDARY"]

        def get(self, key, **kwargs):
            self.calls.append((key, kwargs))
            if key == "SECONDARY":
                return "ok"
            raise KeyError(f"'{key}' not set")

    backend = BackendWithFallbackKwargs()
    configs = GConfigs(backend=backend)

    value = configs.get("PRIMARY", use_instead="SECONDARY", profile="staging")

    assert value == "ok"
    assert backend.calls == [
        ("PRIMARY", {"profile": "staging"}),
        ("SECONDARY", {"profile": "staging"}),
    ]


def test_get_does_not_use_default_or_use_instead_on_success_path():
    class TrackingBackend:
        def __init__(self):
            self.calls = []

        def keys(self):
            return ["CONFIG-1", "FALLBACK"]

        def get(self, key, **kwargs):
            self.calls.append(key)
            if key == "CONFIG-1":
                return "config-1"
            if key == "FALLBACK":
                return "fallback"
            raise KeyError(f"'{key}' not set")

    backend = TrackingBackend()
    configs = GConfigs(backend=backend)

    value = configs.get("CONFIG-1", default="default", use_instead="FALLBACK")

    assert value == "config-1"
    assert backend.calls == ["CONFIG-1"]


def test_get_configs_use_instead():
    configs = GConfigs(backend=DummyBackend)

    # First key doesn't exist, use key/config "CONFIG-1" instead
    assert configs("NON-EXISTENT-CONFIG", use_instead="CONFIG-1") == "config-1"
    # neither key nor use_instead exist, so use the default
    assert (
        configs(
            "NON-EXISTENT-CONFIG", use_instead="NON-EXISTENT-CONFIG-2", default="abc"
        )
        == "abc"
    )

    # if we don't have a default value; and key and use_instead doesn't exist;
    # we get a KeyError about the use_instead key not found.
    with pytest.raises(KeyError, match=r".*'NON-EXISTENT-CONFIG-2' not set.*"):
        assert configs("NON-EXISTENT-CONFIG", use_instead="NON-EXISTENT-CONFIG-2")


def test_get_use_instead_attempts_only_once_then_raises_fallback_error():
    class FailingBackend:
        def __init__(self):
            self.calls = []

        def keys(self):
            return []

        def get(self, key, **kwargs):
            self.calls.append(key)
            raise KeyError(f"'{key}' not set")

    backend = FailingBackend()
    configs = GConfigs(backend=backend)

    with pytest.raises(KeyError, match=r".*'SECONDARY' not set.*"):
        configs.get("PRIMARY", use_instead="SECONDARY")

    assert backend.calls == ["PRIMARY", "SECONDARY"]


def test_get_forwards_backend_kwargs():
    class BackendWithKwargs:
        def __init__(self):
            self.seen = []

        def keys(self):
            return ["CONFIG-1"]

        def get(self, key, **kwargs):
            self.seen.append((key, kwargs))
            return "config-1"

    backend = BackendWithKwargs()
    configs = GConfigs(backend=backend)

    value = configs.get("CONFIG-1", profile="dev", region="sa-east-1")

    assert value == "config-1"
    assert backend.seen == [("CONFIG-1", {"profile": "dev", "region": "sa-east-1"})]


def test_get_calls_output_formatter_with_expected_arguments():
    """Check if `get` method is properly calling the `output_fmt.format_value`
    method with the expected arguments."""

    class SpyOutputFmt:
        def __init__(self):
            self.calls = []

        def format_value(self, value, strip, cast, list_sep, bool_values):
            self.calls.append((value, strip, cast, list_sep, bool_values))
            return "formatted-value"

    spy = SpyOutputFmt()
    configs = GConfigs(backend=DummyBackend, output_fmt=spy)
    bool_values = (("enabled", "disabled"),)

    value = configs.get(
        "CONFIG-1",
        strip=False,
        cast=str,
        list_sep=";",
        bool_values=bool_values,
    )

    assert value == "formatted-value"
    assert spy.calls == [("config-1", False, str, ";", bool_values)]


def test_get_propagates_formatter_errors():
    class ExplodingOutputFmt:
        def format_value(self, value, strip, cast, list_sep, bool_values):
            raise RuntimeError("format failed")

    configs = GConfigs(backend=DummyBackend, output_fmt=ExplodingOutputFmt())

    with pytest.raises(RuntimeError, match=r".*format failed.*"):
        configs.get("CONFIG-1")


def test_access_backend_class_from_gconfigs():
    class DummyBackendExample(DummyBackend):
        def example_method(self, example):
            pass

    configs = GConfigs(backend=DummyBackendExample)
    assert configs.backend.example_method


def test_iterator():
    configs = GConfigs(backend=DummyBackend)
    for config in configs:
        # Make sure the object is a namedtuple
        assert issubclass(config.__class__, tuple) and config._fields, (
            "Looks like the iterator is not returning a namedtuple anymore."
        )
        assert config
        assert config.key
        # guarantee the namedtuple is being properly created
        assert configs(config.key) == config.value, (
            "Looks like the namedtuple is not being properly created."
        )

    # after an iterate in forloops it should have nothing left for next()
    with pytest.raises(StopIteration):
        next(configs)

    # but it's possible to iterator as many as you can with `self.iterator()`
    iter_configs = configs.iterator()
    for config in iter_configs:
        assert config

    # iterating multiple times should always start from the first item again
    first_pass_keys = [config.key for config in configs]
    second_pass_keys = [config.key for config in configs]
    assert first_pass_keys == second_pass_keys
    assert first_pass_keys


def test_json():
    configs = GConfigs(backend=DummyBackend)
    json_ = configs.json()
    assert json_
    # let's turn the json_ into a dict so we can see if it preserved all the configs
    configs_data = json.loads(json_)
    assert all(key in configs.backend.data for key in configs_data)

    assert next(configs), (
        "If `configs` is not iterable after `configs.json()` it's because it's not using the iterator properly."
    )


# gconfigs.ValueOutput tests
# CASTING TYPES TESTS


def test_get_typed_configs():
    """Check if `ValueOutput` is properly preserving types and values."""
    out_fmt = ValueOutput()
    assert out_fmt.format_value("config-1") == "config-1"
    assert out_fmt.format_value(None) is None
    assert out_fmt.format_value(True) is True
    assert out_fmt.format_value(False) is False
    assert out_fmt.format_value(1) == 1
    assert out_fmt.format_value(1.1) == 1.1
    assert out_fmt.format_value([1, 1.1, "a"]) == [1, 1.1, "a"]
    assert out_fmt.format_value((1, 1.1, "a")) == (1, 1.1, "a")
    assert out_fmt.format_value({1, 1.1, "a"}) == {1, 1.1, "a"}
    assert out_fmt.format_value({"a": 1, "b": "b"}) == {"a": 1, "b": "b"}


def test_cast_boolean_based_on_BOOLEAN_VALUES():
    """Considering the default `BOOL_VALUES` in `ValueOutput`, check if the boolean values are properly casted.

    `gconfigs.BOOL_VALUES` is a tuple of tuples, where each inner tuple has the true and false values for that type.
    BOOL_VALUES = (
        ("true", "false"),
        ("1", "0"),
        ("yes", "no"),
        ("y", "n"),
        ("on", "off"),
    )
    """
    out_fmt = ValueOutput()

    assert out_fmt.format_value(True, cast=bool) is True
    assert out_fmt.format_value(False, cast=bool) is False
    assert out_fmt.format_value("true", cast=bool) is True
    assert out_fmt.format_value("false", cast=bool) is False
    # almost unecessary to test all the values, but let's do it anyway to guarantee the defaults:
    assert out_fmt.format_value("1", cast=bool) is True
    assert out_fmt.format_value("0", cast=bool) is False
    assert out_fmt.format_value("yes", cast=bool) is True
    assert out_fmt.format_value("no", cast=bool) is False
    assert out_fmt.format_value("y", cast=bool) is True
    assert out_fmt.format_value("n", cast=bool) is False
    assert out_fmt.format_value("on", cast=bool) is True
    assert out_fmt.format_value("off", cast=bool) is False

    with pytest.raises(ValueError, match=r".*Could not cast the value.*"):
        out_fmt.format_value("invalid", cast=bool)


def test_cast_list_builtin_types():
    out_fmt = ValueOutput()
    assert out_fmt.format_value([1, 1.1, "a"], cast=list) == [1, 1.1, "a"]
    assert out_fmt.format_value((1, 1.1, "a"), cast=list) == [1, 1.1, "a"]
    _list = out_fmt.format_value({1, 1.1, "a"}, cast=list)
    # sets don't preserve order, so we need to check if all the values are in the list, instead of checking for equality
    assert all(value in _list for value in (1, 1.1, "a"))


def test_cast_list_list_separator():
    out_fmt = ValueOutput()
    assert out_fmt.format_value("1,1.1,a", cast=list) == ["1", "1.1", "a"]
    assert out_fmt.format_value("1;1.1;a", cast=list, list_sep=";") == ["1", "1.1", "a"]
    # if the value is not a string, it should just return the value as is, even if we pass a list_sep
    assert out_fmt.format_value([1, 1.1, "a"], cast=list, list_sep=";") == [1, 1.1, "a"]


def test_cast_list_invalid_string_without_separator_or_json_style():
    out_fmt = ValueOutput()
    with pytest.raises(ValueError, match=r".*Could not cast the value.*"):
        out_fmt.format_value("abc", cast=list)


def test_cast_list_value_json_style():
    """These tests won't be extensive, because we would just be testing the `json.loads` behavior."""
    out_fmt = ValueOutput()
    assert out_fmt.format_value('[1, 1.1, "a", null]', cast=list) == [1, 1.1, "a", None]

    # Common mistake: single quotes instead of double quotes in JSON style list
    with pytest.raises(ValueError, match=r".*Expecting value:*"):
        assert out_fmt.format_value("[1, 1.1, 'a']", cast=list)


def test_cat_tuple_builtin_types():
    out_fmt = ValueOutput()
    assert out_fmt.format_value((1, 1.1, "a"), cast=tuple) == (1, 1.1, "a")
    assert out_fmt.format_value([1, 1.1, "a"], cast=tuple) == (1, 1.1, "a")
    _tuple = out_fmt.format_value({1, 1.1, "a"}, cast=tuple)
    # sets don't preserve order, so we need to check if all the values are in the tuple, instead of checking for equality
    assert all(value in _tuple for value in (1, 1.1, "a"))


def test_cast_tuple_list_separator():
    out_fmt = ValueOutput()
    assert out_fmt.format_value("1,1.1,a", cast=tuple) == ("1", "1.1", "a")
    assert out_fmt.format_value("1;1.1;a", cast=tuple, list_sep=";") == (
        "1",
        "1.1",
        "a",
    )
    # if the value is not a string, it should just return the value as is, even if we pass a list_sep
    assert out_fmt.format_value((1, 1.1, "a"), cast=tuple, list_sep=";") == (
        1,
        1.1,
        "a",
    )


def test_cast_tuple_invalid_string_without_separator_or_json_style():
    out_fmt = ValueOutput()
    with pytest.raises(ValueError, match=r".*Could not cast the value.*"):
        out_fmt.format_value("abc", cast=tuple)


def test_cast_tuple_value_json_style():
    """These tests won't be extensive, because we would just be testing the `json.loads` behavior.

    * There are no tuples in JSON, so we will just be testing if it can cast a JSON style list into a tuple.
    """
    out_fmt = ValueOutput()
    assert out_fmt.format_value('[1, 1.1, "a", null]', cast=tuple) == (
        1,
        1.1,
        "a",
        None,
    )

    # Common mistake: single quotes instead of double quotes in JSON style list
    with pytest.raises(ValueError, match=r".*Expecting value:*"):
        assert out_fmt.format_value("[1, 1.1, 'a']", cast=tuple)


def test_cast_set_builtin_types():
    out_fmt = ValueOutput()
    assert out_fmt.format_value({1, 1.1, "a"}, cast=set) == {1, 1.1, "a"}
    assert out_fmt.format_value((1, 1.1, "a"), cast=set) == {1, 1.1, "a"}
    assert out_fmt.format_value([1, 1.1, "a"], cast=set) == {1, 1.1, "a"}


def test_cast_set_list_separator():
    out_fmt = ValueOutput()
    assert out_fmt.format_value("1,1.1,a", cast=set) == {"1", "1.1", "a"}
    assert out_fmt.format_value("1;1.1;a", cast=set, list_sep=";") == {"1", "1.1", "a"}
    # if the value is not a string, it should just return the value as is, even if we pass a list_sep
    assert out_fmt.format_value({1, 1.1, "a"}, cast=set, list_sep=";") == {1, 1.1, "a"}


def test_cast_set_invalid_string_without_separator_or_json_style():
    out_fmt = ValueOutput()
    with pytest.raises(ValueError, match=r".*Could not cast the value.*"):
        out_fmt.format_value("abc", cast=set)


def test_cast_set_value_json_style():
    """These tests won't be extensive, because we would just be testing the `json.loads` behavior."""
    out_fmt = ValueOutput()
    assert out_fmt.format_value('[1, 1.1, "a", null]', cast=set) == {1, 1.1, "a", None}

    # Common mistake: single quotes instead of double quotes in JSON style list
    with pytest.raises(ValueError, match=r".*Expecting value:*"):
        assert out_fmt.format_value("[1, 1.1, 'a']", cast=set)


def test_cast_dict_value():
    out_fmt = ValueOutput()
    assert out_fmt.format_value({"a": 1, "b": "b"}, cast=dict) == {"a": 1, "b": "b"}
    assert out_fmt.format_value('{"a": 1, "none": null}', cast=dict) == {
        "a": 1,
        "none": None,
    }
    with pytest.raises(ValueError, match=r".*Could not cast the value.*"):
        out_fmt.format_value("invalid", cast=dict)


def test_custom_cast_function():
    out_fmt = ValueOutput()

    def custom_cast(value):
        if value == "custom":
            return "casted"
        raise ValueError("Invalid value for custom cast")

    assert out_fmt.format_value("custom", cast=custom_cast) == "casted"
    with pytest.raises(ValueError, match=r".*Invalid value for custom cast.*"):
        out_fmt.format_value("invalid", cast=custom_cast)


def test_custom_cast_decimal():
    out_fmt = ValueOutput()

    from decimal import Decimal

    assert out_fmt.format_value("1.1", cast=Decimal) == Decimal("1.1")
    with pytest.raises(ValueError, match=r".*Could not cast the value.*"):
        out_fmt.format_value("invalid", cast=Decimal)


# STRIP TESTS
def test_strip_value_by_default():
    out_fmt = ValueOutput()
    assert out_fmt.strip is True

    # strip default: True
    assert out_fmt.format_value(" value ") == "value", (
        "Returning value should be stripped by default."
    )
    assert out_fmt.format_value("  ") == "", (
        "Returning value should be stripped by default, even if it's only blank spaces."
    )

    # override default
    assert out_fmt.format_value(" value ", strip=False) == " value ", (
        "Returning value should ALLOW blank spaces."
    )
    assert out_fmt.format_value("  ", strip=False) == "  ", (
        "Returning value should ALLOW blank spaces."
    )

    # after override default it should still be True
    assert out_fmt.strip is True, (
        "Default `strip` behavior should be True. Check if `ValueOutput` is being properly used."
    )


def test_do_not_strip_by_default():
    # no strip
    out_fmt = ValueOutput(strip=False)
    assert out_fmt.strip is False

    # strip default: False
    assert out_fmt.format_value(" value ") == " value ", (
        "Returning value should ALLOW blank spaces."
    )
    assert out_fmt.format_value("  ") == "  ", (
        "Returning value should ALLOW blank spaces."
    )
