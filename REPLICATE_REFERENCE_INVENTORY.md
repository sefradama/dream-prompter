# Google/Gemini Reference Inventory

This audit lists every occurrence of Google Gemini, Nano Banana, or `google-genai` terminology throughout the repository as of the migration effort. Line numbers come from `nl -ba` snapshots gathered during the search.

## Python Modules

### `api.py`
- L5: Module description references "Google AI image generation".
- L6: Notes implementation using the `google-genai` library.
- L38: Warning string instructs users to install `google-genai`.
- L40: Class named `GeminiAPI`.
- L41: Docstring "Google AI client for image generation and editing".
- L45: Constructor docstring references Gemini initialization.
- L48: Parameter description mentions "Google Gemini API key".
- L51: Raises `ImportError` referencing `google-genai`.
- L55: Error message "Nano Banana API not available. Please install google-genai".
- L71: Method docstring mentions "Nano Banana" edit requests.
- L88: Fallback error message referencing Nano Banana and `google-genai`.
- L93: Progress string "Preparing current image for Nano Banana...".
- L101: Progress string "Building Nano Banana edit request...".
- L118: Progress string "Sending edit request to Nano Banana...".
- L126: Progress string "Processing Nano Banana edit response...".
- L137: Error formatting string "Nano Banana API error".
- L148: Method docstring referencing Nano Banana generation.
- L164: Fallback error message referencing Nano Banana and `google-genai`.
- L166: Progress string "Generating image with Nano Banana...".
- L180: Progress string "Sending request to Nano Banana...".
- L188: Progress string "Processing Nano Banana response...".
- L199: Error formatting string "Nano Banana API error".

### `dialog_threads.py`
- L15: Imports `GeminiAPI` from `api`.
- L79, L110, L149, L198: Type hints describing "Google Gemini API key".
- L158, L211: Instantiates `GeminiAPI`.

### `dialog_events.py`
- L98: Validation error message "Please enter your Google Gemini API key".

### `dialog_gtk.py`
- L184: Section header markup "Google Gemini API Key".
- L191: Placeholder text "Enter your Google Gemini API key...".
- L207: Help text pointing to "Google Cloud Console" for the API key.

### `dialog.py`
- L24: Window title "Dream Prompter - Nano Banana AI Image Creator/Editor".

### `dream-prompter.py`
- L5: Plugin subtitle "Nano Banana GIMP Plugin".
- L6: Description references "Google's Nano Banana (Gemini 2.5 Flash Image)".
- L25: `PLUGIN_DESCRIPTION` string "AI-powered image creation/editing with Nano Banana".
- L43: Registration summary "AI-powered image creation/editing with Nano Banana".
- L44: Registration description referencing "Google's Gemini 2.5 Flash Image model (Nano Banana)".

## Documentation & Guidance

### `README.md`
- L3: Overview references "Google's Nano Banana (Gemini 2.5 Flash Image Preview)".
- L24: Prerequisites mention "Google Gemini API key".
- L29, L109, L116, L120, L123, L126, L155, L156: Installation commands for `google-genai`.
- L131, L273, L275: Troubleshooting notes for missing `google-genai`.
- L146: Instruction to install `google-genai` with GIMP's Python.
- L161: Billing note for "Gemini 2.5 Flash Image Preview (Nano Banana)" and Google Cloud.
- L163, L165: Steps referencing Google AI Studio and Google Cloud billing.
- L171: Model identifier ``gemini-2.5-flash-image-preview`` (Nano Banana).
- L182, L183, L288: Usage tips referencing Google AI Studio/Cloud.
- L264: Module description "Google Gemini API integration".
- L343: Closing statement crediting "Google's Gemini 2.5 Flash Image Preview (Nano Banana)".

### `AGENTS.md`
- L6: Describes the plugin embedding Google's Gemini "Nano Banana" model.
- L16: Notes `api.py` as the Gemini API integration module.
- L39: References long-running Gemini operations.
- L44: Mentions keeping Gemini API surface area confined to `api.py`.

