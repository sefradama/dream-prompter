#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File management UI components for Dream Prompter
Handles additional image selection and display
"""

import os

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Pango  # noqa: E402

from i18n import _  # noqa: E402


class FileManagementUI:
    """Handles additional image selection and display UI components"""

    def __init__(self):
        self.selected_files = []
        self.file_chooser_btn = None
        self.files_info_label = None
        self.clear_files_btn = None
        self.files_listbox = None
        self.images_help_label = None

    def create_additional_images_section(self):
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
            Gtk.Image.new_from_icon_name("document-open-symbolic", Gtk.IconSize.BUTTON),
        )
        files_container.pack_start(self.file_chooser_btn, False, False, 0)

        self.files_info_label = Gtk.Label()
        self.files_info_label.set_text(_("No additional images selected"))
        self.files_info_label.set_halign(Gtk.Align.START)
        self.files_info_label.get_style_context().add_class("dim-label")
        files_container.pack_start(self.files_info_label, True, True, 0)

        self.clear_files_btn = Gtk.Button()
        self.clear_files_btn.set_image(
            Gtk.Image.new_from_icon_name("edit-clear-symbolic", Gtk.IconSize.BUTTON),
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

    def update_files_display(self):
        """Update the files display"""
        if not self.selected_files:
            self._update_empty_files_display()
        else:
            self._update_files_with_content()

    def _update_empty_files_display(self):
        """Update display when no files are selected"""
        if self.files_info_label:
            self.files_info_label.set_text(_("No additional images selected"))
        if self.files_listbox:
            self.files_listbox.set_visible(False)
        if self.clear_files_btn:
            self.clear_files_btn.set_sensitive(False)

    def _update_files_with_content(self):
        """Update display when files are selected"""
        self._update_files_info_label()
        self._clear_existing_file_rows()
        self._create_file_rows()
        self._show_files_list()

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

    def _clear_existing_file_rows(self):
        """Clear existing file rows from the listbox"""
        if self.files_listbox:
            for child in self.files_listbox.get_children():
                self.files_listbox.remove(child)

    def _create_file_rows(self):
        """Create rows for each selected file"""
        if not self.files_listbox:
            return

        for file_path in self.selected_files:
            row = self._create_single_file_row(file_path)
            self.files_listbox.add(row)

    def _create_single_file_row(self, file_path):
        """Create a single file row widget"""
        filename = self._get_display_filename(file_path)

        row = Gtk.ListBoxRow()
        file_box = self._create_file_box(filename, file_path)
        row.add(file_box)
        return row

    def _create_file_box(self, filename, file_path):
        """Create the horizontal box for a file entry"""
        file_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        file_box.set_margin_top(3)
        file_box.set_margin_bottom(3)
        file_box.set_margin_start(6)
        file_box.set_margin_end(6)

        icon = Gtk.Image.new_from_icon_name(
            "image-x-generic-symbolic",
            Gtk.IconSize.SMALL_TOOLBAR,
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

    def _create_remove_button(self, file_path):
        """Create remove button for a file"""
        remove_btn = Gtk.Button()
        remove_btn.set_image(
            Gtk.Image.new_from_icon_name(
                "edit-delete-symbolic",
                Gtk.IconSize.SMALL_TOOLBAR,
            ),
        )
        remove_btn.set_relief(Gtk.ReliefStyle.NONE)

        # Note: Event handler connection should be done by the parent component
        # remove_btn.connect("clicked", event_handler.on_remove_file, file_path)

        return remove_btn

    def _show_files_list(self):
        """Make the files list visible"""
        if self.files_listbox:
            self.files_listbox.set_visible(True)
            self.files_listbox.show_all()

    def _get_display_filename(self, file_path):
        """Get filename with size info for display"""
        filename = os.path.basename(file_path)

        try:
            file_size = os.path.getsize(file_path)
            size_mb = file_size / (1024 * 1024)
            if size_mb > 7:
                filename += " " + _("⚠️ ({size:.1f} MB - Max Size Exceeded)").format(
                    size=size_mb,
                )
            elif size_mb > 1:
                filename += " " + _("({size:.1f} MB)").format(size=size_mb)
        except Exception:
            pass

        return filename
