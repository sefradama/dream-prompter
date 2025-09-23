#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Settings management for Dream Prompter plugin."""

import json
import os
import platform
from typing import Any, Dict, Literal, Tuple, Union

ModeKey = Literal["edit", "generate"]
SettingsDict = Dict[str, Union[str, bool]]

CONFIG_FILE_NAME = "dream-prompter-config.json"
GIMP_VERSION = "3.0"
FILE_PERMISSIONS = 0o600

DEFAULT_MODE: ModeKey = "edit"
DEFAULT_API_KEY_VISIBLE = False
DEFAULT_MODEL_VERSION = "google/nano-banana"
DEFAULT_SETTINGS: SettingsDict = {
    "api_key": "",
    "mode": DEFAULT_MODE,
    "prompt": "",
    "api_key_visible": DEFAULT_API_KEY_VISIBLE,
    "model_version": DEFAULT_MODEL_VERSION,
}


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

    api_key, api_key_changed = _sanitize_string(data.get("api_key"), "")
    normalized["api_key"] = api_key
    changed = changed or api_key_changed or ("api_key" not in data)

    mode, mode_changed = _sanitize_mode(data.get("mode"))
    normalized["mode"] = mode
    changed = changed or mode_changed or ("mode" not in data)

    prompt, prompt_changed = _sanitize_string(data.get("prompt"), "")
    normalized["prompt"] = prompt
    changed = changed or prompt_changed or ("prompt" not in data)

    api_key_visible, visibility_changed = _sanitize_bool(
        data.get("api_key_visible"), DEFAULT_API_KEY_VISIBLE
    )
    normalized["api_key_visible"] = api_key_visible
    changed = changed or visibility_changed or ("api_key_visible" not in data)

    model_version, model_version_changed = _sanitize_model_version(
        data.get("model_version")
    )
    normalized["model_version"] = model_version
    changed = changed or model_version_changed or ("model_version" not in data)

    return normalized, changed


def _write_settings(settings: SettingsDict) -> None:
    """Persist the provided settings to disk with appropriate permissions."""

    config_file = get_config_file()

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

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

    try:
        os.makedirs(gimp_dir, exist_ok=True)
    except (OSError, PermissionError) as e:
        print(f"Warning: Could not create config directory {gimp_dir}: {e}")

    return os.path.join(gimp_dir, CONFIG_FILE_NAME)


def load_settings() -> SettingsDict:
    """Load settings from the config file, migrating older formats if needed."""

    try:
        config_file = get_config_file()
        if not os.path.exists(config_file):
            return DEFAULT_SETTINGS.copy()

        with open(config_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        if not isinstance(loaded, dict):
            raise ValueError("Settings file must contain a JSON object")

        normalized, changed = _normalize_settings(loaded)

        if changed:
            try:
                _write_settings(normalized)
            except (OSError, PermissionError) as write_error:
                print(f"Warning: Could not update settings file: {write_error}")

        return normalized

    except (OSError, PermissionError) as e:
        print(f"Failed to read settings file: {e}")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in settings file: {e}")
    except Exception as e:
        print(f"Unexpected error loading settings: {e}")

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

        normalized, _ = _normalize_settings(provided_settings)
        _write_settings(normalized)

    except (OSError, PermissionError) as e:
        print(f"Failed to store settings: {e}")
    except (TypeError, ValueError) as e:
        print(f"Invalid data for JSON encoding: {e}")
    except Exception as e:
        print(f"Unexpected error storing settings: {e}")


def _get_linux_config_dir() -> str:
    """Get Linux config directory"""
    return os.path.join(os.path.expanduser("~"), ".config", "GIMP", GIMP_VERSION)


def _get_macos_config_dir() -> str:
    """Get macOS config directory"""
    home = os.path.expanduser("~")
    return os.path.join(home, "Library", "Application Support", "GIMP", GIMP_VERSION)


def _get_windows_config_dir() -> str:
    """Get Windows config directory"""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        appdata = os.path.expanduser("~\\AppData\\Roaming")
    return os.path.join(appdata, "GIMP", GIMP_VERSION)
