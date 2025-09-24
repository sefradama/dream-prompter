#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Replicate image generation integration for Dream Prompter."""

import base64
import binascii
import io
import mimetypes
import os
import time
from collections.abc import Iterable
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib import error as urlerror
from urllib import request as urlrequest

from gi.repository import GdkPixbuf, Gimp

import integrator
from constants import (
    ENV_TOKEN_VAR,
    MAX_DOWNLOAD_SIZE_MB,
    MAX_FILE_SIZE_MB,
    MAX_REFERENCE_IMAGES_EDIT,
    MAX_REFERENCE_IMAGES_GENERATE,
    PROGRESS_COMPLETE,
    PROGRESS_DOWNLOAD,
    PROGRESS_PREPARE,
    PROGRESS_PROCESS,
    PROGRESS_UPLOAD,
    SUPPORTED_MIME_TYPES,
    TRUSTED_DOMAINS,
    VALIDATION_CHUNK_SIZE,
    VALIDATION_HEADER_SIZE,
    VALIDATION_MAX_CHUNKS,
)
from i18n import _

try:
    import replicate
    from replicate.exceptions import ReplicateError

    REPLICATE_AVAILABLE = True
except ImportError:
    replicate = None  # type: ignore[assignment]
    ReplicateError = RuntimeError  # type: ignore[assignment]
    REPLICATE_AVAILABLE = False

    print("\n" + "=" * 60)
    print("⚠️  DREAM PROMPTER SETUP REQUIRED")
    print("=" * 60)
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
    print("    python -m pip install replicate")
    print("")
    print("After installation, restart GIMP and try again.")
    print("=" * 60 + "\n")


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
                    "Replicate API token not provided. Set the field or export {env_var}.",
                ).format(env_var=ENV_TOKEN_VAR),
            )

        self.api_key = resolved_key
        self.model_version = model_version.strip() if model_version else ""

        try:
            self.client = (
                replicate.Client(api_token=self.api_key) if replicate else None
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Replicate client: {e}") from e

    def edit_image(
        self,
        image: Gimp.Image,
        prompt: str,
        reference_images: Optional[List[str]] = None,
        output_format: Optional[str] = None,
        progress_callback: Optional[Callable[[str, Optional[float]], bool]] = None,
        stream_callback: Optional[Callable[[str], bool]] = None,
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
            stream_callback (callable, optional): Streaming callback function for real-time updates.
                Called with (message: str). Should return True to continue, False to cancel.

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
            _("Preparing current image for Replicate..."),
            PROGRESS_PREPARE,
        ):
            return None, _("Operation cancelled")

        try:
            current_image_data = integrator.export_current_region_to_bytes(image)
            if not current_image_data:
                return None, _("Failed to export current image")

            if progress_callback and not progress_callback(
                _("Building Replicate edit request..."),
                PROGRESS_UPLOAD,
            ):
                return None, _("Operation cancelled")

            payload: Dict[str, Any] = {
                "prompt": prompt.strip(),
                "image": self._create_file_handle(
                    current_image_data,
                    "dream-prompter-edit.png",
                ),
            }

            # Set output_format if specified
            if output_format:
                payload["output_format"] = output_format
            # Default output_format to png for qwen-image-edit to avoid webp format
            # which is not supported by GdkPixbuf
            elif self.model_version == "qwen/qwen-image-edit":
                payload["output_format"] = "png"

            self._add_reference_images(
                payload,
                reference_images,
                MAX_REFERENCE_IMAGES_EDIT,
            )

            if progress_callback and not progress_callback(
                _("Queueing Replicate edit prediction..."),
                PROGRESS_PROCESS,
            ):
                return None, _("Operation cancelled")

            def status_callback(message: str) -> bool:
                """Stream status updates to UI"""
                if stream_callback:
                    return stream_callback(message)
                return True

            response = self._run_streaming_prediction(payload, status_callback)

            if progress_callback and not progress_callback(
                _("Collecting Replicate edit output..."),
                PROGRESS_DOWNLOAD,
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
        extra_params: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[str, Optional[float]], bool]] = None,
        stream_callback: Optional[Callable[[str], bool]] = None,
    ) -> Tuple[Optional[GdkPixbuf.Pixbuf], Optional[str]]:
        """
        Generate a new image from a text prompt using Replicate.

        Args:
            prompt (str): Text description of the image to generate
            reference_images (list, optional): List of image file paths for reference (max 3)
            progress_callback (callable, optional): Progress callback function.
                Called with (message: str, percentage: float | None).
                Should return True to continue, False to cancel.
            stream_callback (callable, optional): Streaming callback function for real-time updates.
                Called with (message: str). Should return True to continue, False to cancel.

        Returns:
            tuple: (GdkPixbuf.Pixbuf | None, str | None)
                - If successful: (pixbuf, None)
                - If failed: (None, error_message)
                - If cancelled: (None, "Operation cancelled")
        """
        if not self.client:
            return None, _("Replicate API client is not available")

        if progress_callback and not progress_callback(
            _("Preparing Replicate generation request..."),
            PROGRESS_PREPARE,
        ):
            return None, _("Operation cancelled")

        try:
            payload: Dict[str, Any] = {"prompt": prompt.strip()}

            # Add extra parameters if provided
            if extra_params:
                payload.update(extra_params)

            self._add_reference_images(
                payload,
                reference_images,
                MAX_REFERENCE_IMAGES_GENERATE,
            )

            if progress_callback and not progress_callback(
                _("Queueing Replicate generation prediction..."),
                PROGRESS_PROCESS,
            ):
                return None, _("Operation cancelled")

            def status_callback(message: str) -> bool:
                """Stream status updates to UI"""
                if stream_callback:
                    return stream_callback(message)
                return True

            response = self._run_streaming_prediction(payload, status_callback)

            if progress_callback and not progress_callback(
                _("Collecting Replicate generation output..."),
                PROGRESS_DOWNLOAD,
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

    def _retry_with_backoff(
        self,
        func: Callable[[], Any],
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        initial_delay: float = 1.0,
    ) -> Any:
        """
        Retry a function with exponential backoff for transient failures.

        Args:
            func: Function to retry
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff multiplier
            initial_delay: Initial delay in seconds

        Returns:
            Result of the function call

        Raises:
            The last exception if all retries fail
        """
        delay = initial_delay

        for attempt in range(max_retries + 1):
            try:
                return func()
            except (ConnectionError, TimeoutError, OSError):
                # Transient network errors
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= backoff_factor
                else:
                    raise
            except ReplicateError as e:
                # Check if it's a rate limit error (429)
                if hasattr(e, "status") and e.status == 429:
                    if attempt < max_retries:
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        raise
                else:
                    # Non-transient error, don't retry
                    raise

    def _run_streaming_prediction(
        self,
        payload: Dict[str, Any],
        status_callback: Callable[[str], bool],
    ) -> Any:
        """
        Run a Replicate prediction with streaming status updates and retry logic.

        Args:
            payload: Input payload for the prediction
            status_callback: Callback for streaming status updates.
                Called with (message: str). Should return True to continue, False to cancel.

        Returns:
            The prediction output or None if failed/cancelled
        """

        def create_prediction():
            prediction = self.client.predictions.create(
                version=self.model_version,
                input=payload,
                stream=True,
            )

            # Stream the prediction status updates
            for event in prediction.stream():
                # Send status updates to UI - different models may send different events
                if hasattr(event, "data") and event.data:
                    if event.data == "starting":
                        if not status_callback(_("Initializing prediction...")):
                            prediction.cancel()
                            return None
                    elif event.data == "processing":
                        if not status_callback(_("Processing image...")):
                            prediction.cancel()
                            return None
                    elif event.data == "succeeded":
                        if not status_callback(_("Prediction completed successfully")):
                            return None

            # Wait for and return the final result
            prediction.wait()
            return prediction.output

        try:
            return self._retry_with_backoff(create_prediction)
        except ReplicateError:
            # Let the caller handle the error
            raise
        except Exception:
            # Let the caller handle the error
            raise

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
        loader = GdkPixbuf.PixbufLoader()
        try:
            loader.write(image_bytes)
            loader.close()

            pixbuf = loader.get_pixbuf()
            return pixbuf

        except Exception as e:
            print(f"Error converting bytes to pixbuf: {e}")
            return None
        finally:
            try:
                loader.close()
            except Exception:
                pass  # Already closed or failed

    def _parse_image_response(
        self,
        response: Any,
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
        self,
        img_path: str,
        max_size_mb: int = MAX_FILE_SIZE_MB,
    ) -> Tuple[Optional[io.BytesIO], bool]:
        """Validate and load a reference image file for Replicate."""

        try:
            file_size = os.path.getsize(img_path)
            max_bytes = max_size_mb * 1024 * 1024
            if file_size > max_bytes:
                print(
                    f"Warning: Image {img_path} is {file_size / (1024 * 1024):.1f} MB, exceeds {max_size_mb} MB limit. Skipping.",
                )
                return None, False

            # Step 1: MIME type validation
            mime_type, encoding = mimetypes.guess_type(img_path)
            if mime_type not in SUPPORTED_MIME_TYPES:
                print(
                    f"Warning: Image {img_path} has unsupported MIME type {mime_type} with encoding {encoding}. Skipping.",
                )
                return None, False

            # Step 2: Stream-based content validation to avoid loading entire file into memory
            if not self._validate_image_file_streaming(img_path):
                print(
                    f"Warning: {img_path} is not a valid image file or contains corrupted data. Skipping.",
                )
                return None, False

            # Step 3: Memory-efficient loading - load file in chunks to avoid memory issues
            try:
                # Load in 1MB chunks to be memory efficient
                image_data = b""
                chunk_size = 1024 * 1024  # 1MB chunks
                with open(img_path, "rb") as img_file:
                    while True:
                        chunk = img_file.read(chunk_size)
                        if not chunk:
                            break
                        image_data += chunk
                        # Safety check: shouldn't exceed size we already validated above
                        if len(image_data) > max_bytes:
                            print("Warning: Image loading exceeded expected size limit")
                            return None, False
            except MemoryError:
                print(f"Warning: Insufficient memory to load image {img_path}")
                return None, False

            handle = self._create_file_handle(
                image_data,
                os.path.basename(img_path) or "reference-image",
            )
            return handle, True

        except Exception as e:
            print(f"Warning: Could not load reference image {img_path}: {e}")
            return None, False

    def _validate_image_file_streaming(self, img_path: str) -> bool:
        """Validate image file without loading entire file into memory.

        Args:
            img_path: Path to the image file to validate

        Returns:
            True if the file is a valid image, False otherwise
        """
        try:
            # Read only the first 64KB to validate image headers
            # This is sufficient for PNG, JPEG, and WebP format detection
            with open(img_path, "rb") as img_file:
                header_data = img_file.read(VALIDATION_HEADER_SIZE)

            if not header_data:
                return False

            # Use a streaming loader to validate the image format and basic structure
            loader = GdkPixbuf.PixbufLoader()
            try:
                loader.write(header_data)

                # Try to get pixbuf info early (may work for headers of some formats)
                try:
                    pixbuf = loader.get_pixbuf()
                    if pixbuf:
                        # We got pixbuf info from header, do basic validation
                        width = pixbuf.get_width()
                        height = pixbuf.get_height()
                        if width <= 0 or height <= 0 or width > 65535 or height > 65535:
                            return False
                        return True
                except Exception:
                    # Header-only validation failed, try partial load
                    pass

                # For formats that need more data, close the loader and try the old method
                # but with a limit to prevent excessive memory usage
            finally:
                try:
                    loader.close()
                except Exception:
                    pass  # Already closed or failed

            # Fallback: read in smaller chunks and validate
            image_data = b""
            chunk_count = 0

            with open(img_path, "rb") as img_file:
                while chunk_count < VALIDATION_MAX_CHUNKS:
                    chunk = img_file.read(VALIDATION_CHUNK_SIZE)
                    if not chunk:
                        break
                    image_data += chunk
                    chunk_count += 1

            # Validate the smaller sample
            return self._validate_image_content(image_data)

        except (OSError, IOError, MemoryError):
            return False

    def _validate_image_content(self, image_bytes: bytes) -> bool:
        """Validate that provided bytes are actually a loadable image.

        Args:
            image_bytes: Raw image file data

        Returns:
            True if the bytes represent a valid image, False otherwise
        """
        if not image_bytes:
            return False

        loader = GdkPixbuf.PixbufLoader()
        try:
            # Attempt to create a pixbuf from the data
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
        finally:
            try:
                loader.close()
            except Exception:
                pass  # Already closed or failed

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

        # Handle FileOutput objects from Replicate library (new client behavior)
        if hasattr(data, "read") and callable(data.read):
            try:
                if hasattr(data, "seek") and callable(data.seek):
                    data.seek(0)
                file_bytes = data.read()
                if isinstance(file_bytes, bytes) and file_bytes:
                    return file_bytes
            except Exception as exc:
                print(f"Warning: Could not read FileOutput object: {exc}")

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

        # Fallback: Check if object has url property (FileOutput objects)
        if hasattr(data, "url") and isinstance(data.url, str):
            image_bytes = self._download_image(data.url)
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

    def _download_image(
        self,
        url: str,
        max_size_bytes: int = MAX_DOWNLOAD_SIZE_MB * 1024 * 1024,
    ) -> Optional[bytes]:
        """Download image bytes from a remote URL with security validation.

        Args:
            url: The URL to download from
            max_size_bytes: Maximum allowed download size (default 50MB)

        Returns:
            Image bytes if successful, None if failed or invalid
        """
        from urllib.parse import urlparse

        # Security: Only allow downloads from trusted replicate domains

        try:
            parsed = urlparse(url)
            if not parsed.scheme or parsed.scheme.lower() not in ("http", "https"):
                print(f"Warning: Invalid URL scheme: {url}")
                return None

            domain = parsed.netloc.lower()
            # Allow main domain and subdomains of trusted domains
            is_trusted = any(
                domain == trusted or domain.endswith("." + trusted)
                for trusted in TRUSTED_DOMAINS
            )

            if not is_trusted:
                print(f"Warning: Attempted download from untrusted domain: {domain}")
                return None

            # Use timeout to prevent hanging connections
            with urlrequest.urlopen(url, timeout=30) as response:
                # Check content type for security
                content_type = response.headers.get("content-type", "").lower()
                if not content_type.startswith("image/"):
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
                        print(
                            f"Warning: Download size exceeded limit ({max_size_bytes} bytes)",
                        )
                        return None

                return downloaded_data

        except (urlerror.URLError, ValueError, OSError) as exc:
            print(f"Warning: Could not download image from {url}: {exc}")
            return None
