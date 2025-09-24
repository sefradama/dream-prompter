#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface definitions for UI components in Dream Prompter
Provides abstract base classes with GObject signals for decoupled communication
"""

import abc
from typing import Any, List, Optional

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import GObject  # noqa: E402


class IModelConfig(GObject.Object):
    """Interface for model configuration UI component"""

    __gsignals__ = {
        "model_changed": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "api_key_changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "mode_changed": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def get_api_key_entry(self) -> Any:
        """Get the API key entry widget"""
        pass

    @abc.abstractmethod
    def get_toggle_visibility_btn(self) -> Any:
        """Get the toggle visibility button"""
        pass

    @abc.abstractmethod
    def get_model_combo(self) -> Any:
        """Get the model combo box"""
        pass

    @abc.abstractmethod
    def set_selected_model_version(self, model_version: str) -> bool:
        """Set the selected model version"""
        pass

    @abc.abstractmethod
    def get_selected_model_version(self) -> str:
        """Get the selected model version"""
        pass

    @abc.abstractmethod
    def toggle_api_key_visibility(self, button: Any) -> None:
        """Toggle API key visibility"""
        pass

    @abc.abstractmethod
    def get_model_parameters(self) -> dict:
        """Get model-specific parameters"""
        pass

    @abc.abstractmethod
    def get_output_format(self) -> Optional[str]:
        """Get output format"""
        pass

    @abc.abstractmethod
    def set_mode(self, mode: str) -> None:
        """Set the current mode"""
        pass

    @abc.abstractmethod
    def create_api_key_section(self) -> Any:
        """Create and return the API key section widget"""
        pass


class IModeSelection(GObject.Object):
    """Interface for mode selection UI component"""

    __gsignals__ = {
        "mode_changed": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def get_edit_mode_radio(self) -> Any:
        """Get the edit mode radio button"""
        pass

    @abc.abstractmethod
    def get_generate_mode_radio(self) -> Any:
        """Get the generate mode radio button"""
        pass

    @abc.abstractmethod
    def get_current_mode(self) -> str:
        """Get the currently selected mode"""
        pass

    @abc.abstractmethod
    def create_mode_section(self) -> Any:
        """Create and return the mode section widget"""
        pass


class IPromptInput(GObject.Object):
    """Interface for prompt input UI component"""

    __gsignals__ = {
        "prompt_changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def get_prompt_textview(self) -> Any:
        """Get the prompt text view"""
        pass

    @abc.abstractmethod
    def get_prompt_buffer(self) -> Any:
        """Get the prompt buffer"""
        pass

    @abc.abstractmethod
    def get_prompt_text(self) -> str:
        """Get the current prompt text"""
        pass

    @abc.abstractmethod
    def create_prompt_section(self) -> Any:
        """Create and return the prompt section widget"""
        pass


class IFileManagement(GObject.Object):
    """Interface for file management UI component"""

    __gsignals__ = {
        "files_changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def get_selected_files(self) -> List[str]:
        """Get the list of selected files"""
        pass

    @abc.abstractmethod
    def get_file_chooser_btn(self) -> Any:
        """Get the file chooser button"""
        pass

    @abc.abstractmethod
    def get_clear_files_btn(self) -> Any:
        """Get the clear files button"""
        pass

    @abc.abstractmethod
    def update_files_display(self) -> None:
        """Update the files display"""
        pass

    @abc.abstractmethod
    def create_additional_images_section(self) -> Any:
        """Create and return the additional images section widget"""
        pass


class IStatusProgress(GObject.Object):
    """Interface for status and progress UI component"""

    __gsignals__ = {
        "status_changed": (GObject.SignalFlags.RUN_FIRST, None, (str, float)),
    }

    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def get_status_label(self) -> Any:
        """Get the status label"""
        pass

    @abc.abstractmethod
    def get_progress_bar(self) -> Any:
        """Get the progress bar"""
        pass

    @abc.abstractmethod
    def update_status(self, message: str, percentage: Optional[float] = None) -> None:
        """Update status display"""
        pass

    @abc.abstractmethod
    def hide_progress(self) -> None:
        """Hide progress display"""
        pass

    @abc.abstractmethod
    def set_ui_enabled(
        self, enabled: bool, ui_components: Optional[List[Any]] = None
    ) -> None:
        """Enable/disable UI controls"""
        pass

    @abc.abstractmethod
    def create_status_section(self) -> Any:
        """Create and return the status section widget"""
        pass
