"""Tests for `gconfigs` package.
- There are some asserts that may seem obvious, that's just because they
act like a restriction to things I think, at the moment, that we may have to
talk before changing the way it's implemented.
"""

from gconfigs import GConfigs
from . import DummyBackend
import gconfigs

import pytest

import json


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


def test_basics():
    # main endpoints
    gconfigs.envs
    gconfigs.dotenvs
    gconfigs.configs
    gconfigs.secrets
    # basic expected
    configs_ = GConfigs(backend=DummyBackend)
    configs_.strip
    configs_.object_type_name
    configs_.get
    configs_.__call__
    # iterator
    configs_.iterator
    configs_.__next__
    configs_.__iter__
    # fancy xD
    configs_.json
    configs_.__contains__
    configs_.__len__
    configs_.__repr__

    assert configs_.object_type_name == "KeyValue", "'object_type_name' default value should be 'KeyValue'"
    assert configs_.strip, "'strip' default value should be boolean 'True'"

    configs = GConfigs(backend=DummyBackend, object_type_name="DummyConfig")
    assert configs.object_type_name == "DummyConfig"
    configs.object_type_name = "DummyConfigChanged"
    assert configs.object_type_name == "DummyConfigChanged"


def test_get_configs_info():
    configs = GConfigs(backend=DummyBackend)
    # if given key is in configs (backend.keys())
    assert "CONFIG-1" in configs
    assert "NON-EXISTENT-CONFIG" not in configs
    assert len(configs) == len(configs._backend.data)
    assert configs("CONFIG-1") == "config-1"

    # Non existent config
    with pytest.raises(KeyError):
        configs("NON-EXISTENT-CONFIG")

    # Non existent config - return default instead
    assert configs("NON-EXISTENT-CONFIG", default="default") == "default"
    # default argument can be anything
    # achieved by using the `gconfigs.gconfigs.NOTSET` trick
    assert configs("NON-EXISTENT-CONFIG", default=None) is None
    assert configs("NON-EXISTENT-CONFIG", default=True) is True
    assert configs("NON-EXISTENT-CONFIG", default=False) is False


def test_get_configs_strip_value_or_not():
    configs = GConfigs(backend=DummyBackend)
    assert configs.strip
    # strip default: True
    assert configs(" white space key ") == "white space value" and configs(
        "space-only-value"
    ) == "", "Returning value should be stripped."
    # override default
    assert configs(
        " white space key ", strip=False
    ) == " white space value " and configs(
        "space-only-value", strip=False
    ) == "  ", "Returning value should ALLOW blank spaces."

    # no strip
    configs2 = GConfigs(backend=DummyBackend, strip=False)
    assert configs2.strip is False
    # strip default: False
    assert configs2(" white space key ") == " white space value " and configs2(
        "space-only-value"
    ) == "  ", "Returning value should ALLOW blank spaces."
    # override default
    assert configs2(
        " white space key ", strip=True
    ) == "white space value" and configs2(
        "space-only-value", strip=True
    ) == "", "Returning value should be stripped."
    configs2.strip = True
    assert configs2.strip


def test_get_typed_configs():
    """Check if gConfigs deal with typed configs
    Most backends will probably return strings as value of a config, but
    if someone cast the value it's nice to know if gConfigs is ok with this.
    """
    configs = GConfigs(backend=DummyBackend)
    assert configs("CONFIG-1") == "config-1"
    assert configs("CONFIG-NONE") is None
    assert configs("CONFIG-TRUE") is True
    assert configs("CONFIG-FALSE") is False
    assert configs("CONFIG-INT") == 1
    assert configs("CONFIG-FLOAT") == 1.1
    assert configs("CONFIG-LIST") == [1, 1.1, "a"]
    assert configs("CONFIG-TUPLE") == (1, 1.1, "a")
    assert configs("CONFIG-DICT") == {"a": 1, "b": "b"}


def test_get_and_cast_value():
    configs = GConfigs(backend=DummyBackend)
    # BOOLEAN
    assert configs.as_bool("CONFIG-TRUE")  # when backend return a bool already
    assert configs.as_bool("CONFIG-TRUE-STRING")
    assert isinstance(configs.as_bool("CONFIG-TRUE-STRING"), bool)
    assert not configs.as_bool("CONFIG-FALSE-STRING")
    assert isinstance(configs.as_bool("CONFIG-FALSE-STRING"), bool)
    assert configs.as_bool("NON-EXISTENT-CONFIG", default=True)
    assert isinstance(configs.as_bool("NON-EXISTENT-CONFIG", default=True), bool)
    with pytest.raises(ValueError, match=r".*Could not cast the value.*"):
        configs.as_bool("CONFIG-NONE")

    # LIST
    assert configs.as_list("CONFIG-LIST") == [1, 1.1, "a"]
    assert configs.as_list("CONFIG-TUPLE") == [1, 1.1, "a"]
    assert configs.as_list("CONFIG-LIST-STRING-JSON-STYLE") == [1, 1.1, "a"]
    with pytest.raises(ValueError, match=r".*Could not cast the value.*"):
        configs.as_list("CONFIG-NONE")

    # DICT
    assert configs.as_dict("CONFIG-DICT") == {"a": 1, "b": "b"}
    assert configs.as_dict("CONFIG-DICT-JSON-STYLE") == {"a": 1, "b": "b"}
    with pytest.raises(ValueError, match=r".*Could not cast the value.*"):
        configs.as_dict("CONFIG-NONE")

    # trigger exception on GConfigs._cast()
    with pytest.raises(ValueError, match=r".*must be a valid json value.*"):
        configs.as_list("CONFIG-LIST-STRING-JSON-STYLE-BROKEN")


def test_iterator():
    configs = GConfigs(backend=DummyBackend)
    # iterate with forloop
    for config in configs:
        # Make sure the object is a namedtuple
        assert issubclass(
            config.__class__, tuple
        ) and config._fields, "Looks like the iterator is not returning a namedtuple anymore."
        assert config
        assert config.key
        # guarantee the namedtuple is being properly created
        assert configs(
            config.key
        ) == config.value, "Looks like the namedtuple is not being properly created."

    # after an iterate in forloops it should have nothing left for next()
    with pytest.raises(StopIteration):
        next(configs)

    # but it's possible to iterator as many as you can with `self.iterator()`
    iter_configs = configs.iterator()
    for config in iter_configs:
        assert config


def test_json():
    configs = GConfigs(backend=DummyBackend)
    json_ = configs.json()
    assert json_
    # let's turn the json_ into a dict so we can see if it preserved all the configs
    configs_data = json.loads(json_)
    assert all(key in configs._backend.data for key in configs_data)

    assert next(
        configs
    ), "If `configs` is not iterable after `configs.json()` it's because it's not using the iterator properly."
