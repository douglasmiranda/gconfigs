"""Tests for `gconfigs.backends` package."""

import os

import pytest

from gconfigs.backends import DotEnv, File, INIFile, LocalEnv, LocalFiles, TOMLFile


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


def test_local_files_path_traversal_is_blocked(tmp_path):
    """LocalFiles must reject keys that resolve outside its base directory."""
    allowed_dir = tmp_path / "allowed"
    allowed_dir.mkdir()
    (tmp_path / "outside-secret").write_text("outside")

    backend = LocalFiles(path=allowed_dir)

    with pytest.raises(FileNotFoundError):
        backend.get("../outside-secret")


def test_local_files_pattern_is_non_recursive(tmp_path):
    """Patterns must match only files directly inside the configured directory."""
    nested_dir = tmp_path / "configs" / "nested"
    nested_dir.mkdir(parents=True)
    (tmp_path / "configs" / "a.txt").write_text("a")
    (nested_dir / "b.txt").write_text("b")

    backend = LocalFiles(path=tmp_path / "configs", pattern="*.txt")

    keys = tuple(backend.keys())
    assert "a.txt" in keys
    assert "b.txt" not in keys

    with pytest.raises(FileNotFoundError):
        backend.get("nested/b.txt")


def test_local_files_get_unreadable_file(monkeypatch, tmp_path):
    """LocalFiles should raise PermissionError for unreadable target files."""
    filepath = tmp_path / "configs" / "password"
    filepath.parent.mkdir(parents=True)
    filepath.write_text("top-secret")

    def deny_read_access(_path, mode):
        return False if mode == os.R_OK else os.access(_path, mode)

    monkeypatch.setattr(os, "access", deny_read_access)

    backend = LocalFiles(path=filepath.parent)
    with pytest.raises(PermissionError):
        backend.get(filepath.name)


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
    assert backend.get("TEST-EMPTY-WITHOUT-NEWLINE") == "", (
        "Final line empty values must be preserved even without trailing newline."
    )

    # just seeing if we can iterate over all configs
    empty_value_keys = {"CONFIG-EMPTY-VALUE", "TEST-EMPTY-WITHOUT-NEWLINE"}
    for key in backend.keys():
        assert not key.startswith(("#", ";", "[")), "Invalid lines must be removed."
        assert "=" not in key
        # keys with empty values should not be asserted as truthy
        if key in empty_value_keys:
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


def test_ini_file():
    backend = INIFile("./tests/files/config-files/.ini")

    keys = tuple(backend.keys())
    assert "app.name" in keys
    assert "database.port" in keys
    assert backend.get("app.name") == "gconfigs"
    assert backend.get("database.port") == "5432"

    with pytest.raises(KeyError):
        backend.get("app.non-existent")

    with pytest.raises(KeyError):
        backend.get("invalid-key-format")


def test_ini_file_missing_file():
    with pytest.raises(FileNotFoundError):
        INIFile("./tests/files/config-files/NON-EXISTENT-INI-FILE")


def test_toml_file():
    backend = TOMLFile("./tests/files/config-files/.toml")

    keys = tuple(backend.keys())
    assert "name" in keys
    assert "database.port" in keys
    assert "database.pool.size" in keys

    assert backend.get("name") == "gconfigs"
    assert backend.get("database.port") == 5432
    assert backend.get("database.pool.size") == 10

    with pytest.raises(KeyError):
        backend.get("database.non-existent")


def test_toml_file_missing_file():
    with pytest.raises(FileNotFoundError):
        TOMLFile("./tests/files/config-files/NON-EXISTENT-TOML-FILE")