### `REPLICATE_IMPLEMENTATION_PLAN.md`
- L3: Goal describes replacing Google "Nano Banana" (Gemini) integrations.
- L6: Checklist item referencing Google/Gemini.
- L7: Checklist item referencing `google-genai` and Google response shapes.
- L11: Task referencing `GeminiAPI` renaming.
- L12: Task referencing Google-specific imports and Nano Banana progress text.
- L25: Task referencing removal of "Nano Banana" branding.
- L34: Task referencing Google-/Gemini-branded text.
- L54: Task referencing Nano Banana in dialog metadata.
- L59: Task referencing Google-specific setup instructions.
- L60: Task referencing docs/comments mentioning Gemini/Nano Banana.

## Localization Templates

### `locale/dream-prompter.pot`
- L21: "Nano Banana API not available. Please install google-genai".
- L33: "Preparing current image for Nano Banana...".
- L46: "Building Nano Banana edit request...".
- L50: "Sending edit request to Nano Banana...".
- L54: "Processing Nano Banana edit response...".
- L63: "Nano Banana API error: {error}".
- L72: "Generating image with Nano Banana...".
- L76: "Sending request to Nano Banana...".
- L80: "Processing Nano Banana response...".
- L105: "Dream Prompter - Nano Banana AI Image Creator/Editor".
- L109: "Please enter your Google Gemini API key".
- L200: "Google Gemini API Key".
- L204: "Enter your Google Gemini API key...".
- L213: "Get your API key from <a href=\"{url}\">Google Cloud Console</a>".
- L327: "AI-powered image creation/editing with Nano Banana".
- L332-L333: Multi-line description referencing "Google's Gemini 2.5 Flash Image model (Nano Banana)".

## Localized `.po` Files

Each translation file mirrors the Nano Banana and Google Gemini terminology present in the template. The entries below list every affected message (both `msgid` and `msgstr`).

### `locale/bn.po`
- L43-44: "AI-powered image creation/editing with Nano Banana" (msgid/msgstr).
- L59-60: "Building Nano Banana edit request...".
- L91-92: "Dream Prompter - Nano Banana AI Image Creator/Editor".
- L111-112: "Enter your Google Gemini API key...".
- L150-151: "Generating image with Nano Banana...".
- L160-161: Help text for Google Cloud Console API key.
- L164-165: "Google Gemini API Key".
- L189-190: "Nano Banana API error".
- L193-194: "Nano Banana API not available. Please install google-genai".
- L242-243: "Please enter your Google Gemini API key".
- L246-247: "Preparing current image for Nano Banana...".
- L250-251: "Processing Nano Banana edit response...".
- L254-255: "Processing Nano Banana response...".
- L290-291: "Sending edit request to Nano Banana...".
- L294-295: "Sending request to Nano Banana...".
- L311-L315: Multi-line dialog description referencing Google's Gemini 2.5 Nano Banana model.

### `locale/ko.po`
- L43-44: "AI-powered image creation/editing with Nano Banana".
- L59-60: "Building Nano Banana edit request...".
- L93-94: "Dream Prompter - Nano Banana AI Image Creator/Editor".
- L113-114: "Enter your Google Gemini API key...".
- L152-153: "Generating image with Nano Banana...".
- L162-163: Google Cloud Console help text.
- L166-167: "Google Gemini API Key".
- L191-192: "Nano Banana API error".
- L195-196: "Nano Banana API not available. Please install google-genai".
- L244-245: "Please enter your Google Gemini API key".
- L248-249: "Preparing current image for Nano Banana...".
- L252-253: "Processing Nano Banana edit response...".
- L256-257: "Processing Nano Banana response...".
- L292-293: "Sending edit request to Nano Banana...".
- L296-297: "Sending request to Nano Banana...".
- L313-L317: Multi-line description referencing Google's Gemini 2.5 Nano Banana model.

