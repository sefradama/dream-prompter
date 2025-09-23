#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Model configuration UI components for Dream Prompter
Handles API key input and model selection
"""

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk  # noqa: E402

from i18n import _  # noqa: E402

REPLICATE_MODEL_OPTIONS = [
    (
        "google/nano-banana",
        _(
            "Nano Banana – Conversational image generation and editing with multi-image fusion support.",
        ),
    ),
    (
        "bytedance/seedream-4",
        _(
            "SeeDream 4 – High-resolution text-to-image generation with optional reference guidance.",
        ),
    ),
    (
        "qwen/qwen-image-edit",
        _(
            "Qwen Image Edit – Natural language guided edits for precise scene adjustments.",
        ),
    ),
    (
        "jingyunliang/swinir:660d922d33153019e8c263a3bba265de882e7f4f70396546b6c9c8f9d47a021a",
        _(
            "SwinIR – Upscaling, denoising, and artifact reduction for real-world photographs.",
        ),
    ),
    (
        "tencentarc/gfpgan:0fbacf7afc6c144e5be9767cff80f25aff23e52b0708f17e20f9879b2f21516c",
        _("GFPGAN – Restore facial details in portraits and vintage photos."),
    ),
]


class ModelConfigUI:
    """Handles API key input and model selection UI components"""

    def __init__(self):
        self.api_key_entry = None
        self.toggle_visibility_btn = None
        self.model_combo = None
        self.selected_model_version = ""

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

        # Fallback to stored version or default
        if self.selected_model_version and self._model_id_exists(self.selected_model_version):
            return self.selected_model_version

        # Final fallback to default
        default_id = self._get_default_model_id()
        self.selected_model_version = default_id
        return default_id

    def create_api_key_section(self):
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
            Gtk.Image.new_from_icon_name("view-conceal-symbolic", Gtk.IconSize.BUTTON),
        )
        self.toggle_visibility_btn.set_tooltip_text(_("Show/Hide API key"))
        key_container.pack_start(self.toggle_visibility_btn, False, False, 0)

        section_box.pack_start(key_container, False, False, 0)

        help_label = Gtk.Label()
        help_url = "https://replicate.com/account/api-tokens"
        help_text = _(
            'Get your token from <a href="{url}">replicate.com/account/api-tokens</a>',
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
            _("Choose which Replicate model to use for generation and editing."),
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
