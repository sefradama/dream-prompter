# Replicate Model Input Reference

The Dream Prompter migration will surface a curated set of Replicate-hosted models.  The table below summarizes the primary input fields exposed by each model's schema so that the API layer, UI, and settings logic can send the correct payloads and offer helpful descriptions to users. *Fields with no default are required, with the exception of seed.*

## google/nano-banana
- API schema: https://replicate.com/google/nano-banana/api/schema

"Conversational image generation & editing, including multi-image fusion & character and style consistency capabilities."

| Field | Type | Default | Description |
|---|---|---:|---|
| `prompt` | string | — | Text description of the image to generate. |
| `image_input` | array of image URIs | `[]` | Input image(s) to transform or use as references (supports multiple). |
| `output_format` | enum | `jpg` | Output image format (`jpg`,`png`). |

---

## bytedance/seedream-4
- API schema: https://replicate.com/bytedance/seedream-4/api/schema

"Unified text-to-image generation and precise single-sentence editing at up to 4K resolution."

| Field | Type | Default | Notes |
|---|---|---:|---|
| `prompt` | string | — | Text prompt for generation. |
| `image_input` | array of image URIs | `[]` | 1–10 images for img2img, single or multi-reference. |
| `size` | enum | `2K` | One of `1K` / `2K` / `4K` / `custom`. |
| `aspect_ratio` | enum | `match_input_image` | Used when `size` ≠ `custom` (`match_input_image`,`1:1`, `4:3`, `3:4`, `16:9`, `9:16`, `3:2`, `2:3`, `21:9`). |
| `width` | integer (1024–4096) | `2048` | Only used when `size='custom'`. |
| `height` | integer (1024–4096) | `2048` | Only used when `size='custom'`. |
| `sequential_image_generation` | enum | `disabled` | `disabled` or `auto` (model may emit a set/sequence). |
| `max_images` | integer (1–15) | `1` | Upper bound when sequential generation is `auto`. Total (inputs+outputs) ≤ 15. |

---

## qwen/qwen-image-edit
- API schema: https://replicate.com/qwen/qwen-image-edit/api/schema

"Use natural language prompts to change anything from specific elements to overall style - even accurately edit text."

| Field | Type | Default | Notes |
|---|---|---:|---|
| `prompt` | string | — | How to edit the given image. |
| `image` | image URI | — | JPEG/PNG/GIF/WebP. |
| `aspect_ratio` | enum | `match_input_image` | Output aspect ratio (`match_input_image`,`1:1`, `4:3`, `3:4`, `16:9`, `9:16`). |
| `go_fast` | boolean | `true` | Enable speed optimizations. |
| `seed` | integer | — | Set for reproducible edits. |
| `output_format` | enum | `webp` | Output format (`webp`, `jpg`, `png`). |
| `output_quality` | integer (0–100) | `95` | Ignored for PNG. |
| `disable_safety_checker` | boolean | `false` | Bypass safety checks. |

---

## jingyunliang/swinir:660d922d33153019e8c263a3bba265de882e7f4f70396546b6c9c8f9d47a021a
- API schema: https://replicate.com/jingyunliang/swinir/api/schema

"State-of-the-art real-world image SR, grayscale/color image denoising & JPEG artifact reduction"

| Field | Type | Default | Notes |
|---|---|---:|---|
| `image` | image URI | — | Input image. |
| `task_type` | enum | `Real-World Image Super-Resolution-Large` | Task selector (`Real-World Image Super-Resolution-Large`, `Real-World Image Super-Resolution-Medium`, `Grayscale Image Denoising`, `Color Image Denoising`, `JPEG Compression Artifact Reduction`). |
| `noise` | integer | `15` | Used by grayscale/color denoising tasks (`15`, `25`, `50`). |
| `jpeg` | integer | `40` | JPEG artifact reduction strength (`10`, `20`, `30`, `40`). |

---

## tencentarc/gfpgan:0fbacf7afc6c144e5be9767cff80f25aff23e52b0708f17e20f9879b2f21516c
- API schema: https://replicate.com/tencentarc/gfpgan/api/schema

"Practical face restoration algorithm for old photos or AI-generated faces."

| Field | Type | Default | Notes |
|---|---|---:|---|
| `img` | image URI | — | Source image with faces. |
| `version` | enum | `v1.4` | Model weights (`v1.3`, `v1.4`). |
| `scale` | number | `2` | Final upsampling factor (valid range not documented). |
