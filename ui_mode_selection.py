#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mode selection UI components for Dream Prompter
Handles edit vs generate mode selection
"""

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk  # noqa: E402

from i18n import _  # noqa: E402
from ui_interfaces import IModeSelection  # noqa: E402


class ModeSelectionUI(IModeSelection):
    """Handles operation mode selection UI components"""

    def __init__(self):
        super().__init__()
        self.edit_mode_radio = None
        self.generate_mode_radio = None

    def create_mode_section(self):
        """Create mode selection section"""
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        title_label = Gtk.Label()
        title_label.set_markup(f"<b>{_('Operation Mode')}</b>")
        title_label.set_halign(Gtk.Align.START)
        section_box.pack_start(title_label, False, False, 0)

        radio_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)

        self.edit_mode_radio = Gtk.RadioButton.new_with_label(None, _("Edit Image"))
        self.edit_mode_radio.connect("toggled", self._on_mode_changed)
        radio_box.pack_start(self.edit_mode_radio, False, False, 0)

        self.generate_mode_radio = Gtk.RadioButton.new_with_label_from_widget(
            self.edit_mode_radio,
            _("Generate Image"),
        )
        self.generate_mode_radio.connect("toggled", self._on_mode_changed)
        radio_box.pack_start(self.generate_mode_radio, False, False, 0)

        section_box.pack_start(radio_box, False, False, 0)

        return section_box

    def _on_mode_changed(self, radio_button):
        """Emit mode changed signal"""
        if radio_button.get_active():
            mode = self.get_current_mode()
            self.emit("mode_changed", mode)

    def get_current_mode(self):
        """Get the currently selected mode"""
        if self.generate_mode_radio and self.generate_mode_radio.get_active():
            return "generate"
        return "edit"
