#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Settings management for Dream Prompter plugin."""

import base64
import json
import os
import platform
from typing import Any, Dict, Literal, Tuple, Union

from cryptography.fernet import Fernet, InvalidToken

from constants import (
    CONFIG_FILE_NAME,
    DEFAULT_API_KEY_VISIBLE,
    DEFAULT_MODE,
    DEFAULT_MODEL_VERSION,
    ENCRYPTION_KEY_FILE,
    FILE_PERMISSIONS,
    GIMP_VERSION,
)

ModeKey = Literal["edit", "generate"]
SettingsDict = Dict[str, Union[str, bool]]

DEFAULT_SETTINGS: SettingsDict = {
    "api_key": "",
    "mode": DEFAULT_MODE,
    "prompt": "",
    "api_key_visible": DEFAULT_API_KEY_VISIBLE,
    "model_version": DEFAULT_MODEL_VERSION,
}


def _get_encryption_key() -> bytes:
    """Get or create encryption key for API key storage."""
    key_file = os.path.join(os.path.dirname(get_config_file()), ENCRYPTION_KEY_FILE)

    try:
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)

            if platform.system() != "Windows":
                os.chmod(key_file, 0o600)

            return key
    except (OSError, PermissionError, IOError) as e:
        print(f"Warning: Could not access encryption key: {e}")
        # Fallback: generate a key but don't cache it
        return Fernet.generate_key()


def _encrypt_api_key(api_key: str) -> str:
    """Encrypt API key for secure storage."""
    if not api_key:
        return ""

    try:
        key = _get_encryption_key()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(api_key.encode())
        return base64.b64encode(encrypted).decode()
    except Exception as e:
        raise ValueError(f"Failed to encrypt API key: {e}")


def _decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt API key from secure storage."""
    if not encrypted_key:
        return ""

    try:
        key = _get_encryption_key()
        fernet = Fernet(key)
        decoded = base64.b64decode(encrypted_key)
        decrypted = fernet.decrypt(decoded)
        return decrypted.decode()
    except (InvalidToken, ValueError, UnicodeDecodeError, Exception) as e:
        raise ValueError(f"Failed to decrypt API key: {e}")


def _sanitize_string(value: Any, default: str = "") -> Tuple[str, bool]:
    """Return a trimmed string value and whether it changed during coercion."""

    if isinstance(value, str):
        sanitized = value.strip()
        return sanitized, sanitized != value

    if value is None:
        return default, default != value

    return str(value).strip(), True


def _sanitize_mode(value: Any) -> Tuple[str, bool]:
    """Normalize the stored editing mode to a supported value."""

    mode, changed = _sanitize_string(value, DEFAULT_MODE)
    if mode not in ("edit", "generate"):
        return DEFAULT_MODE, True
    return mode, changed


def _sanitize_bool(value: Any, default: bool) -> Tuple[bool, bool]:
    """Coerce persisted boolean-like values into strict booleans."""

    if isinstance(value, bool):
        return value, False

    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True, True
        if lowered in {"0", "false", "no", "off"}:
            return False, True
        return default, True

    if value is None:
        return default, True

    coerced = bool(value)
    return coerced, True


def _sanitize_model_version(value: Any) -> Tuple[str, bool]:
    """Ensure the model version string is populated with a sensible default."""

    model_version, changed = _sanitize_string(value, DEFAULT_MODEL_VERSION)
    if not model_version:
        return DEFAULT_MODEL_VERSION, True
    return model_version, changed


def _normalize_settings(data: Dict[str, Any]) -> Tuple[SettingsDict, bool]:
    """Merge persisted settings with defaults and record whether changes occurred."""

    normalized: SettingsDict = DEFAULT_SETTINGS.copy()
    changed = False

    encrypted_api_key = data.get("api_key", "")
    api_key_plain = _decrypt_api_key(str(encrypted_api_key))
    api_key, api_key_changed = _sanitize_string(api_key_plain, "")
    normalized["api_key"] = api_key
    # Don't mark as changed just for decryption - it's expected
    changed = changed or api_key_changed or ("api_key" not in data)

    mode, mode_changed = _sanitize_mode(data.get("mode"))
    normalized["mode"] = mode
    changed = changed or mode_changed or ("mode" not in data)

    prompt, prompt_changed = _sanitize_string(data.get("prompt"), "")
    normalized["prompt"] = prompt
    changed = changed or prompt_changed or ("prompt" not in data)

    api_key_visible, visibility_changed = _sanitize_bool(
        data.get("api_key_visible"),
        DEFAULT_API_KEY_VISIBLE,
    )
    normalized["api_key_visible"] = api_key_visible
    changed = changed or visibility_changed or ("api_key_visible" not in data)

    model_version, model_version_changed = _sanitize_model_version(
        data.get("model_version"),
    )
    normalized["model_version"] = model_version
    changed = changed or model_version_changed or ("model_version" not in data)

    return normalized, changed


def _write_settings(settings: SettingsDict) -> None:
    """Persist the provided settings to disk with appropriate permissions."""

    config_file = get_config_file()

    # Encrypt sensitive data before writing
    settings_to_write = settings.copy()
    if "api_key" in settings_to_write:
        settings_to_write["api_key"] = _encrypt_api_key(
            str(settings_to_write["api_key"]),
        )

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(settings_to_write, f, indent=2)

    if platform.system() != "Windows":
        os.chmod(config_file, FILE_PERMISSIONS)


def get_config_file() -> str:
    """Get path to config file in GIMP's user directory"""
    system = platform.system()

    if system == "Windows":
        gimp_dir = _get_windows_config_dir()
    elif system == "Darwin":
        gimp_dir = _get_macos_config_dir()
    else:
        gimp_dir = _get_linux_config_dir()

    gimp_dir = _expand_and_normalize_path(gimp_dir)

    try:
        os.makedirs(gimp_dir, exist_ok=True)
    except (OSError, PermissionError) as e:
        print(f"Warning: Could not create config directory {gimp_dir}: {e}")

    config_path = os.path.join(gimp_dir, CONFIG_FILE_NAME)
    return _expand_and_normalize_path(config_path)