### `locale/ru.po`
- L44-45: "AI-powered image creation/editing with Nano Banana".
- L60-61: "Building Nano Banana edit request...".
- L95-96: "Dream Prompter - Nano Banana AI Image Creator/Editor".
- L115-116: "Enter your Google Gemini API key...".
- L154-155: "Generating image with Nano Banana...".
- L164-165: Google Cloud Console help text.
- L168-169: "Google Gemini API Key".
- L193-194: "Nano Banana API error".
- L197-198: "Nano Banana API not available. Please install google-genai".
- L246-247: "Please enter your Google Gemini API key".
- L250-251: "Preparing current image for Nano Banana...".
- L254-255: "Processing Nano Banana edit response...".
- L258-259: "Processing Nano Banana response...".
- L294-295: "Sending edit request to Nano Banana...".
- L298-299: "Sending request to Nano Banana...".
- L315-L320: Multi-line description referencing Google's Gemini 2.5 Nano Banana model.

### `locale/pt.po`
- L43-44: "AI-powered image creation/editing with Nano Banana".
- L59-60: "Building Nano Banana edit request...".
- L94-95: "Dream Prompter - Nano Banana AI Image Creator/Editor".
- L114-115: "Enter your Google Gemini API key...".
- L153-154: "Generating image with Nano Banana...".
- L163-164: Google Cloud Console help text.
- L167-168: "Google Gemini API Key".
- L192-193: "Nano Banana API error".
- L196-197: "Nano Banana API not available. Please install google-genai".
- L245-246: "Please enter your Google Gemini API key".
- L249-250: "Preparing current image for Nano Banana...".
- L253-254: "Processing Nano Banana edit response...".
- L257-258: "Processing Nano Banana response...".
- L293-294: "Sending edit request to Nano Banana...".
- L297-298: "Sending request to Nano Banana...".
- L314-L319: Multi-line description referencing Google's Gemini 2.5 Nano Banana model.

### `locale/fr.po`
- L43-44: "AI-powered image creation/editing with Nano Banana".
- L59-60: "Building Nano Banana edit request...".
- L94-95: "Dream Prompter - Nano Banana AI Image Creator/Editor".
- L114-115: "Enter your Google Gemini API key...".
- L153-154: "Generating image with Nano Banana...".
- L163, L165: Google Cloud Console help text (split across lines).
- L168-169: "Google Gemini API Key".
- L193-194: "Nano Banana API error".
- L197-198: "Nano Banana API not available. Please install google-genai".
- L246-247: "Please enter your Google Gemini API key".
- L250-251: "Preparing current image for Nano Banana...".
- L254-255: "Processing Nano Banana edit response...".
- L258-259: "Processing Nano Banana response...".
- L294-295: "Sending edit request to Nano Banana...".
- L298-299: "Sending request to Nano Banana...".
- L315-L320: Multi-line description referencing Google's Gemini 2.5 Nano Banana model.

### `locale/es.po`
- L43-44: "AI-powered image creation/editing with Nano Banana".
- L59-60: "Building Nano Banana edit request...".
- L94-95: "Dream Prompter - Nano Banana AI Image Creator/Editor".
- L114-115: "Enter your Google Gemini API key...".
- L153-154: "Generating image with Nano Banana...".
- L163-164: Google Cloud Console help text.
- L167-168: "Google Gemini API Key".
- L192-193: "Nano Banana API error".
- L196-197: "Nano Banana API not available. Please install google-genai".
- L245-246: "Please enter your Google Gemini API key".
- L249-250: "Preparing current image for Nano Banana...".
- L253-254: "Processing Nano Banana edit response...".
- L257-258: "Processing Nano Banana response...".
- L293-294: "Sending edit request to Nano Banana...".
- L297-298: "Sending request to Nano Banana...".
- L314-L319: Multi-line description referencing Google's Gemini 2.5 Nano Banana model.

