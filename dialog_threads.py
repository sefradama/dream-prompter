#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Threading operations for Dream Prompter dialog
Handles all background AI processing and image operations
"""

import threading
from typing import Any, Callable, Dict, List, Optional

from gi.repository import GdkPixbuf, GLib

import integrator
from api import ReplicateAPI
from dialog_gtk import DreamPrompterUI
from i18n import _


class ThreadSafeState:
    """Thread-safe wrapper for shared state variables"""

    def __init__(self):
        self._lock = threading.Lock()
        self._processing = False
        self._cancel_requested = False

    def set_processing(self, value: bool) -> None:
        """Thread-safe set processing state"""
        with self._lock:
            self._processing = value

    def is_processing(self) -> bool:
        """Thread-safe get processing state"""
        with self._lock:
            return self._processing

    def request_cancel(self) -> None:
        """Thread-safe cancel request"""
        with self._lock:
            self._cancel_requested = True

    def is_cancel_requested(self) -> bool:
        """Thread-safe check cancel state"""
        with self._lock:
            return self._cancel_requested

    def reset_cancel(self) -> None:
        """Thread-safe reset cancel state"""
        with self._lock:
            self._cancel_requested = False

    def can_start_processing(self) -> bool:
        """Thread-safe check if processing can start"""
        with self._lock:
            return not self._processing and not self._cancel_requested


class DreamPrompterThreads:
    """Handles all background threading operations"""

    def __init__(
        self, ui: DreamPrompterUI, image: Optional[Any], drawable: Optional[Any],
    ) -> None:
        """
        Initialize thread manager

        Args:
            ui: The UI controller instance
            image: GIMP image object (optional for generation mode)
            drawable: GIMP drawable object (optional for generation mode)

        Raises:
            ValueError: If ui is None
        """
        if not ui:
            raise ValueError("UI object is required")

        self.ui = ui
        self.image = image
        self.drawable = drawable
        self._state = ThreadSafeState()
        self._callbacks: Dict[str, Callable] = {}
        self._current_thread: Optional[threading.Thread] = None
        self._thread_lock = threading.Lock()

        self._model_version: Optional[str] = None

    def cancel_processing(self) -> None:
        """Request cancellation of current processing"""
        self._state.request_cancel()
        self.ui.update_status(_("Cancelling..."))

    def is_processing(self) -> bool:
        """Check if image processing is currently running"""
        return self._state.is_processing()

    def set_callbacks(self, callbacks: Dict[str, Callable]) -> None:
        """
        Set callback functions for thread completion

        Args:
            callbacks: Dictionary containing 'on_success' and/or 'on_error' callbacks

        Raises:
            ValueError: If callbacks is not a dictionary
        """
        if not isinstance(callbacks, dict):
            raise ValueError("Callbacks must be a dictionary")

        valid_keys = {"on_success", "on_error"}
        for key in callbacks:
            if key not in valid_keys:
                raise ValueError(
                    f"Invalid callback key: {key}. Valid keys: {valid_keys}",
                )

        self._callbacks = callbacks

    def _normalize_model_version(self, model_version: Optional[str]) -> str:
        """Return a sanitized model version string if available."""

        if model_version:
            normalized = model_version.strip()
            if normalized:
                return normalized

        if self._model_version:
            previous = self._model_version.strip()
            if previous:
                return previous

        return ""

    def start_generate_thread(
        self,
        api_key: str,
        prompt: str,
        reference_images: Optional[List[str]] = None,
        model_version: Optional[str] = None,
    ) -> None:
        """
        Start image generation in background thread

        Args:
            api_key: Replicate API token
            prompt: Text prompt for image generation
            reference_images: Optional list of reference image paths
        """
        if not self.ui or not self._state.can_start_processing():
            return

        if not api_key or not api_key.strip():
            self._handle_error(_("Replicate API token is required"))
            return

        if not prompt or not prompt.strip():
            self._handle_error(_("Prompt is required"))
            return

        resolved_model = self._normalize_model_version(model_version)
        if not resolved_model:
            self._handle_error(_("Replicate model version is required"))
            return

        self._model_version = resolved_model

        self._state.set_processing(True)
        self._state.reset_cancel()
        self.ui.set_ui_enabled(False)

        with self._thread_lock:
            self._current_thread = threading.Thread(
                target=self._generate_image_worker,
                args=(api_key, prompt, resolved_model, reference_images or []),
            )
            self._current_thread.daemon = True
            self._current_thread.start()

    def start_edit_thread(
        self,
        api_key: str,
        prompt: str,
        reference_images: Optional[List[str]] = None,
        model_version: Optional[str] = None,
    ) -> None:
        """
        Start image editing in background thread

        Args:
            api_key: Replicate API token
            prompt: Text prompt for image editing
            reference_images: Optional list of reference image paths
        """
        if not self.ui or not self._state.can_start_processing():
            return

        if not self.drawable:
            self._handle_error(_("No layer available for editing"))
            return

        if not self.image:
            self._handle_error(_("No image available for editing"))
            return

        if not api_key or not api_key.strip():
            self._handle_error(_("Replicate API token is required"))
            return

        if not prompt or not prompt.strip():
            self._handle_error(_("Prompt is required"))
            return

        resolved_model = self._normalize_model_version(model_version)
        if not resolved_model:
            self._handle_error(_("Replicate model version is required"))
            return

        self._model_version = resolved_model

        self._state.set_processing(True)
        self._state.reset_cancel()
        self.ui.set_ui_enabled(False)

        with self._thread_lock:
            self._current_thread = threading.Thread(
                target=self._edit_image_worker,
                args=(api_key, prompt, resolved_model, reference_images or []),
            )
            self._current_thread.daemon = True
            self._current_thread.start()

    def _generate_image_worker(
        self,
        api_key: str,
        prompt: str,
        model_version: str,
        reference_images: List[str],
    ) -> None:
        """
        Generate image in background thread

        Args:
            api_key: Replicate API token
            prompt: Text prompt for image generation
            model_version: Replicate model version identifier to use
            reference_images: List of reference image paths
        """
        try:
            if self._state.is_cancel_requested():
                GLib.idle_add(self._handle_cancelled)
                return

            api = ReplicateAPI(api_key, model_version)

            def progress_callback(
                message: str, percentage: Optional[float] = None
            ) -> bool:
                """Progress callback for API operations"""
                if self._state.is_cancel_requested():
                    return False
                try:
                    GLib.idle_add(self.ui.update_status, message, percentage)
                except Exception as e:
                    # UI may be destroyed, silently ignore
                    print(f"Warning: Unable to update UI status: {e}")
                    return False
                return True

            def stream_callback(message: str) -> bool:
                """Stream status callback for real-time updates"""
                if self._state.is_cancel_requested():
                    return False
                try:
                    GLib.idle_add(self.ui.update_status, message)
                except Exception as e:
                    # UI may be destroyed, silently ignore
                    print(f"Warning: Unable to update UI status: {e}")
                    return False
                return True

            pixbuf, error_msg = api.generate_image(
                prompt=prompt,
                reference_images=reference_images,
                progress_callback=progress_callback,
                stream_callback=stream_callback,
            )

            if self._state.is_cancel_requested():
                GLib.idle_add(self._handle_cancelled)
                return

            if error_msg:
                GLib.idle_add(self._handle_error, error_msg)
                return

            if not pixbuf:
                GLib.idle_add(self._handle_error, _("No image data received from API"))
                return

            GLib.idle_add(self._handle_generated_image, pixbuf, prompt)

        except ImportError:
            # Missing dependencies (replicate package) - user actionable
            GLib.idle_add(
                self._handle_error,
                _(
                    "Missing required package. Please install replicate: pip install replicate",
                ),
            )
        except (ValueError, TypeError) as e:
            # Data validation errors - likely user input issues
            GLib.idle_add(
                self._handle_error,
                _("Invalid input data: {error}").format(error=str(e)),
            )
        except (ConnectionError, TimeoutError) as e:
            # Network issues - transient problems
            GLib.idle_add(
                self._handle_error,
                _("Connection failed. Check your internet and API key: {error}").format(
                    error=str(e),
                ),
            )
        except Exception as e:
            # Unexpected errors - technical issues
            error_msg = _("Unexpected error during image generation: {error}").format(
                error=str(e),
            )
            GLib.idle_add(self._handle_error, error_msg)

    def _edit_image_worker(
        self,
        api_key: str,
        prompt: str,
        model_version: str,
        reference_images: List[str],
    ) -> None:
        """
        Edit image in background thread

        Args:
            api_key: Replicate API token
            prompt: Text prompt for image editing
            model_version: Replicate model version identifier to use
            reference_images: List of reference image paths
        """
        try:
            if self._state.is_cancel_requested():
                GLib.idle_add(self._handle_cancelled)
                return

            if not self.image:
                GLib.idle_add(self._handle_error, _("No image available for editing"))
                return

            api = ReplicateAPI(api_key, model_version)

            def progress_callback(
                message: str, percentage: Optional[float] = None,
            ) -> bool:
                """Progress callback for API operations"""
                if self._state.is_cancel_requested():
                    return False
                try:
                    GLib.idle_add(self.ui.update_status, message, percentage)
                except Exception as e:
                    # UI may be destroyed, silently ignore
                    print(f"Warning: Unable to update UI status: {e}")
                    return False
                return True

            def stream_callback(message: str) -> bool:
                """Stream status callback for real-time updates"""
                if self._state.is_cancel_requested():
                    return False
                try:
                    GLib.idle_add(self.ui.update_status, message)
                except Exception as e:
                    # UI may be destroyed, silently ignore
                    print(f"Warning: Unable to update UI status: {e}")
                    return False
                return True

            pixbuf, error_msg = api.edit_image(
                image=self.image,
                prompt=prompt,
                reference_images=reference_images,
                progress_callback=progress_callback,
                stream_callback=stream_callback,
            )

            if self._state.is_cancel_requested():
                GLib.idle_add(self._handle_cancelled)
                return

            if error_msg:
                GLib.idle_add(self._handle_error, error_msg)
                return

            if not pixbuf:
                GLib.idle_add(self._handle_error, _("No image data received from API"))
                return

            layer_name = self._generate_layer_name(prompt)
            GLib.idle_add(self._handle_edited_image, pixbuf, layer_name)

        except ImportError:
            # Missing dependencies (replicate package) - user actionable
            GLib.idle_add(
                self._handle_error,
                _(
                    "Missing required package. Please install replicate: pip install replicate",
                ),
            )
        except (ValueError, TypeError) as e:
            # Data validation errors - likely user input issues
            GLib.idle_add(
                self._handle_error,
                _("Invalid input data: {error}").format(error=str(e)),
            )
        except (ConnectionError, TimeoutError) as e:
            # Network issues - transient problems
            GLib.idle_add(
                self._handle_error,
                _("Connection failed. Check your internet and API key: {error}").format(
                    error=str(e),
                ),
            )
        except Exception as e:
            # Unexpected errors - technical issues
            error_msg = _("Unexpected error during image editing: {error}").format(
                error=str(e),
            )
            GLib.idle_add(self._handle_error, error_msg)

    def _generate_layer_name(self, prompt: str) -> str:
        """
        Generate a name for the new layer

        Args:
            prompt: The AI prompt used for generation

        Returns:
            A descriptive name for the new layer
        """
        if self.drawable and prompt:
            original_name = self.drawable.get_name()
            truncated_prompt = prompt[:30] + "..." if len(prompt) > 30 else prompt
            return _("{original} (AI Edit: {prompt})").format(
                original=original_name, prompt=truncated_prompt,
            )
        if prompt:
            truncated_prompt = prompt[:30] + "..." if len(prompt) > 30 else prompt
            return _("AI Generated: {prompt}").format(prompt=truncated_prompt)
        return _("AI Layer")

    def _handle_cancelled(self) -> None:
        """Handle cancelled operation"""
        self._state.set_processing(False)
        with self._thread_lock:
            self._current_thread = None
        self.ui.update_status(_("Operation cancelled"))
        self.ui.set_ui_enabled(True)

    def _handle_error(self, error_message: str) -> None:
        """
        Handle error during processing

        Args:
            error_message: The error message to display
        """
        self._state.set_processing(False)
        with self._thread_lock:
            self._current_thread = None
        self.ui.set_ui_enabled(True)

        if self._callbacks.get("on_error"):
            self._callbacks["on_error"](error_message)

    def _handle_generated_image(self, pixbuf: GdkPixbuf.Pixbuf, prompt: str) -> None:
        """
        Handle generated image on main thread

        Args:
            pixbuf: The generated image data
            prompt: The prompt used for generation
        """
        try:
            self.ui.update_status(_("Creating GIMP image..."), 0.9)

            image = integrator.create_new_image(pixbuf, prompt)
            if not image:
                self._handle_error(_("Failed to create GIMP image"))
                return

            self.ui.update_status(_("Image generated successfully!"), 1.0)
            self._handle_success()

        except Exception as e:
            error_msg = _("Error creating GIMP image: {error}").format(error=str(e))
            self._handle_error(error_msg)

    def _handle_edited_image(self, pixbuf: GdkPixbuf.Pixbuf, layer_name: str) -> None:
        """
        Handle edited image on main thread

        Args:
            pixbuf: The edited image data
            layer_name: Name for the new layer
        """
        try:
            self.ui.update_status(_("Adding edit layer..."), 0.9)

            layer = integrator.create_edit_layer(
                self.image, self.drawable, pixbuf, layer_name,
            )
            if not layer:
                self._handle_error(_("Failed to create edit layer"))
                return

            self.ui.update_status(_("Edit layer created!"), 1.0)
            self._handle_success()

        except Exception as e:
            error_msg = _("Error creating edit layer: {error}").format(error=str(e))
            self._handle_error(error_msg)

    def _handle_success(self) -> None:
        """Handle successful processing"""
        self._state.set_processing(False)
        with self._thread_lock:
            self._current_thread = None
        self.ui.set_ui_enabled(True)

        if self._callbacks.get("on_success"):
            self._callbacks["on_success"]()
