#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Replicate image generation integration for Dream Prompter."""

import base64
import binascii
import io
import mimetypes
import os
from collections.abc import Iterable
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib import error as urlerror
from urllib import request as urlrequest

from gi.repository import GdkPixbuf, Gimp

import integrator
from i18n import _

MAX_FILE_SIZE_MB = 7
MAX_REFERENCE_IMAGES_EDIT = 2
MAX_REFERENCE_IMAGES_GENERATE = 3
PROGRESS_COMPLETE = 1.0
PROGRESS_DOWNLOAD = 0.9
PROGRESS_PREPARE = 0.1
PROGRESS_PROCESS = 0.7
PROGRESS_UPLOAD = 0.5
SUPPORTED_MIME_TYPES = ["image/png", "image/jpeg", "image/webp"]
ENV_TOKEN_VAR = "REPLICATE_API_TOKEN"

try:
    import replicate
    from replicate.exceptions import ReplicateError

    REPLICATE_AVAILABLE = True
except ImportError as import_error:
    replicate = None  # type: ignore[assignment]
    ReplicateError = RuntimeError  # type: ignore[assignment]
    REPLICATE_AVAILABLE = False

    print("\n" + "="*60)
    print("⚠️  DREAM PROMPTER SETUP REQUIRED")
    print("="*60)
    print("The 'replicate' package is not installed.")
    print("")
    print("To fix this issue, run one of the following commands:")
    print("")
    print("  For system-wide installation:")
    print("    pip install replicate")
    print("")
    print("  For user-specific installation:")
    print("    pip install --user replicate")
    print("")
    print("  Or with specific Python version:")
    print(f"    python -m pip install replicate")
    print("")
    print("After installation, restart GIMP and try again.")
    print("="*60 + "\n")


