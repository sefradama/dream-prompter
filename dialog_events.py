#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Event handlers for Dream Prompter dialog
Handles all user interactions and UI events
"""

import os
import threading

from gi.repository import GLib, Gtk

from dialog_threads import DreamPrompterThreads
from i18n import _
from settings import load_settings, store_settings

DEFAULT_MODEL_ENV_VAR = "REPLICATE_DEFAULT_MODEL"
DEFAULT_MODEL_FALLBACK = "google/nano-banana"


class DreamPrompterEventHandler:
    """Handles all dialog events and user interactions"""

    def __init__(self, dialog, ui, image, drawable):
        self.dialog = dialog
        self.ui = ui
        self.image = image
        self.drawable = drawable
        self.ui.event_handler = self

        # Thread lock for UI state synchronization
        self._ui_state_lock = threading.Lock()

        self.threads = DreamPrompterThreads(ui, image, drawable)
        self.threads.set_callbacks(
            {"on_success": self.close_on_success, "on_error": self.show_async_error},
        )

        self.dialog.connect("destroy", lambda w: self.threads.set_destroyed())

        settings = load_settings()
        self._model_version: str = self._determine_initial_model_version(settings)
        if hasattr(self.ui, "set_selected_model_version"):
            self.ui.set_selected_model_version(self._model_version)
        else:
            self.ui.selected_model_version = self._model_version
        if self.ui.toggle_visibility_btn and self.ui.api_key_entry:
            is_visible = settings.get("api_key_visible", False)
            self.ui.toggle_visibility_btn.set_active(is_visible)
            self.on_toggle_visibility(self.ui.toggle_visibility_btn)

        def after_init():
            if self.ui.api_key_entry:
                self.ui.api_key_entry.select_region(0, 0)
            if self.ui.prompt_textview:
                self.ui.prompt_textview.grab_focus()

            self.update_generate_button_state()

        GLib.idle_add(after_init)

    def close_on_success(self):
        """Handle successful completion - show success message since dialog is already closed"""
        success_msg = _("Image generation completed successfully!")
        try:
            dialog = Gtk.MessageDialog(
                parent=None,  # No parent since main dialog is closed
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text=success_msg,
            )
            dialog.run()
            dialog.destroy()
        except Exception as e:
            print(f"Warning: Unable to show success dialog: {e}")

    def show_async_error(self, message):
        """Show error message for async processing failures - dialog is already closed"""
        try:
            dialog = Gtk.MessageDialog(
                parent=None,  # No parent since main dialog is closed
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=message,
            )
            dialog.run()
            dialog.destroy()
        except Exception as e:
            print(f"Warning: Unable to show error dialog: {e}")

    def show_error(self, message):
        """Show error message in dialog for validation errors during user interaction"""
        if self.ui.status_label:
            self.ui.status_label.set_text(message)

        dialog = Gtk.MessageDialog(
            parent=self.dialog,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message,
        )
        dialog.run()
        dialog.destroy()

    def connect_all_signals(self):
        """Connect all UI signals to handlers"""
        # Connect to component signals
        self.ui.mode_selection.connect("mode_changed", self.on_mode_changed)
        self.ui.model_config.connect("model_changed", self.on_model_changed)
        self.ui.model_config.connect("api_key_changed", self.on_api_key_changed)
        self.ui.prompt_input.connect("prompt_changed", self.on_prompt_changed)
        self.ui.file_management.connect("files_changed", self.on_files_changed)
        self.ui.status_progress.connect("status_changed", self.on_status_changed)

        # Connect to widget signals for actions
        if self.ui.toggle_visibility_btn:
            self.ui.toggle_visibility_btn.connect("toggled", self.on_toggle_visibility)

        if self.ui.file_chooser_btn:
            self.ui.file_chooser_btn.connect("clicked", self.on_select_files)
        if self.ui.clear_files_btn:
            self.ui.clear_files_btn.connect("clicked", self.on_clear_files)

        if self.ui.cancel_btn:
            self.ui.cancel_btn.connect("clicked", self.on_cancel)
        if self.ui.generate_btn:
            self.ui.generate_btn.connect("clicked", self.on_generate)

    def _determine_initial_model_version(self, settings):
        """Resolve the starting model version from settings or environment."""

        stored_version = ""
        if isinstance(settings, dict):
            raw_version = settings.get("model_version", "")
            if isinstance(raw_version, str):
                stored_version = raw_version.strip()

        if stored_version:
            return stored_version

        env_version = os.getenv(DEFAULT_MODEL_ENV_VAR, "").strip()
        if env_version:
            return env_version

        return DEFAULT_MODEL_FALLBACK

    def on_api_key_changed(self, _entry):
        """Handle API key changes"""
        self.update_generate_button_state()

    def on_cancel(self, _button):
        """Handle cancel button click"""
        if self.threads.is_processing():
            self.threads.cancel_processing()
        else:
            self.dialog.response(Gtk.ResponseType.CANCEL)

    def on_clear_files(self, _button):
        """Clear selected files"""
        with self._ui_state_lock:
            self.ui.file_management.selected_files.clear()
            GLib.idle_add(self.ui.file_management.update_files_display)

    def get_selected_model_version(self) -> str:
        """Return the currently selected Replicate model version."""

        if hasattr(self.ui, "get_selected_model_version"):
            selected_version = self.ui.get_selected_model_version()
            if isinstance(selected_version, str) and selected_version.strip():
                normalized = selected_version.strip()
                self._model_version = normalized
                return normalized

        selected_attr = getattr(self.ui, "selected_model_version", "")
        if isinstance(selected_attr, str) and selected_attr.strip():
            normalized = selected_attr.strip()
            self._model_version = normalized
            return normalized

        if isinstance(self._model_version, str) and self._model_version.strip():
            return self._model_version.strip()

        env_version = os.getenv(DEFAULT_MODEL_ENV_VAR, "").strip()
        if env_version:
            self._model_version = env_version
            return env_version

        self._model_version = DEFAULT_MODEL_FALLBACK
        return DEFAULT_MODEL_FALLBACK

    def on_generate(self, _button):
        """Handle generate button - main AI processing entry point"""
        try:
            api_key = self.dialog.get_api_key()
            prompt_text = self.dialog.get_prompt()
        except Exception as e:
            error_msg = _("Error accessing form data: {error}").format(error=str(e))
            self.show_error(error_msg)
            return

        if not api_key:
            self.show_error(_("Please enter your Replicate API token"))
            return

        if not prompt_text:
            self.show_error(_("Please enter a prompt"))
            return

        if (
            hasattr(self.ui, "edit_mode_radio")
            and self.ui.edit_mode_radio
            and self.ui.edit_mode_radio.get_active()
            and not self.drawable
        ):
            self.show_error(_("Edit mode requires a selected layer"))
            return

        try:
            mode = self.dialog.get_current_mode()
            api_key_visible = self.dialog.get_api_key_visible()
            model_version = self.get_selected_model_version()
        except Exception as e:
            error_msg = _("Error accessing dialog state: {error}").format(error=str(e))
            self.show_error(error_msg)
            return

        # Validate model version before proceeding to prevent crashes
        if not model_version or not model_version.strip():
            self.show_error(_("Please select a valid AI model"))
            return

        try:
            store_settings(
                api_key,
                mode,
                prompt_text,
                api_key_visible,
                model_version,
            )
        except Exception as e:
            print(f"Warning: Failed to save settings: {e}")  # Continue anyway for now

        if self.ui.status_label:
            self.ui.status_label.set_text(_("Initializing Replicate request..."))

        # Synchronous processing while dialog remains open for proper UI handling
        try:
            if self.ui.status_label:
                self.ui.status_label.set_text(_("Processing request..."))

            if mode == "edit":
                output_format = (
                    self.ui.get_output_format()
                    if hasattr(self.ui, "get_output_format")
                    else None
                )
                success, result_msg = self._sync_edit(
                    api_key,
                    prompt_text,
                    self.ui.selected_files,
                    model_version,
                    output_format,
                )
            else:
                success, result_msg = self._sync_generate(
                    api_key, prompt_text, self.ui.selected_files, model_version
                )

            if success:
                self.dialog.response(Gtk.ResponseType.OK)
            else:
                self.show_error(result_msg)

        except Exception as e:
            error_msg = "Unexpected error during processing: {0}".format(str(e))
            self.show_error(error_msg)

    def on_mode_changed(self, mode_selection, mode):
        """Handle mode selection changes"""
        with self._ui_state_lock:
            if mode == "edit":
                if len(self.ui.selected_files) > 2:
                    self.ui.selected_files = self.ui.selected_files[:2]
                    GLib.idle_add(self.ui.update_files_display)
                    print(_("Reduced to 2 reference images for edit mode"))

                if self.ui.generate_btn:
                    GLib.idle_add(
                        lambda: self.ui.generate_btn.set_label(_("Generate Edit")),
                    )
                if self.ui.images_help_label:
                    help_text = "<small>{0}</small>".format(
                        _("Select up to 2 additional images")
                    )
                    GLib.idle_add(
                        lambda: self.ui.images_help_label.set_markup(help_text),
                    )
                self.ui.model_config.set_mode("edit")
            else:
                if self.ui.generate_btn:
                    GLib.idle_add(
                        lambda: self.ui.generate_btn.set_label(_("Generate Image")),
                    )
                if self.ui.images_help_label:
                    help_text = "<small>{0}</small>".format(
                        _("Select up to 3 additional images")
                    )
                    GLib.idle_add(
                        lambda: self.ui.images_help_label.set_markup(help_text),
                    )
                self.ui.model_config.set_mode("generate")

        self.update_generate_button_state()

    def on_model_changed(self, model_config, model_version):
        """Handle model selection changes"""
        self._model_version = model_version
        # Update UI if needed

    def on_files_changed(self, file_management):
        """Handle file selection changes"""
        # Files display is updated by the component
        self.update_generate_button_state()

    def on_status_changed(self, status_progress, message, percentage):
        """Handle status changes"""
        # Status is updated by the component
        pass

    def on_prompt_changed(self, _buffer):
        """Handle prompt text changes"""
        self.update_generate_button_state()

    def on_remove_file(self, _button, file_path):
        """Remove a specific file from selection"""
        with self._ui_state_lock:
            selected_files = self.ui.file_management.get_selected_files()
            if file_path in selected_files:
                self.ui.file_management.selected_files.remove(file_path)
                GLib.idle_add(self.ui.file_management.update_files_display)

    def on_select_files(self, _button):
        """Open file chooser for reference images"""
        dialog = Gtk.FileChooserDialog(
            title=_("Select Reference Images"),
            parent=self.dialog,
            action=Gtk.FileChooserAction.OPEN,
        )

        dialog.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        dialog.add_button(_("Select"), Gtk.ResponseType.OK)

        image_filter = Gtk.FileFilter()
        image_filter.set_name(_("Supported Images (PNG, JPEG, WebP)"))
        image_filter.add_mime_type("image/png")
        image_filter.add_mime_type("image/jpeg")
        image_filter.add_mime_type("image/webp")
        dialog.add_filter(image_filter)

        dialog.set_select_multiple(True)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            files = dialog.get_filenames()

            current_mode = self.dialog.get_current_mode()
            if current_mode == "edit":
                max_total_files = 2
            else:
                max_total_files = 3

            with self._ui_state_lock:
                selected_files = self.ui.file_management.get_selected_files()
                max_new_files = max_total_files - len(selected_files)
                if max_new_files > 0:
                    self.ui.file_management.selected_files.extend(files[:max_new_files])
                    GLib.idle_add(self.ui.file_management.update_files_display)
                elif files:
                    if current_mode == "edit":
                        print(
                            _(
                                "Cannot add {count} files. Maximum 2 reference images allowed in edit mode.",
                            ).format(count=len(files)),
                        )
                    else:
                        print(
                            _(
                                "Cannot add {count} files. Maximum 3 reference images allowed.",
                            ).format(count=len(files)),
                        )

        dialog.destroy()

    def on_toggle_visibility(self, button):
        """Handle API key visibility toggle"""
        if not self.ui.api_key_entry:
            return

        if button.get_active():
            self.ui.api_key_entry.set_visibility(True)
            button.set_image(
                Gtk.Image.new_from_icon_name(
                    "view-reveal-symbolic",
                    Gtk.IconSize.BUTTON,
                ),
            )
            button.set_tooltip_text(_("Hide API key"))
        else:
            self.ui.api_key_entry.set_visibility(False)
            button.set_image(
                Gtk.Image.new_from_icon_name(
                    "view-conceal-symbolic",
                    Gtk.IconSize.BUTTON,
                ),
            )
            button.set_tooltip_text(_("Show API key"))

    def _sync_generate(self, api_key, prompt, reference_images, model_version):
        """Synchronous image generation with proper UI updates"""
        from api import ReplicateAPI
        from integrator import create_new_image

        try:
            # Get model-specific parameters
            extra_params = (
                self.ui.get_model_parameters()
                if hasattr(self.ui, "get_model_parameters")
                else {}
            )

            api = ReplicateAPI(api_key, model_version)

            if self.ui.status_label:
                self.ui.status_label.set_text(_("Preparing generation request..."))

            pixbuf, error_msg = api.generate_image(
                prompt=prompt,
                reference_images=reference_images,
                extra_params=extra_params,
                progress_callback=self._sync_progress_callback,
                stream_callback=self._sync_stream_callback,
            )

            if error_msg:
                return False, error_msg

            if not pixbuf:
                error_msg = _("No image data received from API")
                return False, error_msg

            if self.ui.status_label:
                self.ui.status_label.set_text(_("Creating new GIMP image..."))

            image = create_new_image(pixbuf, prompt)
            if not image:
                error_msg = _("Failed to create GIMP image")
                return False, error_msg

            return True, _("Image generated successfully!")

        except Exception as e:
            error_msg = "Generation failed: {0}".format(str(e))
            return False, error_msg

    def _sync_edit(
        self, api_key, prompt, reference_images, model_version, output_format=None
    ):
        """Synchronous image editing with proper UI updates"""
        from api import ReplicateAPI
        from integrator import create_edit_layer

        try:
            if not self.image or not self.drawable:
                error_msg = _("No image available for editing")
                return False, error_msg

            api = ReplicateAPI(api_key, model_version)

            if self.ui.status_label:
                self.ui.status_label.set_text(_("Preparing edit request..."))

            pixbuf, error_msg = api.edit_image(
                image=self.image,
                prompt=prompt,
                reference_images=reference_images,
                output_format=output_format,
                progress_callback=self._sync_progress_callback,
                stream_callback=self._sync_stream_callback,
            )

            if error_msg:
                return False, error_msg

            if not pixbuf:
                error_msg = _("No image data received from API")
                return False, error_msg

            if self.ui.status_label:
                self.ui.status_label.set_text(_("Adding edit layer..."))

            layer = create_edit_layer(self.image, self.drawable, pixbuf, prompt)
            if not layer:
                error_msg = _("Failed to create edit layer")
                return False, error_msg

            return True, _("Image edited successfully!")

        except Exception as e:
            error_msg = "Editing failed: {0}".format(str(e))
            return False, error_msg

    def _sync_progress_callback(self, message, percentage=None):
        """Progress callback that works while dialog is still open"""
        if self.ui.status_label:
            self.ui.status_label.set_text(message)
        # Update progress bar if available
        if hasattr(self.ui, "status_progress_ui") and self.ui.status_progress_ui:
            self.ui.status_progress_ui.update_status(message, percentage)
        return True  # Continue processing

    def _sync_stream_callback(self, message):
        """Stream callback that works while dialog is still open"""
        if self.ui.status_label:
            self.ui.status_label.set_text(message)
        return True  # Continue processing

    def update_generate_button_state(self):
        """Update generate button sensitivity based on input state"""
        if (
            not self.ui.prompt_buffer
            or not self.ui.api_key_entry
            or not self.ui.generate_btn
        ):
            return

        prompt_text = self.dialog.get_prompt()
        api_key = self.dialog.get_api_key()
        current_mode = self.dialog.get_current_mode()

        has_text = bool(prompt_text)
        has_api_key = bool(api_key)

        if current_mode == "edit":
            has_drawable = self.drawable is not None
            self.ui.generate_btn.set_sensitive(
                has_text and has_api_key and has_drawable,
            )
        else:
            self.ui.generate_btn.set_sensitive(has_text and has_api_key)
