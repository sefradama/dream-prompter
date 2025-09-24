#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Status and progress UI components for Dream Prompter
Handles status display and progress indicators
"""

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk  # noqa: E402

from i18n import _  # noqa: E402
from ui_interfaces import IStatusProgress  # noqa: E402


class StatusProgressUI(IStatusProgress):
    """Handles status display and progress indicator UI components"""

    def __init__(self):
        self.status_label = None
        self.progress_bar = None

    def create_status_section(self):
        """Create status display section with label and progress bar.

        Returns:
            Gtk.Box: Vertical box containing status label and progress bar widgets.
        """
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

    def update_status(self, message, percentage=None):
        """Update status display with message and optional progress percentage.

        Args:
            message (str): Status message to display to user.
            percentage (float, optional): Progress percentage (0.0-1.0). If None,
                shows pulsing indeterminate progress.
        """
        if self.status_label:
            self.status_label.set_text(message)

        if self.progress_bar:
            if percentage is not None:
                self.progress_bar.set_fraction(percentage)
                self.progress_bar.set_visible(True)
            else:
                self.progress_bar.pulse()
                self.progress_bar.set_visible(True)

        self.emit("status_changed", message, percentage or 0.0)

    def hide_progress(self):
        """Hide progress display"""
        if self.progress_bar:
            self.progress_bar.set_visible(False)
        if self.status_label:
            self.status_label.set_text(_("Ready"))

    def set_ui_enabled(self, enabled=True, ui_components=None):
        """Enable/disable UI controls for user interaction during processing.

        Args:
            enabled (bool): Whether to enable (True) or disable (False) UI controls.
            ui_components (list, optional): List of GTK widgets to modify.
                If None, no action is taken.
        """
        if not ui_components:
            return

        for component in ui_components:
            if hasattr(component, "set_sensitive"):
                component.set_sensitive(enabled)
