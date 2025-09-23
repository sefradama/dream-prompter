#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GTK UI components for Dream Prompter dialog
Handles all GTK interface creation and layout
"""

import os

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Pango  # noqa: E402
from i18n import _  # noqa: E402


REPLICATE_MODEL_OPTIONS = [
    (
        "google/nano-banana",
        _(
            "Nano Banana – Conversational image generation and editing with multi-image fusion support."
        ),
    ),
    (
        "bytedance/seedream-4",
        _(
            "SeeDream 4 – High-resolution text-to-image generation with optional reference guidance."
        ),
    ),
    (
        "qwen/qwen-image-edit",
        _(
            "Qwen Image Edit – Natural language guided edits for precise scene adjustments."
        ),
    ),
    (
        "jingyunliang/swinir:660d922d33153019e8c263a3bba265de882e7f4f70396546b6c9c8f9d47a021a",
        _(
            "SwinIR – Upscaling, denoising, and artifact reduction for real-world photographs."
        ),
    ),
    (
        "tencentarc/gfpgan:0fbacf7afc6c144e5be9767cff80f25aff23e52b0708f17e20f9879b2f21516c",
        _("GFPGAN – Restore facial details in portraits and vintage photos."),
    ),
]


class DreamPrompterUI:
    """Handles all GTK UI creation and layout"""

    def __init__(self):
        self.selected_files = []
        self.event_handler = None

        self.api_key_entry = None
        self.toggle_visibility_btn = None
        self.model_combo = None
        self.selected_model_version = ""
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

    def build_interface(self, parent_dialog):
        """Build the main plugin interface"""
        if not parent_dialog:
            return

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(16)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)

        try:
            api_key_section = self._create_api_key_section()
            main_box.pack_start(api_key_section, False, False, 0)

            mode_section = self._create_mode_section()
            main_box.pack_start(mode_section, False, False, 0)

            prompt_section = self._create_prompt_section()
            main_box.pack_start(prompt_section, True, True, 0)

            images_section = self._create_additional_images_section()
            main_box.pack_start(images_section, False, False, 0)

            buttons_section = self._create_buttons_section()
            main_box.pack_start(buttons_section, False, False, 0)

            status_section = self._create_status_section()
            main_box.pack_start(status_section, False, False, 0)

            parent_dialog.get_content_area().add(main_box)
        except Exception as e:
            print(f"Error building interface: {e}")

    def hide_progress(self):
        """Hide progress display"""
        if self.progress_bar:
            self.progress_bar.set_visible(False)
        if self.status_label:
            self.status_label.set_text(_("Ready"))

    def set_ui_enabled(self, enabled=True):
        """Enable/disable UI controls"""
        if self.api_key_entry:
            self.api_key_entry.set_sensitive(enabled)
        if self.toggle_visibility_btn:
            self.toggle_visibility_btn.set_sensitive(enabled)
        if self.model_combo:
            self.model_combo.set_sensitive(enabled)
        if self.edit_mode_radio:
            self.edit_mode_radio.set_sensitive(enabled)
        if self.generate_mode_radio:
            self.generate_mode_radio.set_sensitive(enabled)
        if self.prompt_textview:
            self.prompt_textview.set_sensitive(enabled)
        if self.file_chooser_btn:
            self.file_chooser_btn.set_sensitive(enabled)
        if self.clear_files_btn:
            self.clear_files_btn.set_sensitive(enabled)
        if self.generate_btn:
            self.generate_btn.set_sensitive(enabled)

    def set_selected_model_version(self, model_version):
        """Store the selected model version and update the combo box."""

        normalized = (model_version or "").strip()

        if normalized and self._model_id_exists(normalized):
            self.selected_model_version = normalized
            if self.model_combo:
                self.model_combo.set_active_id(normalized)
            return True

        default_id = self._get_default_model_id()
        self.selected_model_version = default_id
        if self.model_combo and default_id:
            self.model_combo.set_active_id(default_id)
        return False

    def get_selected_model_version(self):
        """Return the current model version selection."""

        if self.model_combo:
            active_id = self.model_combo.get_active_id()
            if active_id:
                self.selected_model_version = active_id
                return active_id

        return self.selected_model_version

    def _get_default_model_id(self):
        """Return the default model identifier from the options list."""

        if REPLICATE_MODEL_OPTIONS:
            return REPLICATE_MODEL_OPTIONS[0][0]
        return ""

    def _model_id_exists(self, model_id):
        """Check if the provided model ID exists in the options list."""

        for option_id, _label in REPLICATE_MODEL_OPTIONS:
            if option_id == model_id:
                return True
        return False

    def _on_model_combo_changed(self, combo):
        """Keep the stored model version synchronized with the combo box."""

        if not combo:
            return

        active_id = combo.get_active_id()
        self.selected_model_version = active_id or ""

    def toggle_api_key_visibility(self, button):
        """Toggle API key visibility and update button icon"""
        if not self.api_key_entry:
            return

        is_visible = button.get_active()
        self.api_key_entry.set_visibility(is_visible)

        icon_name = "view-reveal-symbolic" if is_visible else "view-conceal-symbolic"
        button.get_image().set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)

    def update_files_display(self):
        """Update the files display"""
        if not self.selected_files:
            self._update_empty_files_display()
        else:
            self._update_files_with_content()

    def update_status(self, message, percentage=None):
        """Update status display"""
        if self.status_label:
            self.status_label.set_text(message)

        if self.progress_bar:
            if percentage is not None:
                self.progress_bar.set_fraction(percentage)
                self.progress_bar.set_visible(True)
            else:
                self.progress_bar.pulse()
                self.progress_bar.set_visible(True)

    def _clear_existing_file_rows(self):
        """Clear existing file rows from the listbox"""
        if self.files_listbox:
            for child in self.files_listbox.get_children():
                self.files_listbox.remove(child)

    def _create_additional_images_section(self):
        """Create additional images selection section"""
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        title_label = Gtk.Label()
        title_label.set_markup(f"<b>{_('Additional Images (Optional)')}</b>")
        title_label.set_halign(Gtk.Align.START)
        section_box.pack_start(title_label, False, False, 0)

        files_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.file_chooser_btn = Gtk.Button()
        self.file_chooser_btn.set_label(_("Select Images..."))
        self.file_chooser_btn.set_image(
            Gtk.Image.new_from_icon_name("document-open-symbolic", Gtk.IconSize.BUTTON)
        )
        files_container.pack_start(self.file_chooser_btn, False, False, 0)

        self.files_info_label = Gtk.Label()
        self.files_info_label.set_text(_("No additional images selected"))
        self.files_info_label.set_halign(Gtk.Align.START)
        self.files_info_label.get_style_context().add_class("dim-label")
        files_container.pack_start(self.files_info_label, True, True, 0)

        self.clear_files_btn = Gtk.Button()
        self.clear_files_btn.set_image(
            Gtk.Image.new_from_icon_name("edit-clear-symbolic", Gtk.IconSize.BUTTON)
        )
        self.clear_files_btn.set_tooltip_text(_("Clear selected files"))
        self.clear_files_btn.set_sensitive(False)
        files_container.pack_start(self.clear_files_btn, False, False, 0)

        section_box.pack_start(files_container, False, False, 0)

        self.files_listbox = Gtk.ListBox()
        self.files_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.files_listbox.get_style_context().add_class("content")
        self.files_listbox.set_visible(False)
        section_box.pack_start(self.files_listbox, False, False, 0)

        self.images_help_label = Gtk.Label()
        self.images_help_label.set_halign(Gtk.Align.START)
        self.images_help_label.set_line_wrap(True)
        section_box.pack_start(self.images_help_label, False, False, 0)

        return section_box

    def _create_api_key_section(self):
        """Create API key input section"""
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        title_label = Gtk.Label()
        title_label.set_markup("<b>{}</b>".format(_("Replicate API Token")))
        title_label.set_halign(Gtk.Align.START)
        section_box.pack_start(title_label, False, False, 0)

        key_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.api_key_entry = Gtk.Entry()
        self.api_key_entry.set_placeholder_text(_("Enter your Replicate API token..."))
        self.api_key_entry.set_visibility(False)
        self.api_key_entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        key_container.pack_start(self.api_key_entry, True, True, 0)

        self.toggle_visibility_btn = Gtk.ToggleButton()
        self.toggle_visibility_btn.set_image(
            Gtk.Image.new_from_icon_name("view-conceal-symbolic", Gtk.IconSize.BUTTON)
        )
        self.toggle_visibility_btn.set_tooltip_text(_("Show/Hide API key"))
        key_container.pack_start(self.toggle_visibility_btn, False, False, 0)

        section_box.pack_start(key_container, False, False, 0)

        help_label = Gtk.Label()
        help_url = "https://replicate.com/account/api-tokens"
        help_text = _(
            'Get your token from <a href="{url}">replicate.com/account/api-tokens</a>'
        ).format(url=help_url)
        help_label.set_markup(f"<small>{help_text}</small>")
        help_label.set_halign(Gtk.Align.START)
        help_label.set_line_wrap(True)
        section_box.pack_start(help_label, False, False, 0)

        model_title = Gtk.Label()
        model_title.set_markup(f"<b>{_('Model')}</b>")
        model_title.set_halign(Gtk.Align.START)
        section_box.pack_start(model_title, False, False, 0)

        model_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.model_combo = Gtk.ComboBoxText()
        self.model_combo.set_hexpand(True)
        self.model_combo.set_tooltip_text(
            _("Choose which Replicate model to use for generation and editing.")
        )

        for model_id, label in REPLICATE_MODEL_OPTIONS:
            self.model_combo.append(model_id, label)

        self.model_combo.connect("changed", self._on_model_combo_changed)

        if self.selected_model_version:
            self.set_selected_model_version(self.selected_model_version)
        else:
            self.set_selected_model_version(self._get_default_model_id())

        model_row.pack_start(self.model_combo, True, True, 0)
        section_box.pack_start(model_row, False, False, 0)

        return section_box

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
                "applications-graphics-symbolic", Gtk.IconSize.BUTTON
            )
        )
        self.generate_btn.get_style_context().add_class("suggested-action")
        self.generate_btn.set_size_request(150, -1)
        buttons_box.pack_start(self.generate_btn, False, False, 0)

        return buttons_box

    def _create_file_box(self, filename, file_path):
        """Create the horizontal box for a file entry"""
        file_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        file_box.set_margin_top(3)
        file_box.set_margin_bottom(3)
        file_box.set_margin_start(6)
        file_box.set_margin_end(6)

        icon = Gtk.Image.new_from_icon_name(
            "image-x-generic-symbolic", Gtk.IconSize.SMALL_TOOLBAR
        )
        file_box.pack_start(icon, False, False, 0)

        label = Gtk.Label()
        label.set_text(filename)
        label.set_halign(Gtk.Align.START)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        file_box.pack_start(label, True, True, 0)

        remove_btn = self._create_remove_button(file_path)
        file_box.pack_start(remove_btn, False, False, 0)

        return file_box

    def _create_file_rows(self):
        """Create rows for each selected file"""
        if not self.files_listbox:
            return

        for file_path in self.selected_files:
            row = self._create_single_file_row(file_path)
            self.files_listbox.add(row)

    def _create_mode_section(self):
        """Create mode selection section"""
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        title_label = Gtk.Label()
        title_label.set_markup(f"<b>{_('Operation Mode')}</b>")
        title_label.set_halign(Gtk.Align.START)
        section_box.pack_start(title_label, False, False, 0)

        radio_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)

        self.edit_mode_radio = Gtk.RadioButton.new_with_label(None, _("Edit Image"))
        radio_box.pack_start(self.edit_mode_radio, False, False, 0)

        self.generate_mode_radio = Gtk.RadioButton.new_with_label_from_widget(
            self.edit_mode_radio, _("Generate Image")
        )
        radio_box.pack_start(self.generate_mode_radio, False, False, 0)

        section_box.pack_start(radio_box, False, False, 0)

        return section_box

    def _create_prompt_section(self):
        """Create prompt input section"""
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        title_label = Gtk.Label()
        title_label.set_markup(f"<b>{_('AI Prompt')}</b>")
        title_label.set_halign(Gtk.Align.START)
        section_box.pack_start(title_label, False, False, 0)

        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_window.set_min_content_height(120)

        self.prompt_textview = Gtk.TextView()
        self.prompt_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.prompt_buffer = self.prompt_textview.get_buffer()

        scroll_window.add(self.prompt_textview)
        section_box.pack_start(scroll_window, True, True, 0)

        return section_box

    def _create_remove_button(self, file_path):
        """Create remove button for a file"""
        remove_btn = Gtk.Button()
        remove_btn.set_image(
            Gtk.Image.new_from_icon_name(
                "edit-delete-symbolic", Gtk.IconSize.SMALL_TOOLBAR
            )
        )
        remove_btn.set_relief(Gtk.ReliefStyle.NONE)

        if self.event_handler:
            remove_btn.connect("clicked", self.event_handler.on_remove_file, file_path)

        return remove_btn

    def _create_single_file_row(self, file_path):
        """Create a single file row widget"""
        filename = self._get_display_filename(file_path)

        row = Gtk.ListBoxRow()
        file_box = self._create_file_box(filename, file_path)
        row.add(file_box)
        return row

    def _create_status_section(self):
        """Create status display section"""
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        self.status_label = Gtk.Label()
        self.status_label.set_text(_("Ready"))
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.get_style_context().add_class("dim-label")
        section_box.pack_start(self.status_label, False, False, 0)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(False)
        self.progress_bar.set_visible(False)
        section_box.pack_start(self.progress_bar, False, False, 0)

        return section_box

    def _get_display_filename(self, file_path):
        """Get filename with size info for display"""
        filename = os.path.basename(file_path)

        try:
            file_size = os.path.getsize(file_path)
            size_mb = file_size / (1024 * 1024)
            if size_mb > 7:
                filename += " " + _("⚠️ ({size:.1f} MB - Max Size Exceeded)").format(
                    size=size_mb
                )
            elif size_mb > 1:
                filename += " " + _("({size:.1f} MB)").format(size=size_mb)
        except Exception:
            pass

        return filename

    def _show_files_list(self):
        """Make the files list visible"""
        if self.files_listbox:
            self.files_listbox.set_visible(True)
            self.files_listbox.show_all()

    def _update_empty_files_display(self):
        """Update display when no files are selected"""
        if self.files_info_label:
            self.files_info_label.set_text(_("No additional images selected"))
        if self.files_listbox:
            self.files_listbox.set_visible(False)
        if self.clear_files_btn:
            self.clear_files_btn.set_sensitive(False)

    def _update_files_info_label(self):
        """Update the info label with file count"""
        if not self.files_info_label:
            return

        count = len(self.selected_files)
        if count == 1:
            text = _("{count} image selected").format(count=count)
        else:
            text = _("{count} images selected").format(count=count)

        self.files_info_label.set_text(text)

        if self.clear_files_btn:
            self.clear_files_btn.set_sensitive(True)

    def _update_files_with_content(self):
        """Update display when files are selected"""
        self._update_files_info_label()
        self._clear_existing_file_rows()
        self._create_file_rows()
        self._show_files_list()
