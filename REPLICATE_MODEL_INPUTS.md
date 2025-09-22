# Replicate Model Input Reference

The Dream Prompter migration will surface a curated set of Replicate-hosted models.  The table below summarizes the primary input fields exposed by each model's schema so that the API layer, UI, and settings logic can send the correct payloads and offer helpful descriptions to users.  Optional values include the defaults reported by the schema as of May 2024.

## google/nano-banana

Text-to-image and image-to-image generation powered by Google's Nano Banana model.

| Field | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `prompt` | string | Yes | — | Main text instructions for the generation request. |
| `negative_prompt` | string | No | `""` | Additional concepts to avoid; set to an empty string when unused. |
| `image` | file (PNG/JPEG/WebP ≤7 MB) | No | — | Upload when running an edit or reference-guided task. Leave unset for pure text-to-image. |
| `mask` | file (PNG with alpha) | No | — | Transparent regions mark areas eligible for inpainting when editing. |
| `image_strength` | number (0.0–1.0) | No | `1.0` | Governs how much of the original image persists during edits. Lower values allow stronger prompt influence. |
| `num_images` | integer | No | `1` | Number of images to return per prediction. |
| `aspect_ratio` | enum | No | `"1:1"` | Choose among schema-defined ratios such as `"1:1"`, `"16:9"`, or `"3:4"`. |
| `cfg_scale` | number | No | `7.0` | Classifier-free guidance scale controlling prompt adherence. |
| `seed` | integer | No | random | Set for reproducible output; omit to let Replicate randomize. |
| `safety_filter_level` | enum | No | `"medium"` | Adjusts Google's content safety filter; valid values come directly from the schema. |
| `scheduler` | enum | No | `"DDIM"` | Diffusion scheduler selection; expose schema-provided options if surfaced in the UI. |

## bytedance/seedream-4

Diffusion model for high-quality text-to-image and style-conditioned edits.

| Field | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `prompt` | string | Yes | — | Base description for the generated scene. |
| `negative_prompt` | string | No | `""` | Optional text for undesired content. |
| `image` | file | No | — | When supplied, Seedream performs image-to-image guidance using the uploaded photo or reference render. |
| `strength` | number (0.0–1.0) | No | `0.75` | Controls how strongly the uploaded image steers the result (lower values produce bigger changes). |
| `num_inference_steps` | integer | No | `30` | Diffusion steps; higher counts improve detail but increase latency. |
| `guidance_scale` | number | No | `7.5` | Prompt adherence similar to CFG. |
| `seed` | integer | No | random | Deterministic output when set. |
| `sampler` | enum | No | `"k_euler"` | Diffusion sampler selection per schema options. |
| `style_preset` | enum | No | `"general"` | Optional style mode (e.g., cinematic, anime). |
| `highres_fix` | boolean | No | `false` | Enables two-pass generation for larger images; increases processing time. |

## qwen/qwen-image-edit

Image editing model optimized for localized, prompt-driven adjustments.

| Field | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `prompt` | string | Yes | — | Instructions for how to modify the supplied image. |
| `image` | file | Yes | — | Source image to edit; accepts PNG/JPEG/WebP ≤7 MB. |
| `mask` | file | No | — | Optional transparency mask; non-transparent pixels are preserved. |
| `size` | enum | No | `"1024x1024"` | Output resolution selector (`"512x512"`, `"768x768"`, `"1024x1024"`, etc.). |
| `negative_prompt` | string | No | `""` | Concepts to avoid when editing. |
| `reference_image` | file | No | — | Secondary guidance image when the model supports reference style transfer. |
| `reference_strength` | number (0.0–1.0) | No | `0.5` | Weight applied to the reference image when provided. |
| `seed` | integer | No | random | Fix for reproducible edits. |

## jingyunliang/swinir:660d922d33153019e8c263a3bba265de882e7f4f70396546b6c9c8f9d47a021a

SwinIR super-resolution and restoration network for upscaling or denoising images.

| Field | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `image` | file | Yes | — | Input image to upscale or restore. |
| `task_type` | enum | No | `"real_world_sr"` | Task selector such as `"classical_sr"`, `"lightweight_sr"`, `"real_world_sr"`, `"gray_dn"`, or `"jpeg_car"`. |
| `scale` | integer | No | `4` | Upscaling factor (commonly 2, 3, or 4) for super-resolution modes. |
| `noise` | integer | No | `15` | Denoising strength when using the gray/noisy tasks. |
| `jpeg` | integer | No | `40` | JPEG compression quality level when running the artifact removal task. |

## tencentarc/gfpgan:0fbacf7afc6c144e5be9767cff80f25aff23e52b0708f17e20f9879b2f21516c

Face restoration model for cleaning and upscaling portraits.

| Field | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `img` | file | Yes | — | Source image containing faces to enhance. |
| `version` | enum | No | `"1.4"` | Choose GFPGAN weights (e.g., `"1.3"`, `"1.4"`). |
| `scale` | integer | No | `2` | Upscaling factor applied to the restored face crops. |
| `codeformer_weight` | number (0.0–1.0) | No | `0.5` | Blend between GFPGAN (0) and CodeFormer (1) restoration styles. |
| `face_enhance` | boolean | No | `true` | Toggle dedicated facial refinement. |
| `background_enhance` | boolean | No | `true` | Run Real-ESRGAN on the background for sharper context. |
| `bg_upsampler` | enum | No | `"realesrgan"` | Background upsampler selection; typically `"realesrgan"` or `"none"`. |
| `bg_tile` | integer | No | `400` | Tile size for background upscaling to manage GPU memory. |

## Usage Notes

- All models enforce Replicate's 7 MB upload limit per image input; keep reference and mask files within this boundary.
- Binary inputs should be sent as file handles or `io.BytesIO` instances when using the Python client.
- When a field accepts enumerated values, surface those options in the UI so users understand the trade-offs; the schema links above remain the source of truth and should be rechecked if Replicate updates any defaults.

