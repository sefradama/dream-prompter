#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Constants and configuration values for Dream Prompter."""

# File and size limits
MAX_LAYER_NAME_LENGTH = 64
"""Maximum length for GIMP layer names"""

MAX_FILE_SIZE_MB = 7
"""Maximum file size for reference images in MB"""

MAX_DOWNLOAD_SIZE_MB = 50
"""Maximum download size for images in MB"""

# Replicate API limits
MAX_REFERENCE_IMAGES_EDIT = 2
"""Maximum reference images allowed for edit mode"""

MAX_REFERENCE_IMAGES_GENERATE = 3
"""Maximum reference images allowed for generate mode"""

# Progress reporting constants
PROGRESS_COMPLETE = 1.0
"""Progress value indicating completion"""

PROGRESS_DOWNLOAD = 0.9
"""Progress value for download phase"""

PROGRESS_PREPARE = 0.1
"""Progress value for preparation phase"""

PROGRESS_PROCESS = 0.7
"""Progress value for processing phase"""

PROGRESS_UPLOAD = 0.5
"""Progress value for upload phase"""

# File types
SUPPORTED_MIME_TYPES = ["image/png", "image/jpeg", "image/webp"]
"""Supported MIME types for reference images"""

# Validation sizes
VALIDATION_HEADER_SIZE = 65536  # 64KB
"""Size of file header to read for validation"""

VALIDATION_CHUNK_SIZE = 8192  # 8KB
"""Chunk size for validation reads"""

VALIDATION_MAX_CHUNKS = 10
"""Maximum chunks to read for validation"""

# Security
TRUSTED_DOMAINS = {"replicate.com", "replicate.ai", "api.replicate.com"}
"""Trusted domains for image downloads"""

DOWNLOAD_TIMEOUT = 30
"""Timeout for download requests in seconds"""

# Settings
CONFIG_FILE_NAME = "dream-prompter-config.json"
GIMP_VERSION = "3.0"
FILE_PERMISSIONS = 0o600

# Encryption
ENCRYPTION_KEY_FILE = "dream-prompter-key"

# Environment variables
ENV_TOKEN_VAR = "REPLICATE_API_TOKEN"
DEFAULT_MODEL_ENV_VAR = "REPLICATE_DEFAULT_MODEL"

# Defaults
DEFAULT_MODE = "edit"
DEFAULT_API_KEY_VISIBLE = False
DEFAULT_MODEL_VERSION = "google/nano-banana"
