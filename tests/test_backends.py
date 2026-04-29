"""Tests for `gconfigs.backends` package."""

import os

import pytest

from gconfigs.backends import DotEnv, File, LocalEnv, LocalFiles


def test_local_env():
    """Tests for `gconfigs.backends.LocalEnv`"""
    os.environ.update({"GCONFIGS_ENV_TEST": "env-test-1"})
    backend = LocalEnv()

    assert "GCONFIGS_ENV_TEST" in backend.keys()
    assert backend.get("GCONFIGS_ENV_TEST") == "env-test-1"
    with pytest.raises(KeyError):
        backend.get("GCONFIGS_NON-EXISTENT-ENV-KEY")


def test_local_mount_file_generic():
    """Tests for `gconfigs.backends.LocalFiles` with path='./tests/files/configs'"""
    with pytest.raises(FileNotFoundError):
        backend = LocalFiles(path="./NON-EXISTENT-DIR")

    with pytest.raises(NotADirectoryError):
        backend = LocalFiles(path="./tests/files/config-files/.env")

    backend = LocalFiles(path="./tests/files/configs")
    assert "CONFIG_TEST" in backend.keys()
    assert backend.get("CONFIG_TEST") == "config-test"

    with pytest.raises(FileNotFoundError):
        backend.get("NON-EXISTENT-CONFIG")


def test_dotenv():
    backend = DotEnv("./tests/files/config-files/.env")

    assert "CONFIG-1" in backend.keys()
    with pytest.raises(KeyError):
        backend.get("NON-EXISTENT-CONFIG-KEY")

    # `.get` must filter break lines
    assert "\n" not in backend.get("CONFIG-1") and "\r" not in backend.get(
        "CONFIG-1"
    ), "Breaklines on values must be removed."

    assert backend.get("CONFIG-1") == "config-1"
    assert "config-key-with-spaces" in backend.keys(), "Keys must be stripped."
    assert backend.get("config-value-with-spaces") == " config value with spaces", (
        "values should NOT be stripped."
    )

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
    backend.load_file("./tests/files/config-files/.env-empty")
    assert not backend.keys()

    with pytest.raises(FileNotFoundError):
        backend.load_file("./tests/files/config-files/NON-EXISTENT-DOTENV-FILE")


def test_file_keys_returns_empty_tuple():
    backend = File()
    assert backend.keys() == tuple()


def test_file_get_success(tmp_path):
    filepath = tmp_path / "secret.txt"
    filepath.write_text("super-secret")

    backend = File()
    assert backend.get(str(filepath)) == "super-secret"


def test_file_get_missing_file():
    backend = File()

    with pytest.raises(FileNotFoundError):
        backend.get("./tests/files/local_file/NON-EXISTENT-FILE")


def test_file_get_unreadable_file(monkeypatch, tmp_path):
    filepath = tmp_path / "password"
    filepath.write_text("top-secret")

    def deny_read_access(_path, mode):
        return False if mode == os.R_OK else os.access(_path, mode)

    monkeypatch.setattr(os, "access", deny_read_access)

    backend = File()
    with pytest.raises(PermissionError):
        backend.get(str(filepath))
