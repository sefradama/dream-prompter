# Replicate Migration Implementation Plan

> Goal: Replace all Google "Nano Banana" (Gemini) integrations with Replicate so the plugin exclusively uses Replicate-hosted image models with a user-selectable model choice.

## 1. Preliminary Cleanup & Inventory
- [x] Search for and list every Google/Gemini reference across the codebase (Python modules, README, translations) to ensure no strings or imports remain after migration. (See `REPLICATE_REFERENCE_INVENTORY.md` for the full inventory.)
- [x] Verify there are no hidden runtime dependencies on `google-genai` (e.g., error handling specific to Google response shapes) before reworking the API layer.
  - Confirmed `api.py` is the only module importing `google.genai`; downstream modules interact solely with `GeminiAPI`'s `(pixbuf, error_message)` contract.
  - Reviewed `dialog_threads.py`, `dialog_events.py`, `dialog.py`, and `dream-prompter.py` to ensure they only depend on generic status strings and the high-level API interface.
  - Audited support utilities (`integrator.py`, `settings.py`, GTK builders) to verify they manipulate `GdkPixbuf` data without touching Google-specific response objects or exceptions.
- [x] Initial Replicate models to expose: `google/nano-banana`, `bytedance/seedream-4`, `qwen/qwen-image-edit`, `jingyunliang/swinir:660d922d33153019e8c263a3bba265de882e7f4f70396546b6c9c8f9d47a021a`, `tencentarc/gfpgan:0fbacf7afc6c144e5be9767cff80f25aff23e52b0708f17e20f9879b2f21516c`. Documented expected input fields for each schema in `REPLICATE_MODEL_INPUTS.md` so the API and UI layers know which payload keys, types, and defaults to honor when wiring up Replicate requests.

## 2. API Layer Replacement (`api.py`)
- [x] Rename `GeminiAPI` to `ReplicateAPI` and update docstrings and module header comments to describe Replicate usage.
- [x] Remove Google-specific imports (`google.genai` packages) and constants that only apply to Nano Banana (e.g., progress messages with "Nano Banana").
- [x] Add `import replicate` and handle optional dependency messaging (warn if the library is missing with install instructions for `replicate`).
- [x] Initialize a Replicate client via `replicate.Client(api_token=api_key)` inside `__init__`, storing the token for future requests.
- [x] Extend the constructor to accept a `model_version` (full Replicate identifier like `owner/model:version_hash`) so we can route both generation and editing to the user-selected model.
- [x] Update `generate_image`:
  - [x] Build the Replicate input payload (at minimum `{"prompt": prompt}`) and attach reference images by opening each file and passing `io.BytesIO` handles when the selected model supports them.
  - [x] Call the API using either `self.client.run(model_version, input=payload)` or `self.client.predictions.create` depending on synchronous needs; parse streaming/batch output to obtain binary image data (Replicate typically returns a list of URLs or binary data).
  - [x] Download or decode the returned image(s); if URLs are provided, use `requests` (already vendored?) or `urllib.request` to fetch the image bytes before loading them into a `GdkPixbuf`.
  - [x] Preserve reference image validation (`_validate_reference_image`) but generalize MIME/type checks if Replicate has different limits (retain 7MB/PNG-JPEG-WebP unless the chosen models demand changes).
- [x] Update `edit_image` to send the current GIMP layer as an input image where the selected Replicate model supports image-to-image operations:
  - [x] Export the current layer to PNG bytes (`integrator.export_gimp_image_to_bytes` already does this).
  - [x] Feed that into the payload (`{"prompt": prompt, "image": BytesIO(...)}`) alongside optional reference images if accepted by the chosen model.
- [x] Replace `_parse_image_response` logic with Replicate-specific parsing (their responses may be lists of URLs, base64 strings, or file handles); loop through outputs until a usable image byte sequence is found and convert to `GdkPixbuf` as before.
- [x] Update progress callback messaging to remove "Nano Banana" branding and reflect Replicate steps (e.g., "Queueing Replicate job", "Waiting for prediction", "Downloading result").

## 3. Threading Layer Updates (`dialog_threads.py`)
- [x] Update imports to reference `ReplicateAPI` and thread worker instantiations to pass the selected `model_version` from the UI/settings.
- [x] Propagate model selection through `start_generate_thread`/`start_edit_thread` so that `_generate_image_worker` and `_edit_image_worker` call `ReplicateAPI(api_key, model_version)`.
- [x] Enhance progress handling to include waiting/streaming statuses specific to Replicate predictions (e.g., handle polling if using `predictions.create`).
- [x] Adjust error handling so that Replicate-specific errors (HTTP errors, `replicate.exceptions.ReplicateError`) are surfaced cleanly to the UI.

## 4. UI Adjustments (`dialog_gtk.py`)
- [x] Replace all Google-/Gemini-branded text with Replicate terminology (section headers, placeholders, help text).
- [x] Update the API key help link to point to Replicate token instructions (https://replicate.com/account/api-tokens).
- [x] Insert a new "Model" selection row beneath the API key section:
  - [x] Use `Gtk.ComboBoxText` populated from a shared constant list (e.g., defined in `dialog_gtk.py` or a new config module) that maps friendly labels to Replicate model version identifiers.
  - [x] Provide a short descriptive label or tooltip for each model (e.g., "Flux Dev – photorealistic text-to-image").
- [x] Ensure new widgets are exposed via `DreamPrompterUI` attributes so the event handler can read/write the selected model.

## 5. Event Handling & State Management (`dialog_events.py`)
- [x] Load and store the selected model version alongside the API key when persisting settings.
- [x] Update validation messages to reference Replicate (e.g., "Please enter your Replicate API token").
- [x] Initialize the model combo box selection from stored settings or default to a sensible option.
- [x] Pass the chosen model version into the thread launcher methods.

## 6. Settings Persistence (`settings.py`)
- [x] Extend stored JSON structure with a `model_version` field (defaulting to the preferred Replicate model) and migrate existing configs gracefully (handle missing key by injecting default when loading older files).
- [ ] Keep existing permissions logic; ensure new field respects cross-platform path handling.

## 7. Dialog Metadata (`dialog.py` & `dream-prompter.py`)
- [x] Update window titles, descriptions, and registration metadata to describe Replicate usage instead of Nano Banana.
- [ ] Update plugin documentation strings (`procedure.set_documentation`, `PLUGIN_DESCRIPTION`) to reflect new capabilities and mention that users can pick from multiple Replicate models.

## 8. Documentation
- [x] Rewrite `README.md` sections (features, prerequisites, installation, API key acquisition) to reference Replicate, including instructions to install the `replicate` Python package and to create tokens on replicate.com.
- [x] Remove Google-specific setup instructions and replace screenshots/notes if necessary.
- [x] Update any other docs or comments referencing Gemini/Nano Banana.

## 9. Dependency Audit
- [x] Ensure `google-genai` is no longer mentioned in installation or optional dependencies; add guidance for installing `replicate` (and any additional libraries needed for HTTP downloads like `requests` if used).

## 10. QA & Verification
- [ ] Manual smoke test generation mode with at least one supported Replicate model to confirm predictions complete and layers are created.
- [ ] Manual smoke test edit mode (if supported) using a model that accepts image inputs.
- [ ] Verify reference image validation still works and gracefully skips oversized/unsupported files.
- [ ] Confirm configuration persistence (API token, model choice, prompt visibility) across plugin restarts on at least one platform.
- [ ] Review UI layout to ensure the new model selector does not break dialog sizing.
- [ ] Finalize by running `ruff format .` and `ruff check .` to satisfy linting/formatting requirements (no other automated tests per instructions).
