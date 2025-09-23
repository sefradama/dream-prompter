#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dream Prompter UI Coordinator
Orchestrates modular UI components for the dialog
"""

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk  # noqa: E402

from i18n import _  # noqa: E402
from ui_file_management import FileManagementUI  # noqa: E402
from ui_mode_selection import ModeSelectionUI  # noqa: E402
from ui_model_config import ModelConfigUI  # noqa: E402
from ui_prompt_input import PromptInputUI  # noqa: E402
from ui_status_progress import StatusProgressUI  # noqa: E402


class DreamPrompterUI:
    """Main UI coordinator that orchestrates modular components"""

    def __init__(self):
        # Initialize UI component modules
        self.model_config = ModelConfigUI()
        self.mode_selection = ModeSelectionUI()
        self.prompt_input = PromptInputUI()
        self.file_management = FileManagementUI()
        self.status_progress = StatusProgressUI()

        # Legacy attributes for backward compatibility
        self.selected_files = self.file_management.selected_files
        self.selected_model_version = self.model_config.selected_model_version

        # Component references for event handlers
        self.api_key_entry = None
        self.toggle_visibility_btn = None
        self.model_combo = None
        self.edit_mode_radio = None
        self.generate_mode_radio = None
        self.prompt_textview = None
        self.prompt_buffer = None
        self.file_chooser_btn = None
        self.files_info_label = None
        self.clear_files_btn = None
        self.files_listbox = None
        self.images_help_label = None
        self.cancel_btn = None
        self.generate_btn = None
        self.status_label = None
        self.progress_bar = None

        self.event_handler = None

    def build_interface(self, parent_dialog):
        """Build the main plugin interface using modular components"""
        if not parent_dialog:
            return

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(16)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)

        try:
            # Build interface using modular components
            api_key_section = self.model_config.create_api_key_section()
            main_box.pack_start(api_key_section, False, False, 0)

            mode_section = self.mode_selection.create_mode_section()
            main_box.pack_start(mode_section, False, False, 0)

            prompt_section = self.prompt_input.create_prompt_section()
            main_box.pack_start(prompt_section, True, True, 0)

            images_section = self.file_management.create_additional_images_section()
            main_box.pack_start(images_section, False, False, 0)

            buttons_section = self._create_buttons_section()
            main_box.pack_start(buttons_section, False, False, 0)

            status_section = self.status_progress.create_status_section()
            main_box.pack_start(status_section, False, False, 0)

            parent_dialog.get_content_area().add(main_box)

            # Wire up component references for backward compatibility
            self._wire_component_references()

        except Exception as e:
            print(f"Error building interface: {e}")

    def _wire_component_references(self):
        """Wire component references for backward compatibility"""
        # Model config references
        self.api_key_entry = self.model_config.api_key_entry
        self.toggle_visibility_btn = self.model_config.toggle_visibility_btn
        self.model_combo = self.model_config.model_combo

        # Mode selection references
        self.edit_mode_radio = self.mode_selection.edit_mode_radio
        self.generate_mode_radio = self.mode_selection.generate_mode_radio

        # Prompt input references
        self.prompt_textview = self.prompt_input.prompt_textview
        self.prompt_buffer = self.prompt_input.prompt_buffer

        # File management references
        self.file_chooser_btn = self.file_management.file_chooser_btn
        self.files_info_label = self.file_management.files_info_label
        self.clear_files_btn = self.file_management.clear_files_btn
        self.files_listbox = self.file_management.files_listbox
        self.images_help_label = self.file_management.images_help_label

        # Status progress references
        self.status_label = self.status_progress.status_label
        self.progress_bar = self.status_progress.progress_bar

    def hide_progress(self):
        """Hide progress display"""
        self.status_progress.hide_progress()

    def set_ui_enabled(self, enabled=True):
        """Enable/disable UI controls through component modules"""
        ui_components = [
            self.api_key_entry,
            self.toggle_visibility_btn,
            self.model_combo,
            self.edit_mode_radio,
            self.generate_mode_radio,
            self.prompt_textview,
            self.file_chooser_btn,
            self.clear_files_btn,
            self.generate_btn,
        ]
        self.status_progress.set_ui_enabled(enabled, ui_components)

    def set_selected_model_version(self, model_version):
        """Delegate to model config component"""
        return self.model_config.set_selected_model_version(model_version)

    def get_selected_model_version(self):
        """Delegate to model config component"""
        return self.model_config.get_selected_model_version()

    def toggle_api_key_visibility(self, button):
        """Delegate to model config component"""
        self.model_config.toggle_api_key_visibility(button)

    def update_files_display(self):
        """Delegate to file management component"""
        self.file_management.update_files_display()

    def update_status(self, message, percentage=None):
        """Delegate to status progress component"""
        self.status_progress.update_status(message, percentage)

    def _create_buttons_section(self):
        """Create action buttons section"""
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        buttons_box.set_halign(Gtk.Align.CENTER)

        self.cancel_btn = Gtk.Button()
        self.cancel_btn.set_label(_("Cancel"))
        self.cancel_btn.set_size_request(100, -1)
        buttons_box.pack_start(self.cancel_btn, False, False, 0)

        self.generate_btn = Gtk.Button()
        self.generate_btn.set_label(_("Generate Edit"))
        self.generate_btn.set_image(
            Gtk.Image.new_from_icon_name(
                "applications-graphics-symbolic", Gtk.IconSize.BUTTON,
            ),
        )
        self.generate_btn.get_style_context().add_class("suggested-action")
        self.generate_btn.set_size_request(150, -1)
        buttons_box.pack_start(self.generate_btn, False, False, 0)

        return buttons_box
