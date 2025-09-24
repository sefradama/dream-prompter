#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Model configuration UI components for Dream Prompter
Handles API key input and model selection
"""

import abc
import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk  # noqa: E402

from i18n import _  # noqa: E402
from ui_interfaces import IModelConfig  # noqa: E402

REPLICATE_MODEL_OPTIONS = [
    (
        "google/nano-banana",
        _(
            "Nano Banana",
        ),
    ),
    (
        "bytedance/seedream-4",
        _(
            "Seedream 4.0",
        ),
    ),
    (
        "qwen/qwen-image-edit-plus",
        _(
            "Qwen Image Edit Plus",
        ),
    ),
    (
        "jingyunliang/swinir:660d922d33153019e8c263a3bba265de882e7f4f70396546b6c9c8f9d47a021a",
        _(
            "SwinIR",
        ),
    ),
    (
        "tencentarc/gfpgan:0fbacf7afc6c144e5be9767cff80f25aff23e52b0708f17e20f9879b2f21516c",
        _(
            "GFPGAN",
        ),
    ),
]


class ModelConfigStrategy(abc.ABC):
    """Abstract base class for model configuration strategies"""

    def __init__(self):
        self.current_mode = "generate"  # or "edit"

    @abc.abstractmethod
    def create_params_ui(self, model_params_box):
        """Create and add parameter UI elements to the model_params_box"""
        pass

    @abc.abstractmethod
    def get_parameters(self):
        """Get relevant model-specific parameters as a dictionary"""
        pass

    @abc.abstractmethod
    def set_mode(self, mode):
        """Set the current mode (generate or edit) for parameter visibility"""
        self.current_mode = mode.lower()

    @abc.abstractmethod
    def get_output_format(self):
        """Get the selected output format, or None if not applicable"""
        pass


class ModelRegistry:
    """Registry for model configuration strategies"""

    _strategies = {}

    @classmethod
    def register(cls, model_id, strategy_class):
        """Register a strategy class for a model ID"""
        cls._strategies[model_id] = strategy_class

    @classmethod
    def get_strategy(cls, model_id):
        """Get the strategy class for a model ID"""
        return cls._strategies.get(model_id)


class GoogleNanoBananaStrategy(ModelConfigStrategy):
    """Strategy for Google Nano Banana model"""

    def __init__(self):
        super().__init__()
        self.output_format_combo = None

    def create_params_ui(self, model_params_box):
        """Create parameters for Google Nano Banana"""
        # Output format
        format_label = Gtk.Label(_("Output Format:"))
        format_label.set_halign(Gtk.Align.START)

        format_combo = Gtk.ComboBoxText()
        format_combo.set_tooltip_text(_("Select output image format"))
        format_combo.append("jpg", _("JPEG"))
        format_combo.append("png", _("PNG"))
        format_combo.set_active_id("jpg")

        format_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        format_row.pack_start(format_label, False, False, 0)
        format_row.pack_start(format_combo, True, True, 0)

        self.output_format_combo = format_combo
        model_params_box.pack_start(format_row, False, False, 0)

    def get_parameters(self):
        """Get parameters for Google Nano Banana"""
        params = {}
        if self.output_format_combo:
            params["output_format"] = self.output_format_combo.get_active_id()
        return params

    def set_mode(self, mode):
        """Set mode (no effect for this model)"""
        super().set_mode(mode)

    def get_output_format(self):
        """Get output format"""
        return (
            self.output_format_combo.get_active_id()
            if self.output_format_combo
            else None
        )


class BytedanceSeedreamStrategy(ModelConfigStrategy):
    """Strategy for Bytedance SeeDream 4 model"""

    def __init__(self):
        super().__init__()
        self.size_combo = None
        self.aspect_ratio_combo = None
        self.width_spin = None
        self.height_spin = None
        self.sequential_gen_combo = None
        self.max_images_spin = None
        self.aspect_ratio_row = None
        self.custom_size_row = None
        self.max_images_row = None

    def create_params_ui(self, model_params_box):
        """Create parameters for Bytedance SeeDream 4"""

        # Size
        size_label = Gtk.Label(_("Size:"))
        size_label.set_halign(Gtk.Align.START)

        size_combo = Gtk.ComboBoxText()
        size_combo.set_tooltip_text(_("Select image size preset"))
        size_combo.append("1K", _("1K"))
        size_combo.append("2K", _("2K"))
        size_combo.append("4K", _("4K"))
        size_combo.append("custom", _("Custom"))
        size_combo.set_active_id("2K")

        size_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        size_row.pack_start(size_label, False, False, 0)
        size_row.pack_start(size_combo, True, True, 0)

        self.size_combo = size_combo
        size_combo.connect("changed", self._on_size_combo_changed)
        model_params_box.pack_start(size_row, False, False, 0)

        # Aspect ratio
        aspect_label = Gtk.Label(_("Aspect Ratio:"))
        aspect_label.set_halign(Gtk.Align.START)

        aspect_combo = Gtk.ComboBoxText()
        aspect_combo.set_tooltip_text(_("Select aspect ratio"))
        aspect_combo.append("match_input_image", _("Match Input Image"))
        aspect_combo.append("1:1", _("1:1"))
        aspect_combo.append("4:3", _("4:3"))
        aspect_combo.append("3:4", _("3:4"))
        aspect_combo.append("16:9", _("16:9"))
        aspect_combo.append("9:16", _("9:16"))
        aspect_combo.append("3:2", _("3:2"))
        aspect_combo.append("2:3", _("2:3"))
        aspect_combo.append("21:9", _("21:9"))
        aspect_combo.set_active_id("match_input_image")

        aspect_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        aspect_row.pack_start(aspect_label, False, False, 0)
        aspect_row.pack_start(aspect_combo, True, True, 0)

        self.aspect_ratio_combo = aspect_combo
        self.aspect_ratio_row = aspect_row
        model_params_box.pack_start(aspect_row, False, False, 0)

        # Custom size controls
        self.width_spin = Gtk.SpinButton()
        self.width_spin.set_range(1024, 4096)
        self.width_spin.set_increments(64, 256)
        self.width_spin.set_value(2048)
        self.width_spin.set_tooltip_text(_("Width (1024-4096)"))

        self.height_spin = Gtk.SpinButton()
        self.height_spin.set_range(1024, 4096)
        self.height_spin.set_increments(64, 256)
        self.height_spin.set_value(2048)
        self.height_spin.set_tooltip_text(_("Height (1024-4096)"))

        size_label_custom = Gtk.Label(_("Custom Size:"))
        size_label_custom.set_halign(Gtk.Align.START)

        size_row_custom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        size_row_custom.pack_start(size_label_custom, False, False, 0)
        size_row_custom.pack_start(Gtk.Label("W:"), False, False, 0)
        size_row_custom.pack_start(self.width_spin, False, False, 0)
        size_row_custom.pack_start(Gtk.Label("H:"), False, False, 0)
        size_row_custom.pack_start(self.height_spin, False, False, 0)
        size_row_custom.pack_start(Gtk.Label(""), True, True, 0)

        self.custom_size_row = size_row_custom
        model_params_box.pack_start(size_row_custom, False, False, 0)

        # Sequential generation
        seq_label = Gtk.Label(_("Sequential Generation:"))
        seq_label.set_halign(Gtk.Align.START)

        seq_combo = Gtk.ComboBoxText()
        seq_combo.set_tooltip_text(_("Enable sequential image generation"))
        seq_combo.append("disabled", _("Disabled"))
        seq_combo.append("auto", _("Auto"))
        seq_combo.set_active_id("disabled")

        seq_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        seq_row.pack_start(seq_label, False, False, 0)
        seq_row.pack_start(seq_combo, True, True, 0)

        self.sequential_gen_combo = seq_combo
        seq_combo.connect("changed", self._on_sequential_gen_changed)
        model_params_box.pack_start(seq_row, False, False, 0)

        # Max images
        max_images_label = Gtk.Label(_("Max Images:"))
        max_images_label.set_halign(Gtk.Align.START)

        max_images_spin = Gtk.SpinButton()
        max_images_spin.set_range(1, 15)
        max_images_spin.set_increments(1, 3)
        max_images_spin.set_value(1)
        max_images_spin.set_tooltip_text(_("Maximum images to generate (1-15)"))

        max_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        max_row.pack_start(max_images_label, False, False, 0)
        max_row.pack_start(max_images_spin, False, False, 0)
        max_row.pack_start(Gtk.Label(""), True, True, 0)

        self.max_images_spin = max_images_spin
        self.max_images_row = max_row
        model_params_box.pack_start(max_row, False, False, 0)

        # Apply initial visibility
        self._apply_initial_visibility()

    def _on_size_combo_changed(self, combo):
        """Show/hide custom size controls and aspect ratio based on size selection"""
        is_custom = combo.get_active_id() == "custom"
        if self.custom_size_row:
            self.custom_size_row.set_visible(is_custom)
        if self.aspect_ratio_row:
            self.aspect_ratio_row.set_visible(not is_custom)

    def _on_sequential_gen_changed(self, combo):
        """Show/hide max images control based on sequential generation selection"""
        if combo.get_active_id() == "auto":
            if self.max_images_row:
                self.max_images_row.set_visible(True)
        else:
            if self.max_images_row:
                self.max_images_row.set_visible(False)

    def _apply_initial_visibility(self):
        """Apply initial conditional visibility"""
        if self.size_combo:
            is_custom = self.size_combo.get_active_id() == "custom"
            if self.custom_size_row:
                self.custom_size_row.set_visible(is_custom)
            if self.aspect_ratio_row:
                self.aspect_ratio_row.set_visible(not is_custom)
        if self.sequential_gen_combo:
            if self.max_images_row:
                self.max_images_row.set_visible(
                    self.sequential_gen_combo.get_active_id() == "auto"
                )

    def get_parameters(self):
        """Get parameters for Bytedance SeeDream 4"""
        params = {}
        if self.size_combo:
            params["size"] = self.size_combo.get_active_id()
        # aspect_ratio only sent when size != custom
        if (
            self.aspect_ratio_combo
            and self.size_combo
            and self.size_combo.get_active_id() != "custom"
        ):
            params["aspect_ratio"] = self.aspect_ratio_combo.get_active_id()
        # width/height only sent when size = custom
        if self.size_combo and self.size_combo.get_active_id() == "custom":
            if self.width_spin:
                params["width"] = int(self.width_spin.get_value())
            if self.height_spin:
                params["height"] = int(self.height_spin.get_value())
        if self.sequential_gen_combo:
            params["sequential_image_generation"] = (
                self.sequential_gen_combo.get_active_id()
            )
        # max_images only sent when sequential_generation = auto
        if (
            self.max_images_spin
            and self.sequential_gen_combo
            and self.sequential_gen_combo.get_active_id() == "auto"
        ):
            params["max_images"] = int(self.max_images_spin.get_value())
        return params

    def set_mode(self, mode):
        """Set mode"""
        super().set_mode(mode)
        # Re-create UI if mode changes (but since strategy is recreated, this is handled in create_params_ui)

    def get_output_format(self):
        """No output format for this model"""
        return None


class QwenImageEditStrategy(ModelConfigStrategy):
    """Strategy for Qwen Image Edit model"""

    def __init__(self):
        super().__init__()
        self.qwen_aspect_ratio_combo = None
        self.go_fast_check = None
        self.seed_spin = None
        self.output_format_combo = None
        self.output_quality_spin = None
        self.disable_safety_check = None
        self.quality_row = None

    def create_params_ui(self, model_params_box):
        """Create parameters for Qwen Image Edit"""
        # Aspect ratio (only shown in edit mode)
        if self.current_mode == "edit":
            aspect_label = Gtk.Label(_("Aspect Ratio:"))
            aspect_label.set_halign(Gtk.Align.START)

            aspect_combo = Gtk.ComboBoxText()
            aspect_combo.set_tooltip_text(_("Select output aspect ratio"))
            aspect_combo.append("match_input_image", _("Match Input Image"))
            aspect_combo.append("1:1", _("1:1"))
            aspect_combo.append("4:3", _("4:3"))
            aspect_combo.append("3:4", _("3:4"))
            aspect_combo.append("16:9", _("16:9"))
            aspect_combo.append("9:16", _("9:16"))
            aspect_combo.set_active_id("match_input_image")

            aspect_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            aspect_row.pack_start(aspect_label, False, False, 0)
            aspect_row.pack_start(aspect_combo, True, True, 0)

            self.qwen_aspect_ratio_combo = aspect_combo
            model_params_box.pack_start(aspect_row, False, False, 0)

        # Go fast
        go_fast_check = Gtk.CheckButton(_("Go Fast (Speed Optimization)"))
        go_fast_check.set_active(True)
        go_fast_check.set_tooltip_text(_("Enable speed optimizations"))

        self.go_fast_check = go_fast_check
        model_params_box.pack_start(go_fast_check, False, False, 0)

        # Seed
        seed_label = Gtk.Label(_("Seed (optional):"))
        seed_label.set_halign(Gtk.Align.START)

        seed_spin = Gtk.SpinButton()
        seed_spin.set_range(0, 999999999)
        seed_spin.set_increments(1, 1000)
        seed_spin.set_value(0)
        seed_spin.set_tooltip_text(_("Set for reproducible edits (0 = random)"))

        seed_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        seed_row.pack_start(seed_label, False, False, 0)
        seed_row.pack_start(seed_spin, False, False, 0)
        seed_row.pack_start(Gtk.Label(""), True, True, 0)

        self.seed_spin = seed_spin
        model_params_box.pack_start(seed_row, False, False, 0)

        # Output format
        format_label = Gtk.Label(_("Output Format:"))
        format_label.set_halign(Gtk.Align.START)

        format_combo = Gtk.ComboBoxText()
        format_combo.set_tooltip_text(_("Select output image format"))
        format_combo.append("png", _("PNG"))
        format_combo.append("jpg", _("JPEG"))
        format_combo.set_active_id("png")

        format_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        format_row.pack_start(format_label, False, False, 0)
        format_row.pack_start(format_combo, True, True, 0)

        self.output_format_combo = format_combo
        format_combo.connect("changed", self._on_output_format_changed)
        model_params_box.pack_start(format_row, False, False, 0)

        # Output quality
        quality_label = Gtk.Label(_("Output Quality:"))
        quality_label.set_halign(Gtk.Align.START)

        quality_spin = Gtk.SpinButton()
        quality_spin.set_range(0, 100)
        quality_spin.set_increments(1, 10)
        quality_spin.set_value(95)
        quality_spin.set_tooltip_text(_("Quality for JPEG (0-100, ignored for PNG)"))

        quality_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        quality_row.pack_start(quality_label, False, False, 0)
        quality_row.pack_start(quality_spin, False, False, 0)
        quality_row.pack_start(Gtk.Label(""), True, True, 0)

        self.output_quality_spin = quality_spin
        self.quality_row = quality_row
        model_params_box.pack_start(quality_row, False, False, 0)

        # Disable safety checker
        safety_check = Gtk.CheckButton(_("Disable Safety Checker"))
        safety_check.set_active(False)
        safety_check.set_tooltip_text(_("Bypass safety checks"))

        self.disable_safety_check = safety_check
        model_params_box.pack_start(safety_check, False, False, 0)

        # Apply initial visibility
        self._apply_initial_visibility()

    def _on_output_format_changed(self, combo):
        """Show/hide output quality based on format selection"""
        if combo.get_active_id() == "jpg":
            if self.quality_row:
                self.quality_row.set_visible(True)
        else:
            if self.quality_row:
                self.quality_row.set_visible(False)

    def _apply_initial_visibility(self):
        """Apply initial conditional visibility"""
        if self.output_format_combo:
            if self.quality_row:
                self.quality_row.set_visible(
                    self.output_format_combo.get_active_id() == "jpg"
                )

    def get_parameters(self):
        """Get parameters for Qwen Image Edit"""
        params = {}
        # aspect_ratio is model-specific for editing (only shown in edit mode)
        if self.qwen_aspect_ratio_combo and self.current_mode == "edit":
            params["aspect_ratio"] = self.qwen_aspect_ratio_combo.get_active_id()
        if self.go_fast_check:
            params["go_fast"] = self.go_fast_check.get_active()
        if self.seed_spin and self.seed_spin.get_value() != 0:
            params["seed"] = int(self.seed_spin.get_value())
        if self.output_format_combo:
            params["output_format"] = self.output_format_combo.get_active_id()
        # output_quality only sent when format is jpg
        if (
            self.output_quality_spin
            and self.output_format_combo
            and self.output_format_combo.get_active_id() == "jpg"
        ):
            params["output_quality"] = int(self.output_quality_spin.get_value())
        if self.disable_safety_check:
            params["disable_safety_checker"] = self.disable_safety_check.get_active()
        return params

    def set_mode(self, mode):
        """Set mode"""
        super().set_mode(mode)
        # Note: aspect_ratio visibility is handled in create_params_ui

    def get_output_format(self):
        """Get output format"""
        return (
            self.output_format_combo.get_active_id()
            if self.output_format_combo
            else None
        )


class SwinirStrategy(ModelConfigStrategy):
    """Strategy for SwinIR model"""

    def __init__(self):
        super().__init__()
        self.task_type_combo = None
        self.noise_spin = None
        self.jpeg_spin = None
        self.noise_row = None
        self.jpeg_row = None

    def create_params_ui(self, model_params_box):
        """Create parameters for SwinIR"""
        # Task type
        task_label = Gtk.Label(_("Task Type:"))
        task_label.set_halign(Gtk.Align.START)

        task_combo = Gtk.ComboBoxText()
        task_combo.set_tooltip_text(_("Select image processing task"))
        task_combo.append(
            "Real-World Image Super-Resolution-Large", _("Super-Resolution Large")
        )
        task_combo.append(
            "Real-World Image Super-Resolution-Medium", _("Super-Resolution Medium")
        )
        task_combo.append("Grayscale Image Denoising", _("Grayscale Denoising"))
        task_combo.append("Color Image Denoising", _("Color Denoising"))
        task_combo.append(
            "JPEG Compression Artifact Reduction", _("JPEG Artifact Reduction")
        )
        task_combo.set_active_id("Real-World Image Super-Resolution-Large")

        task_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        task_row.pack_start(task_label, False, False, 0)
        task_row.pack_start(task_combo, True, True, 0)

        self.task_type_combo = task_combo
        task_combo.connect("changed", self._on_task_type_changed)
        model_params_box.pack_start(task_row, False, False, 0)

        # Noise level
        noise_label = Gtk.Label(_("Noise Level:"))
        noise_label.set_halign(Gtk.Align.START)

        noise_spin = Gtk.SpinButton()
        noise_spin.set_range(15, 50)
        noise_spin.set_increments(10, 25)
        noise_spin.set_value(15)
        noise_spin.set_tooltip_text(_("Noise level for denoising (15, 25, 50)"))

        noise_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        noise_row.pack_start(noise_label, False, False, 0)
        noise_row.pack_start(noise_spin, False, False, 0)
        noise_row.pack_start(Gtk.Label(""), True, True, 0)

        self.noise_spin = noise_spin
        self.noise_row = noise_row
        model_params_box.pack_start(noise_row, False, False, 0)

        # JPEG strength
        jpeg_label = Gtk.Label(_("JPEG Quality:"))
        jpeg_label.set_halign(Gtk.Align.START)

        jpeg_spin = Gtk.SpinButton()
        jpeg_spin.set_range(10, 40)
        jpeg_spin.set_increments(10, 15)
        jpeg_spin.set_value(40)
        jpeg_spin.set_tooltip_text(_("JPEG reduction strength (10, 20, 30, 40)"))

        jpeg_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        jpeg_row.pack_start(jpeg_label, False, False, 0)
        jpeg_row.pack_start(jpeg_spin, False, False, 0)
        jpeg_row.pack_start(Gtk.Label(""), True, True, 0)

        self.jpeg_spin = jpeg_spin
        self.jpeg_row = jpeg_row
        model_params_box.pack_start(jpeg_row, False, False, 0)

        # Apply initial visibility
        self._apply_initial_visibility()

    def _on_task_type_changed(self, combo):
        """Show/hide parameters based on selected task type"""
        task = combo.get_active_id()
        if self.noise_row:
            if task in ["Grayscale Image Denoising", "Color Image Denoising"]:
                self.noise_row.set_visible(True)
            else:
                self.noise_row.set_visible(False)

        if self.jpeg_row:
            if task == "JPEG Compression Artifact Reduction":
                self.jpeg_row.set_visible(True)
            else:
                self.jpeg_row.set_visible(False)

    def _apply_initial_visibility(self):
        """Apply initial conditional visibility"""
        if self.task_type_combo:
            task = self.task_type_combo.get_active_id()
            if self.noise_row:
                self.noise_row.set_visible(
                    task in ["Grayscale Image Denoising", "Color Image Denoising"]
                )
            if self.jpeg_row:
                self.jpeg_row.set_visible(task == "JPEG Compression Artifact Reduction")

    def get_parameters(self):
        """Get parameters for SwinIR"""
        params = {}
        if self.task_type_combo:
            params["task_type"] = self.task_type_combo.get_active_id()
        task = self.task_type_combo.get_active_id() if self.task_type_combo else None
        # noise parameter only relevant for denoising tasks
        if task and task in ["Grayscale Image Denoising", "Color Image Denoising"]:
            if self.noise_spin:
                params["noise"] = int(self.noise_spin.get_value())
        # jpeg parameter only relevant for JPEG artifact reduction
        if task and task == "JPEG Compression Artifact Reduction":
            if self.jpeg_spin:
                params["jpeg"] = int(self.jpeg_spin.get_value())
        return params

    def set_mode(self, mode):
        """Set mode (no effect for this model)"""
        super().set_mode(mode)

    def get_output_format(self):
        """No output format for this model"""
        return None


class GfpganStrategy(ModelConfigStrategy):
    """Strategy for GFPGAN model"""

    def __init__(self):
        super().__init__()
        self.gfp_version_combo = None
        self.scale_spin = None

    def create_params_ui(self, model_params_box):
        """Create parameters for GFPGAN"""
        # Version
        version_label = Gtk.Label(_("Model Version:"))
        version_label.set_halign(Gtk.Align.START)

        version_combo = Gtk.ComboBoxText()
        version_combo.set_tooltip_text(_("Select GFPGAN model weights"))
        version_combo.append("v1.3", _("v1.3"))
        version_combo.append("v1.4", _("v1.4"))
        version_combo.set_active_id("v1.4")

        version_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        version_row.pack_start(version_label, False, False, 0)
        version_row.pack_start(version_combo, True, True, 0)

        self.gfp_version_combo = version_combo
        model_params_box.pack_start(version_row, False, False, 0)

        # Scale
        scale_label = Gtk.Label(_("Scale Factor:"))
        scale_label.set_halign(Gtk.Align.START)

        scale_spin = Gtk.SpinButton()
        scale_spin.set_range(1.0, 4.0)
        scale_spin.set_increments(0.5, 1.0)
        scale_spin.set_value(2.0)
        scale_spin.set_tooltip_text(_("Final upsampling factor"))

        scale_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        scale_row.pack_start(scale_label, False, False, 0)
        scale_row.pack_start(scale_spin, False, False, 0)
        scale_row.pack_start(Gtk.Label(""), True, True, 0)

        self.scale_spin = scale_spin
        model_params_box.pack_start(scale_row, False, False, 0)

    def get_parameters(self):
        """Get parameters for GFPGAN"""
        params = {}
        if self.gfp_version_combo:
            params["version"] = self.gfp_version_combo.get_active_id()
        if self.scale_spin:
            params["scale"] = float(self.scale_spin.get_value())
        return params

    def set_mode(self, mode):
        """Set mode (no effect for this model)"""
        super().set_mode(mode)

    def get_output_format(self):
        """No output format for this model"""
        return None


# Register strategies
ModelRegistry.register("google/nano-banana", GoogleNanoBananaStrategy)
ModelRegistry.register("bytedance/seedream-4", BytedanceSeedreamStrategy)
ModelRegistry.register("qwen/qwen-image-edit-plus", QwenImageEditStrategy)
ModelRegistry.register(
    "jingyunliang/swinir:660d922d33153019e8c263a3bba265de882e7f4f70396546b6c9c8f9d47a021a",
    SwinirStrategy,
)
ModelRegistry.register(
    "tencentarc/gfpgan:0fbacf7afc6c144e5be9767cff80f25aff23e52b0708f17e20f9879b2f21516c",
    GfpganStrategy,
)


class ModelConfigUI(IModelConfig):
    """Handles API key input and model selection UI components"""

    def __init__(self):
        super().__init__()
        self.api_key_entry = None
        self.toggle_visibility_btn = None
        self.model_combo = None
        self.selected_model_version = ""
        self.output_format_combo = None
        self.model_params_box = None

        # Model parameter controls
        self.size_combo = None
        self.aspect_ratio_combo = None
        self.width_spin = None
        self.height_spin = None
        self.sequential_gen_combo = None
        self.max_images_spin = None
        self.qwen_aspect_ratio_combo = None
        self.go_fast_check = None
        self.seed_spin = None
        self.output_quality_spin = None
        self.disable_safety_check = None
        self.task_type_combo = None
        self.noise_spin = None
        self.jpeg_spin = None
        self.gfp_version_combo = None
        self.scale_spin = None

        # Store mode for parameter visibility
        self.current_mode = "generate"  # or "edit"

        # Current strategy
        self.current_strategy = None

    def _on_model_combo_changed(self, combo):
        """Keep the stored model version synchronized with the combo box."""
        if not combo:
            return
        active_id = combo.get_active_id()
        self.selected_model_version = active_id or ""
        self.emit("model_changed", self.selected_model_version)

    def toggle_api_key_visibility(self, button):
        """Toggle API key visibility and update button icon"""
        if not self.api_key_entry:
            return

        is_visible = button.get_active()
        self.api_key_entry.set_visibility(is_visible)

        icon_name = "view-reveal-symbolic" if is_visible else "view-conceal-symbolic"
        button.get_image().set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)

    def set_selected_model_version(self, model_version):
        """Store the selected model version and update the combo box."""
        normalized = (model_version or "").strip()

        if normalized and self._model_id_exists(normalized):
            self.selected_model_version = normalized
            if self.model_combo:
                self.model_combo.set_active_id(normalized)
            return True

        default_id = self._get_default_model_id()
        self.selected_model_version = default_id
        if self.model_combo and default_id:
            self.model_combo.set_active_id(default_id)
        return False

    def get_selected_model_version(self):
        """Return the current model version selection."""
        if self.model_combo:
            active_id = self.model_combo.get_active_id()
            if active_id:
                self.selected_model_version = active_id
                return active_id

        # Fallback to stored version or default
        if self.selected_model_version and self._model_id_exists(
            self.selected_model_version
        ):
            return self.selected_model_version

        # Final fallback to default
        default_id = self._get_default_model_id()
        self.selected_model_version = default_id
        return default_id

    def create_api_key_section(self):
        """Create API key input section"""
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        title_label = Gtk.Label()
        title_label.set_markup("<b>{}</b>".format(_("Replicate API Token")))
        title_label.set_halign(Gtk.Align.START)
        section_box.pack_start(title_label, False, False, 0)

        key_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.api_key_entry = Gtk.Entry()
        self.api_key_entry.set_placeholder_text(_("Enter your Replicate API token..."))
        self.api_key_entry.set_visibility(False)
        self.api_key_entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        key_container.pack_start(self.api_key_entry, True, True, 0)

        self.toggle_visibility_btn = Gtk.ToggleButton()
        self.toggle_visibility_btn.set_image(
            Gtk.Image.new_from_icon_name("view-conceal-symbolic", Gtk.IconSize.BUTTON),
        )
        self.toggle_visibility_btn.set_tooltip_text(_("Show/Hide API key"))
        key_container.pack_start(self.toggle_visibility_btn, False, False, 0)

        section_box.pack_start(key_container, False, False, 0)

        help_label = Gtk.Label()
        help_url = "https://replicate.com/account/api-tokens"
        help_text = _(
            'Get your token from <a href="{url}">replicate.com/account/api-tokens</a>',
        ).format(url=help_url)
        help_label.set_markup(f"<small>{help_text}</small>")
        help_label.set_halign(Gtk.Align.START)
        help_label.set_line_wrap(True)
        section_box.pack_start(help_label, False, False, 0)

        model_title = Gtk.Label()
        model_title.set_markup(f"<b>{_('Model')}</b>")
        model_title.set_halign(Gtk.Align.START)
        section_box.pack_start(model_title, False, False, 0)

        model_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.model_combo = Gtk.ComboBoxText()
        self.model_combo.set_hexpand(True)
        self.model_combo.set_tooltip_text(
            _("Choose which Replicate model to use for generation and editing."),
        )

        for model_id, label in REPLICATE_MODEL_OPTIONS:
            self.model_combo.append(model_id, label)

        self.model_combo.connect("changed", self._on_model_combo_changed)
        self.model_combo.connect("changed", self._on_model_changed_update_params)

        if self.selected_model_version:
            self.set_selected_model_version(self.selected_model_version)
        else:
            self.set_selected_model_version(self._get_default_model_id())

        model_row.pack_start(self.model_combo, True, True, 0)
        section_box.pack_start(model_row, False, False, 0)

        # Model parameters section (collapsible)
        params_expander = Gtk.Expander.new(_("Model Parameters"))
        params_expander.set_expanded(True)
        params_expander.set_margin_top(8)
        section_box.pack_start(params_expander, False, False, 0)

        self.model_params_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._update_model_parameters()
        params_expander.add(self.model_params_box)

        return section_box

    def _on_model_changed_update_params(self, combo):
        """Update model parameters when model selection changes"""
        self._update_model_parameters()

    def set_mode(self, mode):
        """Set the current mode (generate or edit) for parameter visibility"""
        self.current_mode = mode.lower()
        self._update_model_parameters()
        self.emit("mode_changed", self.current_mode)

    def _update_model_parameters(self):
        """Update the model parameters UI based on selected model and mode"""
        if not self.model_params_box:
            return

        # Clear existing parameters
        for child in self.model_params_box.get_children():
            self.model_params_box.remove(child)

        model_version = self.get_selected_model_version()
        if not model_version:
            return

        strategy_class = ModelRegistry.get_strategy(model_version)
        if not strategy_class:
            return

        self.current_strategy = strategy_class()
        self.current_strategy.set_mode(self.current_mode)
        self.current_strategy.create_params_ui(self.model_params_box)

        # Show all widgets first, then apply conditional visibility
        self.model_params_box.show_all()
        # Strategies handle their own initial visibility

    def _create_google_nano_banana_params(self):
        """Create parameters for Google Nano Banana"""
        # Output format
        format_label = Gtk.Label(_("Output Format:"))
        format_label.set_halign(Gtk.Align.START)

        format_combo = Gtk.ComboBoxText()
        format_combo.set_tooltip_text(_("Select output image format"))
        format_combo.append("jpg", _("JPEG"))
        format_combo.append("png", _("PNG"))
        format_combo.set_active_id("jpg")

        format_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        format_row.pack_start(format_label, False, False, 0)
        format_row.pack_start(format_combo, True, True, 0)

        self.output_format_combo = format_combo
        self.model_params_box.pack_start(format_row, False, False, 0)

    def _create_bytedance_seedream_params(self):
        """Create parameters for Bytedance SeeDream 4 (generation only)"""
        if self.current_mode != "generate":
            return

        # Size
        size_label = Gtk.Label(_("Size:"))
        size_label.set_halign(Gtk.Align.START)

        size_combo = Gtk.ComboBoxText()
        size_combo.set_tooltip_text(_("Select image size preset"))
        size_combo.append("1K", _("1K"))
        size_combo.append("2K", _("2K"))
        size_combo.append("4K", _("4K"))
        size_combo.append("custom", _("Custom"))
        size_combo.set_active_id("2K")

        size_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        size_row.pack_start(size_label, False, False, 0)
        size_row.pack_start(size_combo, True, True, 0)

        self.size_combo = size_combo
        size_combo.connect("changed", self._on_size_combo_changed)
        self.model_params_box.pack_start(size_row, False, False, 0)

        # Aspect ratio (only shown when size != custom)
        aspect_label = Gtk.Label(_("Aspect Ratio:"))
        aspect_label.set_halign(Gtk.Align.START)

        aspect_combo = Gtk.ComboBoxText()
        aspect_combo.set_tooltip_text(_("Select aspect ratio"))
        aspect_combo.append("match_input_image", _("Match Input Image"))
        aspect_combo.append("1:1", _("1:1"))
        aspect_combo.append("4:3", _("4:3"))
        aspect_combo.append("3:4", _("3:4"))
        aspect_combo.append("16:9", _("16:9"))
        aspect_combo.append("9:16", _("9:16"))
        aspect_combo.append("3:2", _("3:2"))
        aspect_combo.append("2:3", _("2:3"))
        aspect_combo.append("21:9", _("21:9"))
        aspect_combo.set_active_id("match_input_image")

        aspect_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        aspect_row.pack_start(aspect_label, False, False, 0)
        aspect_row.pack_start(aspect_combo, True, True, 0)

        self.aspect_ratio_combo = aspect_combo
        # Show aspect ratio by default when size starts as non-custom (2K)
        # Will be hidden if user selects "custom" later
        aspect_row.set_visible(True)
        self.aspect_ratio_row = aspect_row
        self.model_params_box.pack_start(aspect_row, False, False, 0)

        # Custom size controls (initially hidden)
        self._create_custom_size_controls()

        # Sequential generation
        seq_label = Gtk.Label(_("Sequential Generation:"))
        seq_label.set_halign(Gtk.Align.START)

        seq_combo = Gtk.ComboBoxText()
        seq_combo.set_tooltip_text(_("Enable sequential image generation"))
        seq_combo.append("disabled", _("Disabled"))
        seq_combo.append("auto", _("Auto"))
        seq_combo.set_active_id("disabled")

        seq_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        seq_row.pack_start(seq_label, False, False, 0)
        seq_row.pack_start(seq_combo, True, True, 0)

        self.sequential_gen_combo = seq_combo
        seq_combo.connect("changed", self._on_sequential_gen_changed)
        self.model_params_box.pack_start(seq_row, False, False, 0)

        # Max images (initially hidden)
        self._create_max_images_control()

    def _create_custom_size_controls(self):
        """Create width/height controls for custom size"""
        self.width_spin = Gtk.SpinButton()
        self.width_spin.set_range(1024, 4096)
        self.width_spin.set_increments(64, 256)
        self.width_spin.set_value(2048)
        self.width_spin.set_tooltip_text(_("Width (1024-4096)"))

        self.height_spin = Gtk.SpinButton()
        self.height_spin.set_range(1024, 4096)
        self.height_spin.set_increments(64, 256)
        self.height_spin.set_value(2048)
        self.height_spin.set_tooltip_text(_("Height (1024-4096)"))

        size_label = Gtk.Label(_("Custom Size:"))
        size_label.set_halign(Gtk.Align.START)

        size_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        size_row.pack_start(size_label, False, False, 0)
        size_row.pack_start(Gtk.Label("W:"), False, False, 0)
        size_row.pack_start(self.width_spin, False, False, 0)
        size_row.pack_start(Gtk.Label("H:"), False, False, 0)
        size_row.pack_start(self.height_spin, False, False, 0)
        size_row.pack_start(Gtk.Label(""), True, True, 0)

        self.model_params_box.pack_start(size_row, False, False, 0)
        size_row.set_visible(False)
        self.custom_size_row = size_row

    def _create_max_images_control(self):
        """Create max images control for sequential generation"""
        max_images_label = Gtk.Label(_("Max Images:"))
        max_images_label.set_halign(Gtk.Align.START)

        max_images_spin = Gtk.SpinButton()
        max_images_spin.set_range(1, 15)
        max_images_spin.set_increments(1, 3)
        max_images_spin.set_value(1)
        max_images_spin.set_tooltip_text(_("Maximum images to generate (1-15)"))

        max_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        max_row.pack_start(max_images_label, False, False, 0)
        max_row.pack_start(max_images_spin, False, False, 0)
        max_row.pack_start(Gtk.Label(""), True, True, 0)

        self.max_images_spin = max_images_spin
        self.model_params_box.pack_start(max_row, False, False, 0)
        max_row.set_visible(False)
        self.max_images_row = max_row

    def _on_size_combo_changed(self, combo):
        """Show/hide custom size controls and aspect ratio based on size selection"""
        is_custom = combo.get_active_id() == "custom"
        if hasattr(self, "custom_size_row"):
            self.custom_size_row.set_visible(is_custom)
        # aspect_ratio is shown when size != custom (as per API docs: "used when size ≠ custom")
        if hasattr(self, "aspect_ratio_row"):
            self.aspect_ratio_row.set_visible(not is_custom)

    def _on_sequential_gen_changed(self, combo):
        """Show/hide max images control based on sequential generation selection"""
        if combo.get_active_id() == "auto":
            if hasattr(self, "max_images_row"):
                self.max_images_row.set_visible(True)
        else:
            if hasattr(self, "max_images_row"):
                self.max_images_row.set_visible(False)

    def _create_qwen_image_edit_params(self):
        """Create parameters for Qwen Image Edit"""
        # Show aspect ratio only in edit mode for Qwen (generation models should use aspect ratio)
        if self.current_mode == "edit":
            # Aspect ratio
            aspect_label = Gtk.Label(_("Aspect Ratio:"))
            aspect_label.set_halign(Gtk.Align.START)

            aspect_combo = Gtk.ComboBoxText()
            aspect_combo.set_tooltip_text(_("Select output aspect ratio"))
            aspect_combo.append("match_input_image", _("Match Input Image"))
            aspect_combo.append("1:1", _("1:1"))
            aspect_combo.append("4:3", _("4:3"))
            aspect_combo.append("3:4", _("3:4"))
            aspect_combo.append("16:9", _("16:9"))
            aspect_combo.append("9:16", _("9:16"))
            aspect_combo.set_active_id("match_input_image")

            aspect_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            aspect_row.pack_start(aspect_label, False, False, 0)
            aspect_row.pack_start(aspect_combo, True, True, 0)

            self.qwen_aspect_ratio_combo = aspect_combo
            self.model_params_box.pack_start(aspect_row, False, False, 0)

        # Go fast
        go_fast_check = Gtk.CheckButton(_("Go Fast (Speed Optimization)"))
        go_fast_check.set_active(True)
        go_fast_check.set_tooltip_text(_("Enable speed optimizations"))

        self.go_fast_check = go_fast_check
        self.model_params_box.pack_start(go_fast_check, False, False, 0)

        # Seed
        seed_label = Gtk.Label(_("Seed (optional):"))
        seed_label.set_halign(Gtk.Align.START)

        seed_spin = Gtk.SpinButton()
        seed_spin.set_range(0, 999999999)
        seed_spin.set_increments(1, 1000)
        seed_spin.set_value(0)
        seed_spin.set_tooltip_text(_("Set for reproducible edits (0 = random)"))

        seed_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        seed_row.pack_start(seed_label, False, False, 0)
        seed_row.pack_start(seed_spin, False, False, 0)
        seed_row.pack_start(Gtk.Label(""), True, True, 0)

        self.seed_spin = seed_spin
        self.model_params_box.pack_start(seed_row, False, False, 0)

        # Output format
        format_label = Gtk.Label(_("Output Format:"))
        format_label.set_halign(Gtk.Align.START)

        format_combo = Gtk.ComboBoxText()
        format_combo.set_tooltip_text(_("Select output image format"))
        format_combo.append("png", _("PNG"))
        format_combo.append("jpg", _("JPEG"))
        format_combo.set_active_id("png")

        format_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        format_row.pack_start(format_label, False, False, 0)
        format_row.pack_start(format_combo, True, True, 0)

        self.output_format_combo = format_combo
        format_combo.connect("changed", self._on_output_format_changed)
        self.model_params_box.pack_start(format_row, False, False, 0)

        # Output quality (only shown when format is not PNG, as per API docs: "Ignored for PNG")
        quality_label = Gtk.Label(_("Output Quality:"))
        quality_label.set_halign(Gtk.Align.START)

        quality_spin = Gtk.SpinButton()
        quality_spin.set_range(0, 100)
        quality_spin.set_increments(1, 10)
        quality_spin.set_value(95)
        quality_spin.set_tooltip_text(_("Quality for JPEG (0-100, ignored for PNG)"))

        quality_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        quality_row.pack_start(quality_label, False, False, 0)
        quality_row.pack_start(quality_spin, False, False, 0)
        quality_row.pack_start(Gtk.Label(""), True, True, 0)

        self.output_quality_spin = quality_spin
        # Hide quality initially when format starts as PNG
        quality_row.set_visible(False)
        self.quality_row = quality_row
        self.model_params_box.pack_start(quality_row, False, False, 0)

        # Disable safety checker
        safety_check = Gtk.CheckButton(_("Disable Safety Checker"))
        safety_check.set_active(False)
        safety_check.set_tooltip_text(_("Bypass safety checks"))

        self.disable_safety_check = safety_check
        self.model_params_box.pack_start(safety_check, False, False, 0)

    def _create_swinir_params(self):
        """Create parameters for SwinIR"""
        # Task type
        task_label = Gtk.Label(_("Task Type:"))
        task_label.set_halign(Gtk.Align.START)

        task_combo = Gtk.ComboBoxText()
        task_combo.set_tooltip_text(_("Select image processing task"))
        task_combo.append(
            "Real-World Image Super-Resolution-Large", _("Super-Resolution Large")
        )
        task_combo.append(
            "Real-World Image Super-Resolution-Medium", _("Super-Resolution Medium")
        )
        task_combo.append("Grayscale Image Denoising", _("Grayscale Denoising"))
        task_combo.append("Color Image Denoising", _("Color Denoising"))
        task_combo.append(
            "JPEG Compression Artifact Reduction", _("JPEG Artifact Reduction")
        )
        task_combo.set_active_id("Real-World Image Super-Resolution-Large")

        task_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        task_row.pack_start(task_label, False, False, 0)
        task_row.pack_start(task_combo, True, True, 0)

        self.task_type_combo = task_combo
        task_combo.connect("changed", self._on_task_type_changed)
        self.model_params_box.pack_start(task_row, False, False, 0)

        # Noise level (for denoising tasks)
        self._create_noise_control()

        # JPEG strength (for JPEG reduction task)
        self._create_jpeg_control()

    def _create_noise_control(self):
        """Create noise level control for denoising tasks"""
        noise_label = Gtk.Label(_("Noise Level:"))
        noise_label.set_halign(Gtk.Align.START)

        noise_spin = Gtk.SpinButton()
        noise_spin.set_range(15, 50)
        noise_spin.set_increments(10, 25)
        noise_spin.set_value(15)
        noise_spin.set_tooltip_text(_("Noise level for denoising (15, 25, 50)"))

        noise_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        noise_row.pack_start(noise_label, False, False, 0)
        noise_row.pack_start(noise_spin, False, False, 0)
        noise_row.pack_start(Gtk.Label(""), True, True, 0)

        self.noise_spin = noise_spin
        self.model_params_box.pack_start(noise_row, False, False, 0)
        noise_row.set_visible(False)
        self.noise_row = noise_row

    def _create_jpeg_control(self):
        """Create JPEG strength control for JPEG reduction task"""
        jpeg_label = Gtk.Label(_("JPEG Quality:"))
        jpeg_label.set_halign(Gtk.Align.START)

        jpeg_spin = Gtk.SpinButton()
        jpeg_spin.set_range(10, 40)
        jpeg_spin.set_increments(10, 15)
        jpeg_spin.set_value(40)
        jpeg_spin.set_tooltip_text(_("JPEG reduction strength (10, 20, 30, 40)"))

        jpeg_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        jpeg_row.pack_start(jpeg_label, False, False, 0)
        jpeg_row.pack_start(jpeg_spin, False, False, 0)
        jpeg_row.pack_start(Gtk.Label(""), True, True, 0)

        self.jpeg_spin = jpeg_spin
        self.model_params_box.pack_start(jpeg_row, False, False, 0)
        jpeg_row.set_visible(False)
        self.jpeg_row = jpeg_row

    def _on_output_format_changed(self, combo):
        """Show/hide output quality based on format selection"""
        # Force show_all on the quality_row to ensure it's visible when needed, but will be hidden if not jpg
        if hasattr(self, "quality_row"):
            self.quality_row.show_all()
        if combo.get_active_id() == "jpg":
            if hasattr(self, "quality_row"):
                self.quality_row.set_visible(True)
        else:
            if hasattr(self, "quality_row"):
                self.quality_row.set_visible(False)

    def _on_task_type_changed(self, combo):
        """Show/hide parameters based on selected task type"""
        task = combo.get_active_id()
        if hasattr(self, "noise_row"):
            if task in ["Grayscale Image Denoising", "Color Image Denoising"]:
                self.noise_row.set_visible(True)
            else:
                self.noise_row.set_visible(False)

        if hasattr(self, "jpeg_row"):
            if task == "JPEG Compression Artifact Reduction":
                self.jpeg_row.set_visible(True)
            else:
                self.jpeg_row.set_visible(False)

    def _create_gfpgan_params(self):
        """Create parameters for GFPGAN"""
        # Version
        version_label = Gtk.Label(_("Model Version:"))
        version_label.set_halign(Gtk.Align.START)

        version_combo = Gtk.ComboBoxText()
        version_combo.set_tooltip_text(_("Select GFPGAN model weights"))
        version_combo.append("v1.3", _("v1.3"))
        version_combo.append("v1.4", _("v1.4"))
        version_combo.set_active_id("v1.4")

        version_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        version_row.pack_start(version_label, False, False, 0)
        version_row.pack_start(version_combo, True, True, 0)

        self.gfp_version_combo = version_combo
        self.model_params_box.pack_start(version_row, False, False, 0)

        # Scale
        scale_label = Gtk.Label(_("Scale Factor:"))
        scale_label.set_halign(Gtk.Align.START)

        scale_spin = Gtk.SpinButton()
        scale_spin.set_range(1.0, 4.0)
        scale_spin.set_increments(0.5, 1.0)
        scale_spin.set_value(2.0)
        scale_spin.set_tooltip_text(_("Final upsampling factor"))

        scale_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        scale_row.pack_start(scale_label, False, False, 0)
        scale_row.pack_start(scale_spin, False, False, 0)
        scale_row.pack_start(Gtk.Label(""), True, True, 0)

        self.scale_spin = scale_spin
        self.model_params_box.pack_start(scale_row, False, False, 0)

    def get_output_format(self):
        """Get the selected output format, or None if not applicable"""
        if self.current_strategy:
            return self.current_strategy.get_output_format()
        return None

    def get_model_parameters(self):
        """Get relevant model-specific parameters as a dictionary (only sends visible/relevant params)"""
        if self.current_strategy:
            return self.current_strategy.get_parameters()
        return {}

    def _get_default_model_id(self):
        """Return the default model identifier from the options list."""
        if REPLICATE_MODEL_OPTIONS:
            return REPLICATE_MODEL_OPTIONS[0][0]
        return ""

    def _apply_initial_conditional_visibility(self):
        """Apply initial conditional visibility based on default values"""
        # Apply initial visibility rules when parameters are first created
        # This ensures proper visibility from the start, not just on user selections

        # For SeeDream 4 size combo (default "2K" = non-custom: aspect_ratio visible, custom_size hidden)
        if self.size_combo:
            if hasattr(self, "aspect_ratio_row") and self.aspect_ratio_row:
                self.aspect_ratio_row.set_visible(True)
            if hasattr(self, "custom_size_row") and self.custom_size_row:
                self.custom_size_row.set_visible(False)

        # For SeeDream 4 sequential generation (default "disabled": max_images hidden)
        if self.sequential_gen_combo:
            if hasattr(self, "max_images_row") and self.max_images_row:
                self.max_images_row.set_visible(False)

        # For Qwen output format (default "png": quality hidden)
        if self.output_format_combo:
            if hasattr(self, "quality_row") and self.quality_row:
                self.quality_row.set_visible(False)

        # For SwinIR task type (default "Real-World Image Super-Resolution-Large": noise/jpeg hidden)
        if self.task_type_combo:
            if hasattr(self, "noise_row") and self.noise_row:
                self.noise_row.set_visible(False)
            if hasattr(self, "jpeg_row") and self.jpeg_row:
                self.jpeg_row.set_visible(False)

    def _model_id_exists(self, model_id):
        """Check if the provided model ID exists in the options list."""
        for option_id, _label in REPLICATE_MODEL_OPTIONS:
            if option_id == model_id:
                return True
        return False