def load_settings() -> SettingsDict:
    """Load settings from the config file, migrating older formats if needed."""

    try:
        config_file = get_config_file()
        if not os.path.exists(config_file):
            return DEFAULT_SETTINGS.copy()

        with open(config_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        if not isinstance(loaded, dict):
            print(
                "Warning: Invalid settings file format - expected JSON object, using defaults",
            )
            return DEFAULT_SETTINGS.copy()

        try:
            normalized, changed = _normalize_settings(loaded)
        except (ValueError, TypeError, KeyError) as e:
            print(f"Warning: Settings validation failed: {e}, using defaults")
            return DEFAULT_SETTINGS.copy()

        if changed:
            try:
                _write_settings(normalized)
            except (OSError, PermissionError, IOError) as write_error:
                print(f"Warning: Could not update settings file: {write_error}")

        return normalized

    except (OSError, PermissionError, IOError) as e:
        print(f"Warning: Could not access settings file: {e}")
    except json.JSONDecodeError as e:
        print(f"Warning: Settings file contains invalid JSON: {e}")
    except UnicodeDecodeError as e:
        print(f"Warning: Settings file encoding issue: {e}")
    except Exception as e:
        print(f"Warning: Unexpected error loading settings: {e}")

    return DEFAULT_SETTINGS.copy()


def store_settings(
    api_key: str,
    mode: ModeKey,
    prompt: str,
    api_key_visible: bool,
    model_version: str,
) -> None:
    """Store settings to config file"""
    if mode not in ("edit", "generate"):
        raise ValueError(f"Invalid mode: {mode}. Must be 'edit' or 'generate'")

    try:
        provided_settings = {
            "api_key": api_key,
            "mode": mode,
            "prompt": prompt,
            "api_key_visible": api_key_visible,
            "model_version": model_version,
        }

        try:
            normalized, _ = _normalize_settings(provided_settings)
        except (ValueError, TypeError, KeyError) as e:
            print(f"Warning: Settings validation failed: {e}")
            raise ValueError(f"Invalid settings provided: {e}")

        _write_settings(normalized)

    except (OSError, PermissionError, IOError) as e:
        print(f"Warning: Could not write settings file: {e}")
        raise IOError(f"Failed to save settings: {e}")
    except json.JSONDecodeError as e:
        print(f"Warning: JSON encoding failed: {e}")
        raise ValueError(f"Settings data could not be encoded as JSON: {e}")
    except UnicodeEncodeError as e:
        print(f"Warning: Text encoding issue: {e}")
        raise ValueError(f"Settings contain invalid characters: {e}")
    except Exception as e:
        print(f"Warning: Unexpected error storing settings: {e}")
        raise RuntimeError(f"Unexpected error while saving settings: {e}")


def _expand_and_normalize_path(path: str) -> str:
    """Expand user shorthand and normalize a filesystem path."""

    expanded = os.path.expanduser(path)
    # os.path.abspath preserves UNC prefixes on Windows while ensuring an
    # absolute path that works across platforms.
    absolute = os.path.abspath(expanded)
    return os.path.normpath(absolute)


def _get_linux_config_dir() -> str:
    """Get Linux config directory"""

    path = os.path.join(os.path.expanduser("~"), ".config", "GIMP", GIMP_VERSION)
    return _expand_and_normalize_path(path)


def _get_macos_config_dir() -> str:
    """Get macOS config directory"""
    home = os.path.expanduser("~")
    path = os.path.join(home, "Library", "Application Support", "GIMP", GIMP_VERSION)
    return _expand_and_normalize_path(path)


def _get_windows_config_dir() -> str:
    """Get Windows config directory"""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        appdata = os.path.expanduser("~\\AppData\\Roaming")
    path = os.path.join(appdata, "GIMP", GIMP_VERSION)
    return _expand_and_normalize_path(path)
