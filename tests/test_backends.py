"""Tests for `gconfigs.backends` package.
"""
import os

import pytest

from gconfigs.backends import LocalEnv, LocalMountFile, DotEnv, RootDirectoryNotFound


def test_local_env():
    """Tests for `gconfigs.backends.LocalEnv`
    """
    os.environ.update({"GCONFIGS_ENV_TEST": "env-test-1"})
    backend = LocalEnv()

    assert "GCONFIGS_ENV_TEST" in backend.keys()
    assert backend.get("GCONFIGS_ENV_TEST") == "env-test-1"
    with pytest.raises(KeyError):
        backend.get("GCONFIGS_NON-EXISTENT-ENV-KEY")


def test_local_mount_file_generic():
    """Tests for `gconfigs.backends.LocalMountFile` with root_dir='./tests/files/configs'
    """
    with pytest.raises(RootDirectoryNotFound):
        backend = LocalMountFile(root_dir="./NON-EXISTENT-DIR")
        assert backend.root_dir

    backend = LocalMountFile(root_dir="./tests/files/configs")
    assert "CONFIG_TEST" in backend.keys()
    assert backend.get("CONFIG_TEST") == "config-test"

    with pytest.raises(FileNotFoundError):
        backend.get("NON-EXISTENT-CONFIG")


def test_dotenv():
    backend = DotEnv()
    with pytest.raises(Exception, match=r".*you didn't loaded the your dotenv file.*"):
        backend.get("CONFIG-1")

    backend.load_file("./tests/files/config-files/.env")
    assert "CONFIG-1" in backend.keys()
    with pytest.raises(KeyError):
        backend.get("NON-EXISTENT-CONFIG-KEY")

    # `.get` must filter break lines
    assert "\n" not in backend.get("CONFIG-1") and "\r" not in backend.get(
        "CONFIG-1"
    ), "Breaklines on values must be removed."

    assert backend.get("CONFIG-1") == "config-1"
    assert "config-key-with-spaces" in backend.keys(), "Keys must be stripped."
    assert backend.get(
        "config-value-with-spaces"
    ) == " config value with spaces", "values should NOT be stripped."

    assert "COMMENTED-CONFIG" not in backend.keys()
    assert backend.get("CONFIG-EMPTY-VALUE") == "", "Empty values must be empty string."

    # just seeing if we can iterate over all configs
    for key in backend.keys():
        assert not key.startswith(("#", ";", "[")), "Invalid lines must be removed."
        assert "=" not in key
        # the `CONFIG-EMPTY-VALUE` will be an empty value, so, no good to assert
        if key == "CONFIG-EMPTY-VALUE":
            continue

        assert backend.get(key)

    # Empty .env file
    with pytest.raises(Exception, match=r".*You have no configs to look for.*"):
        backend.load_file("./tests/files/config-files/.env-empty")

    with pytest.raises(FileNotFoundError):
        backend.load_file("./tests/files/config-files/NON-EXISTENT-DOTENV-FILE")