class ReplicateAPI:
    """Replicate client for image generation and editing operations."""

    def __init__(self, api_key: str, model_version: str) -> None:
        """Initialize the Replicate API client."""

        if not REPLICATE_AVAILABLE:
            raise ImportError(
                _("Replicate API not available. Please install the replicate package.")
            )

        resolved_key = (
            api_key.strip()
            if api_key and api_key.strip()
            else os.getenv(ENV_TOKEN_VAR, "").strip()
        )
        if not resolved_key:
            raise ValueError(
                _(
                    "Replicate API token not provided. Set the field or export {env_var}."
                ).format(env_var=ENV_TOKEN_VAR)
            )

        self.api_key = resolved_key
        self.model_version = model_version.strip() if model_version else ""

        self.client = replicate.Client(api_token=self.api_key) if replicate else None

    def edit_image(
        self,
        image: Gimp.Image,
        prompt: str,
        reference_images: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[str, Optional[float]], bool]] = None,
    ) -> Tuple[Optional[GdkPixbuf.Pixbuf], Optional[str]]:
        """
        Edit an image from a text prompt using Replicate.

        Args:
            image (Gimp.Image): Image to edit
            prompt (str): Text description of the edits to make
            reference_images (list, optional): List of image file paths for reference (max 2)
            progress_callback (callable, optional): Progress callback function.
                Called with (message: str, percentage: float | None).
                Should return True to continue, False to cancel.

        Returns:
            tuple: (GdkPixbuf.Pixbuf | None, str | None)
                - If successful: (pixbuf, None)
                - If failed: (None, error_message)
                - If cancelled: (None, "Operation cancelled")
        """
        if not self.client:
            return None, _("Replicate API client is not available")

        if not image:
            return None, _("No GIMP image provided for editing")

        if progress_callback and not progress_callback(
            _("Preparing current image for Replicate..."), PROGRESS_PREPARE
        ):
            return None, _("Operation cancelled")

        try:
            current_image_data = integrator.export_current_region_to_bytes(image)
            if not current_image_data:
                return None, _("Failed to export current image")

            if progress_callback and not progress_callback(
                _("Building Replicate edit request..."), PROGRESS_UPLOAD
            ):
                return None, _("Operation cancelled")

            payload: Dict[str, Any] = {
                "prompt": prompt.strip(),
                "image": self._create_file_handle(
                    current_image_data, "dream-prompter-edit.png"
                ),
            }
            self._add_reference_images(
                payload, reference_images, MAX_REFERENCE_IMAGES_EDIT
            )

            if progress_callback and not progress_callback(
                _("Queueing Replicate edit prediction..."), PROGRESS_PROCESS
            ):
                return None, _("Operation cancelled")

            response = self.client.run(self.model_version, input=payload)

            if progress_callback and not progress_callback(
                _("Collecting Replicate edit output..."), PROGRESS_DOWNLOAD
            ):
                return None, _("Operation cancelled")

            pixbuf, error_msg = self._parse_image_response(response)

            if progress_callback and pixbuf:
                progress_callback(_("Image editing complete!"), PROGRESS_COMPLETE)

            return pixbuf, error_msg

        except ReplicateError as e:
            return None, _("Replicate API error: {error}").format(error=str(e))
        except Exception as e:
            return None, _("Unexpected error: {error}").format(error=str(e))

    def generate_image(
        self,
        prompt: str,
        reference_images: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[str, Optional[float]], bool]] = None,
    ) -> Tuple[Optional[GdkPixbuf.Pixbuf], Optional[str]]:
        """
        Generate a new image from a text prompt using Replicate.

        Args:
            prompt (str): Text description of the image to generate
            reference_images (list, optional): List of image file paths for reference (max 3)
            progress_callback (callable, optional): Progress callback function.
                Called with (message: str, percentage: float | None).
                Should return True to continue, False to cancel.

        Returns:
            tuple: (GdkPixbuf.Pixbuf | None, str | None)
                - If successful: (pixbuf, None)
                - If failed: (None, error_message)
                - If cancelled: (None, "Operation cancelled")
        """
        if not self.client:
            return None, _("Replicate API client is not available")

        if progress_callback and not progress_callback(
            _("Preparing Replicate generation request..."), PROGRESS_PREPARE
        ):
            return None, _("Operation cancelled")

        try:
            payload: Dict[str, Any] = {"prompt": prompt.strip()}
            self._add_reference_images(
                payload, reference_images, MAX_REFERENCE_IMAGES_GENERATE
            )

            if progress_callback and not progress_callback(
                _("Queueing Replicate generation prediction..."), PROGRESS_PROCESS
            ):
                return None, _("Operation cancelled")

            response = self.client.run(self.model_version, input=payload)

            if progress_callback and not progress_callback(
                _("Collecting Replicate generation output..."), PROGRESS_DOWNLOAD
            ):
                return None, _("Operation cancelled")

            pixbuf, error_msg = self._parse_image_response(response)

            if progress_callback and pixbuf:
                progress_callback(_("Image generation complete!"), PROGRESS_COMPLETE)

            return pixbuf, error_msg

        except ReplicateError as e:
            return None, _("Replicate API error: {error}").format(error=str(e))
        except Exception as e:
            return None, _("Unexpected error: {error}").format(error=str(e))

    def _add_reference_images(
        self,
        payload: Dict[str, Any],
        reference_images: Optional[List[str]],
        max_count: int,
    ) -> None:
        """Attach validated reference images to the Replicate payload."""

        if not reference_images:
            return

        handles: List[io.BytesIO] = []
        for img_path in reference_images[:max_count]:
            image_handle, success = self._validate_reference_image(img_path)
            if success and image_handle:
                handles.append(image_handle)

        if handles:
            payload["image_input"] = handles

    def _bytes_to_pixbuf(self, image_bytes: bytes) -> Optional[GdkPixbuf.Pixbuf]:
        """
        Convert image bytes to GdkPixbuf

        Args:
            image_bytes (bytes): Image data

        Returns:
            GdkPixbuf.Pixbuf: Pixbuf object, or None if conversion failed
        """
        try:
            loader = GdkPixbuf.PixbufLoader()
            loader.write(image_bytes)
            loader.close()

            pixbuf = loader.get_pixbuf()
            return pixbuf

        except Exception as e:
            print(f"Error converting bytes to pixbuf: {e}")
            return None

    def _parse_image_response(
        self, response: Any
    ) -> Tuple[Optional[GdkPixbuf.Pixbuf], Optional[str]]:
        """Parse Replicate response payloads into a ``GdkPixbuf``."""

        image_bytes = self._extract_image_bytes(response)
        if not image_bytes:
            return None, _("No image data found in Replicate response")

        pixbuf = self._bytes_to_pixbuf(image_bytes)
        if pixbuf:
            return pixbuf, None

        return None, _("Failed to decode image data from Replicate response")

    def _validate_reference_image(
        self, img_path: str, max_size_mb: int = MAX_FILE_SIZE_MB
    ) -> Tuple[Optional[io.BytesIO], bool]:
        """Validate and load a reference image file for Replicate."""

        try:
            file_size = os.path.getsize(img_path)
            if file_size > max_size_mb * 1024 * 1024:
                print(
                    f"Warning: Image {img_path} is {file_size / (1024 * 1024):.1f} MB, exceeds {max_size_mb} MB limit. Skipping."
                )
                return None, False

            with open(img_path, "rb") as img_file:
                image_data = img_file.read()

            # Step 1: MIME type validation
            mime_type, encoding = mimetypes.guess_type(img_path)
            if mime_type not in SUPPORTED_MIME_TYPES:
                print(
                    f"Warning: Image {img_path} has unsupported MIME type {mime_type} with encoding {encoding}. Skipping."
                )
                return None, False

            # Step 2: Content validation - attempt to load as actual image
            # This prevents uploading files with fake extensions or malicious content
            if not self._validate_image_content(image_data):
                print(
                    f"Warning: {img_path} is not a valid image file or contains corrupted data. Skipping."
                )
                return None, False

            handle = self._create_file_handle(
                image_data, os.path.basename(img_path) or "reference-image"
            )
            return handle, True

        except Exception as e:
            print(f"Warning: Could not load reference image {img_path}: {e}")
            return None, False

    def _validate_image_content(self, image_bytes: bytes) -> bool:
        """Validate that provided bytes are actually a loadable image.

        Args:
            image_bytes: Raw image file data

        Returns:
            True if the bytes represent a valid image, False otherwise
        """
        if not image_bytes:
            return False

        try:
            # Attempt to create a pixbuf from the data
            loader = GdkPixbuf.PixbufLoader()
            loader.write(image_bytes)
            loader.close()

            pixbuf = loader.get_pixbuf()
            if pixbuf is None:
                return False

            # Verify basic image properties (must have dimensions)
            width = pixbuf.get_width()
            height = pixbuf.get_height()

            if width <= 0 or height <= 0 or width > 65535 or height > 65535:
                return False

            return True

        except Exception:
            return False

    def _create_file_handle(self, image_bytes: bytes, name: str) -> io.BytesIO:
        """Wrap image bytes in a file-like buffer compatible with Replicate SDK."""

        handle = io.BytesIO(image_bytes)
        handle.name = name
        handle.seek(0)
        return handle

    def _extract_image_bytes(self, data: Any) -> Optional[bytes]:
        """Extract image bytes from Replicate responses of varying shapes."""

        if data is None:
            return None

        if isinstance(data, bytes):
            return data

        if isinstance(data, str):
            if data.startswith("http://") or data.startswith("https://"):
                return self._download_image(data)

            _, _, encoded = data.partition(",")
            candidate = encoded or data

            # Security: Validate base64 input before decoding
            try:
                # Check for reasonable size limits (base64 is ~33% larger than binary)
                # Limit to ~100MB of decoded data max
                if len(candidate) > 134217728:  # ~100MB * 4/3
                    print("Warning: Base64 input too large for safe decoding")
                    return None

                decoded_bytes = base64.b64decode(candidate)
                # Final safety check on decoded size
                if len(decoded_bytes) > 104857600:  # 100MB limit
                    print("Warning: Decoded base64 data exceeds size limit")
                    return None

                return decoded_bytes
            except (binascii.Error, ValueError, MemoryError) as e:
                print(f"Warning: Base64 decode failed: {e}")
                return None

        if hasattr(data, "read") and callable(data.read):
            try:
                if hasattr(data, "seek") and callable(data.seek):
                    data.seek(0)
                file_bytes = data.read()
                if file_bytes:
                    return file_bytes
            except Exception as exc:
                print(f"Warning: Could not read file-like response: {exc}")

        if hasattr(data, "url") and isinstance(getattr(data, "url"), str):
            image_bytes = self._download_image(getattr(data, "url"))
            if image_bytes:
                return image_bytes

        if isinstance(data, dict):
            for key in ("image", "output", "result", "url", "uri", "data", "urls"):
                if key in data:
                    image_bytes = self._extract_image_bytes(data[key])
                    if image_bytes:
                        return image_bytes

        if isinstance(data, (list, tuple)):
            for item in data:
                image_bytes = self._extract_image_bytes(item)
                if image_bytes:
                    return image_bytes

        if isinstance(data, Iterable):
            for item in data:
                image_bytes = self._extract_image_bytes(item)
                if image_bytes:
                    return image_bytes

        return None

    def _download_image(self, url: str, max_size_bytes: int = 50 * 1024 * 1024) -> Optional[bytes]:
        """Download image bytes from a remote URL with security validation.

        Args:
            url: The URL to download from
            max_size_bytes: Maximum allowed download size (default 50MB)

        Returns:
            Image bytes if successful, None if failed or invalid
        """
        from urllib.parse import urlparse

        # Security: Only allow downloads from trusted replicate domains
        TRUSTED_DOMAINS = {"replicate.com", "replicate.ai", "api.replicate.com"}

        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.scheme.lower() in ("http", "https"):
                print(f"Warning: Invalid URL scheme: {url}")
                return None

            domain = parsed.netloc.lower()
            # Allow main domain and subdomains of trusted domains
            is_trusted = any(domain == trusted or domain.endswith("." + trusted)
                           for trusted in TRUSTED_DOMAINS)

            if not is_trusted:
                print(f"Warning: Attempted download from untrusted domain: {domain}")
                return None

            # Use timeout to prevent hanging connections
            with urlrequest.urlopen(url, timeout=30) as response:
                # Check content type for security
                content_type = response.headers.get('content-type', '').lower()
                if not content_type.startswith('image/'):
                    print(f"Warning: Non-image content-type: {content_type}")
                    return None

                # Stream download with size limit to prevent memory exhaustion
                downloaded_data = b""
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    downloaded_data += chunk
                    if len(downloaded_data) > max_size_bytes:
                        print(f"Warning: Download size exceeded limit ({max_size_bytes} bytes)")
                        return None

                return downloaded_data

        except (urlerror.URLError, ValueError, OSError) as exc:
            print(f"Warning: Could not download image from {url}: {exc}")
            return None
