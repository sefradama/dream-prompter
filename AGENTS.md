# Dream Prompter Contribution Guidelines

Welcome! This document captures project-wide conventions for the Dream Prompter GIMP plugin. Follow these notes for any change unless a more specific instruction overrides them.

## Project Overview
- The plugin embeds Google's Gemini "Nano Banana" model into GIMP via Python plug-in hooks.
- GTK UI widgets live in Python modules alongside GIMP-specific integration helpers. Keep the separation between UI layout, event orchestration, threading, API integration, and GIMP image manipulation.
- The repository ships ready-to-install code; avoid assuming availability of extra build tooling or packaging systems.

## Repository Layout
- `dream-prompter.py`: Entry point registered with GIMP. Limit it to plug-in registration and dialog bootstrap logic.
- `dialog.py`: High-level dialog controller that wires the GTK layout and event handlers together.
- `dialog_gtk.py`: UI construction routines. All widget creation and layout changes belong here.
- `dialog_events.py`: Signal handlers, validation, and user interaction logic.
- `dialog_threads.py`: Background threading and GLib handoff helpers for API calls and GIMP updates. Any new asynchronous work should follow its patterns.
- `api.py`: Gemini API integration and request/response handling.
- `integrator.py`: Functions that translate pixbufs into GIMP images/layers and export existing layers.
- `settings.py`: Persistent configuration helpers that must remain cross-platform.
- `locale/`: gettext `.po` files (one per language). Maintain translations when user-visible text changes.
- `scripts/`: Automation for translation catalogs (`build-translations.py`, `update-pot.py`, `update-translations.py`). Use these when adjusting localization resources.
- `screenshots/`: Documentation imagery referenced by `README.md`.

## Python Style & Structure
- Target Python 3.8+ syntax compatible with GIMP 3's embedded interpreter.
- Preserve the `#!/usr/bin/env python3` shebang and UTF-8 encoding comment at the top of executable modules.
- Keep `gi.require_version(...)` calls near the top of any module that imports GI bindings, before other GI-related imports.
- Follow the existing docstring convention: triple double-quoted strings that describe purpose and parameters where useful.
- Favor descriptive variable names and guard user-facing operations with robust error handling. When catching broad exceptions, log contextual information with `print` as done elsewhere.
- Use `_()` for any user-visible string so that translations stay discoverable. For formatted strings, call `.format` on the translated text (or use f-strings nested inside `_()` when placeholders are interpolated safely).
- When adding imports, keep standard library first, then third-party, then local modules, mirroring the current ordering.

## UI & Event Patterns
- Create new widgets inside `DreamPrompterUI` and expose them via attributes for event handlers.
- Connect signals in `DreamPrompterEventHandler.connect_all_signals`; avoid wiring callbacks directly in UI builders.
- Whenever UI changes depend on the current editing/generation mode, route logic through `on_mode_changed` so button states, help text, and limits update together.
- Update selection lists (like reference images) through dedicated helpers that sync both internal data (`selected_files`) and visible widgets.

## Threading & Background Work
- Any long-running Gemini or disk operation should run in `dialog_threads.py` using Python threads.
- Use `GLib.idle_add` or `GLib.timeout_add_seconds` to marshal UI updates back to the GTK main loop, as demonstrated in `_generate_image_worker` and `_edit_image_worker`.
- Ensure `_disable_ui`/`_enable_ui` or equivalent guards are invoked around asynchronous calls to keep the interface responsive.

## API Integration Guidelines
- Keep Gemini API surface area confined to `api.py`. New API features should mirror the existing pattern: validate inputs, update progress callbacks, and translate API errors into readable messages.
- Validate file size, MIME type, and count of reference images before sending requests. Add helper routines if new constraints appear.
- Any user-facing warnings or errors from the API layer should be localized through `_()` before presenting them to the UI or logs.

## GIMP Integration Notes
- `integrator.py` owns all interactions with GIMP images and layers. Maintain its utilities for creating new images, adding edit layers, and exporting PNG data.
- Clean up temporary resources (e.g., duplicate images, temp files) in `finally` blocks to avoid leaving artifacts on disk.
- Keep layer naming concise using `textwrap.shorten` so layers are meaningful within GIMP's UI.

## Settings & Persistence
- `settings.py` must support Linux, macOS, and Windows paths. Use `os.path` helpers and guard filesystem operations against permission errors, logging warnings instead of failing hard.
- Mask API keys in the UI by default. Toggling visibility should always flow through the event handler for consistent icon and tooltip updates.

## Internationalization
- Whenever you add or modify strings marked for translation, update the POT template (`scripts/update-pot.py`) and propagate changes to `.po` files (`scripts/update-translations.py`). Regenerate compiled catalogs with `scripts/build-translations.py` as needed.
- Embedded markup (e.g., `<small>` tags) should remain inside translated strings so language-specific grammar can be preserved. Keep markup minimal and well-formed.

## Documentation Assets
- Store reference imagery in `screenshots/` and link from Markdown using relative paths. Keep the README aligned with any UI or workflow changes.

When adding new modules or assets, extend this document with any additional conventions they require.
