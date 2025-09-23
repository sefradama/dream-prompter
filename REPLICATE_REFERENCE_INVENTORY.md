# Replicate Terminology Inventory

This inventory tracks the current state of user-facing messaging after migrating off the legacy Nano Banana stack. Each section confirms that strings, documentation, and translations now reference Replicate concepts exclusively.

## Python Modules
- `api.py` progress messages, errors, and validation strings refer to the Replicate client, Replicate predictions, and Replicate responses.
- `dialog_events.py` validation prompts require a "Replicate API token" and report "Initializing Replicate request..." when work begins.
- `dialog_gtk.py` labels the credentials section "Replicate API Token", provides the placeholder "Enter your Replicate API token...", and links to `replicate.com/account/api-tokens` for setup help.
- `dialog.py` and `dream-prompter.py` title and describe the plug-in as a Replicate-powered image creator/editor.

## Documentation & Contributor Guidance
- `README.md` documents Replicate prerequisites, token management, billing considerations, and model selection.
- `AGENTS.md` describes embedding Replicate-hosted models, constraining Replicate API usage to `api.py`, and running long-running Replicate operations in the threading helpers.
- `REPLICATE_IMPLEMENTATION_PLAN.md` and related planning docs now refer to Replicate deliverables without calling out Gemini migration gaps.

## Localization Templates
- `locale/dream-prompter.pot` includes only Replicate-flavoured strings (e.g., "Replicate API not available. Please install the replicate package.", "Enter your Replicate API token...", "Transform existing images... using Replicate-hosted models...").

## Localized `.po` Files
- All translated strings across `locale/*.po` mirror the Replicate terminology found in the template, including the token label, placeholder text, validation prompts, progress messages, and the long-form plug-in description.
- Obsolete entries containing legacy Gemini wording have been removed so translation catalogs no longer ship historical Nano Banana messaging.

This audit confirms there are no remaining Gemini or `google-genai` references in active code, documentation, or translation resources.