### `locale/hi.po`
- L43-44: "AI-powered image creation/editing with Nano Banana".
- L59-60: "Building Nano Banana edit request...".
- L91-92: "Dream Prompter - Nano Banana AI Image Creator/Editor".
- L111-112: "Enter your Google Gemini API key...".
- L150-151: "Generating image with Nano Banana...".
- L160-161: Google Cloud Console help text.
- L164-165: "Google Gemini API Key".
- L189-190: "Nano Banana API error".
- L193-194: "Nano Banana API not available. Please install google-genai".
- L242-243: "Please enter your Google Gemini API key".
- L246-247: "Preparing current image for Nano Banana...".
- L250-251: "Processing Nano Banana edit response...".
- L254-255: "Processing Nano Banana response...".
- L290-291: "Sending edit request to Nano Banana...".
- L294-295: "Sending request to Nano Banana...".
- L311-L315: Multi-line description referencing Google's Gemini 2.5 Nano Banana model.

### `locale/zh_TW.po`
- L43-44: "AI-powered image creation/editing with Nano Banana".
- L59-60: "Building Nano Banana edit request...".
- L90-91: "Dream Prompter - Nano Banana AI Image Creator/Editor".
- L110-111: "Enter your Google Gemini API key...".
- L149-150: "Generating image with Nano Banana...".
- L159-160: Google Cloud Console help text.
- L163-164: "Google Gemini API Key".
- L188-189: "Nano Banana API error".
- L192-193: "Nano Banana API not available. Please install google-genai".
- L241-242: "Please enter your Google Gemini API key".
- L245-246: "Preparing current image for Nano Banana...".
- L249-250: "Processing Nano Banana edit response...".
- L253-254: "Processing Nano Banana response...".
- L289-290: "Sending edit request to Nano Banana...".
- L293-294: "Sending request to Nano Banana...".
- L310-L314: Multi-line description referencing Google's Gemini 2.5 Nano Banana model.

### `locale/zh_CN.po`
- L43-44: "AI-powered image creation/editing with Nano Banana".
- L59-60: "Building Nano Banana edit request...".
- L90-91: "Dream Prompter - Nano Banana AI Image Creator/Editor".
- L110-111: "Enter your Google Gemini API key...".
- L149-150: "Generating image with Nano Banana...".
- L159-160: Google Cloud Console help text.
- L163-164: "Google Gemini API Key".
- L188-189: "Nano Banana API error".
- L192-193: "Nano Banana API not available. Please install google-genai".
- L241-242: "Please enter your Google Gemini API key".
- L245-246: "Preparing current image for Nano Banana...".
- L249-250: "Processing Nano Banana edit response...".
- L253-254: "Processing Nano Banana response...".
- L289-290: "Sending edit request to Nano Banana...".
- L293-294: "Sending request to Nano Banana...".
- L310-L314: Multi-line description referencing Google's Gemini 2.5 Nano Banana model.

### `locale/ja.po`
- L43-44: "AI-powered image creation/editing with Nano Banana".
- L59-60: "Building Nano Banana edit request...".
- L93-94: "Dream Prompter - Nano Banana AI Image Creator/Editor".
- L113-114: "Enter your Google Gemini API key...".
- L152-153: "Generating image with Nano Banana...".
- L162, L164: Google Cloud Console help text (split across lines).
- L167-168: "Google Gemini API Key".
- L192-193: "Nano Banana API error".
- L196, L198: "Nano Banana API not available. Please install google-genai" (split lines).
- L246-247: "Please enter your Google Gemini API key".
- L250-251: "Preparing current image for Nano Banana...".
- L254-255: "Processing Nano Banana edit response...".
- L258-259: "Processing Nano Banana response...".
- L294-295: "Sending edit request to Nano Banana...".
- L298-299: "Sending request to Nano Banana...".
- L315-L319: Multi-line description referencing Google's Gemini 2.5 Nano Banana model.

## Summary

The inventory above confirms that Google Gemini/Nano Banana terminology and `google-genai` references span core Python modules, documentation, contributor guidance, and every localization artifact. These findings will guide subsequent replacement work during the Replicate migration.
