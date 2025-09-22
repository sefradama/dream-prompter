# Replicate Migration Plan

This plan mirrors the actionable steps tracked in `REPLICATE_IMPLEMENTATION_PLAN.md` while recording overall migration progress.

## Checklist
- [x] Rename `GeminiAPI` to `ReplicateAPI` and update docstrings and module header comments to describe Replicate usage.
- [x] Continue migrating the API layer and dependent modules to Replicate per the detailed implementation plan.
  - Incorporate the Replicate Python client requirements from `replicate-python_README.md`, including initializing `replicate.Client` instances with `REPLICATE_API_TOKEN` from the environment instead of storing tokens in source.
  - Update API-layer tasks to work with the 1.0 `FileOutput` objects returned by `replicate.run()`/prediction calls by reading or streaming the file handles (`output.read()`, iteration) when converting responses to `GdkPixbuf` data.
  - Ensure downstream modules (thread workers, UI messaging) reflect Replicate terminology and the new request/response flow, including progress messaging for waiting on predictions and any download/stream handling required for `FileOutput` objects.
- [x] Remove remaining Google-specific imports and defaults from `api.py` so Replicate callers must supply a model version instead of relying on the Nano Banana fallback.
- [ ] Update thread worker initialization to source the model version from UI/settings selections instead of a hard-coded fallback.
