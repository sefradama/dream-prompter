#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prompt input UI components for Dream Prompter
Handles AI prompt text input
"""

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk  # noqa: E402
from i18n import _  # noqa: E402


class PromptInputUI:
    """Handles prompt text input UI components"""

    def __init__(self):
        self.prompt_textview = None
        self.prompt_buffer = None

    def create_prompt_section(self):
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

    def get_prompt_text(self):
        """Get the current prompt text"""
        if self.prompt_buffer:
            start_iter = self.prompt_buffer.get_start_iter()
            end_iter = self.prompt_buffer.get_end_iter()
            return self.prompt_buffer.get_text(start_iter, end_iter, False).strip()
        return ""
