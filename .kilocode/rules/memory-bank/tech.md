# Technology Stack

## Technologies Used

### Core Technologies
- **Python 3.8+**: Primary programming language for GIMP plugin development
- **GTK 3.0**: Cross-platform GUI toolkit for user interface components
- **GIMP 3.0**: Host application providing image manipulation capabilities
- **GdkPixbuf**: Image processing and format conversion library
- **Gio**: File I/O operations within GIMP environment

### External Integrations
- **Replicate API**: Cloud-based AI model hosting and execution platform
- **Cryptography (Fernet)**: Symmetric encryption for secure credential storage

### Development Tools
- **Ruff**: Fast Python linter and code formatter
- **Pyright**: Static type checker for Python
- **GNU Gettext**: Internationalization and localization framework

## Development Setup

### Prerequisites
- **GIMP 3.0.x** with Python 3.8+ support
- **Replicate account** with active API token
- **Python dependencies**: `replicate`, `cryptography`

### Installation Steps
1. **Clone repository**: `git clone <repository-url>`
2. **Install Python dependencies**: `pip install replicate cryptography`
3. **Copy plugin files** to GIMP plugins directory:
   - Linux: `~/.config/GIMP/3.0/plug-ins/dream-prompter/`
   - macOS: `~/Library/Application Support/GIMP/3.0/plug-ins/dream-prompter/`
   - Windows: `%APPDATA%\GIMP\3.0\plug-ins\dream-prompter\`
4. **Set executable permissions**: `chmod +x dream-prompter.py`
5. **Build translations** (optional): `python3 scripts/build-translations.py`

### Development Workflow
1. **Code changes** in source directory
2. **Symlink for testing**: `ln -s $(pwd) ~/.config/GIMP/3.0/plug-ins/dream-prompter`
3. **Restart GIMP** to load plugin changes
4. **Test functionality** through GIMP interface
5. **Run linting**: `ruff check --fix && ruff format`

## Technical Constraints

### GIMP Plugin Limitations
- **Single-threaded UI**: All GTK operations must occur on main thread
- **Memory constraints**: Large images require careful memory management
- **File permissions**: Plugin directory must be writable for settings storage
- **Python environment**: Must use GIMP's embedded Python interpreter

### API Limitations
- **Rate limiting**: Replicate API has request frequency limits
- **Cost tracking**: Each API call consumes credits from user account
- **Image size limits**: Maximum dimensions and file sizes for uploads
- **Model availability**: Only Replicate-hosted models are supported

### Security Constraints
- **Credential storage**: API keys must be encrypted at rest
- **Network security**: HTTPS-only communication with Replicate
- **Domain validation**: Only trusted domains allowed for image downloads
- **Input validation**: All user inputs must be sanitized

### Performance Constraints
- **UI responsiveness**: Long-running operations must be background-threaded
- **Memory usage**: Large images require streaming and chunked processing
- **Network timeouts**: API calls must have reasonable timeout limits
- **File I/O**: Efficient handling of temporary files and cleanup

## Dependencies

### Runtime Dependencies
- **replicate>=0.25.0**: Python client for Replicate API
- **cryptography>=3.4.0**: Encryption library for secure settings storage

### System Dependencies
- **GIMP 3.0+**: Host application with Python scripting support
- **GTK 3.0**: GUI toolkit (included with GIMP)
- **GdkPixbuf**: Image processing (included with GIMP)
- **Gio**: File operations (included with GIMP)

### Development Dependencies
- **ruff>=0.1.0**: Linting and formatting tool
- **pyright>=1.1.0**: Type checking tool
- **gettext**: Translation toolchain

## Tool Usage Patterns

### Code Quality
- **Linting**: `ruff check --fix` - Automatically fix linting issues
- **Formatting**: `ruff format` - Standardize code formatting
- **Type checking**: `pyright` - Static type analysis

### Translation Management
- **Extract strings**: `python3 scripts/update-pot.py` - Update translation template
- **Update translations**: `python3 scripts/update-translations.py` - Sync translation files
- **Compile translations**: `python3 scripts/build-translations.py` - Generate binary catalogs

### Testing Patterns
- **Manual testing**: Restart GIMP after code changes
- **API testing**: Use Replicate dashboard to monitor usage
- **UI testing**: Test all dialog states and error conditions
- **Cross-platform testing**: Verify on Linux, macOS, and Windows

### Build Patterns
- **Plugin packaging**: Copy all Python files to GIMP plugins directory
- **Translation building**: Compile .po files to .mo binaries
- **Symlink development**: Use symbolic links for rapid iteration
- **Permission setting**: Ensure executable permissions on main script

### Deployment Patterns
- **User installation**: Copy files to user-specific GIMP directory
- **System installation**: May require elevated permissions
- **Update mechanism**: Manual download and replacement
- **Configuration migration**: Handle settings format changes gracefully

## Development Environment

### Directory Structure
```
dream-prompter/
├── *.py                 # Core Python modules
├── scripts/             # Build and development scripts
├── locale/              # Translation files
├── stubs/               # Type stubs for external libraries
├── screenshots/         # Documentation images
└── .kilocode/           # Development tooling configuration
```

### Configuration Files
- **pyproject.toml**: Python project configuration and tool settings
- **pyrightconfig.json**: Type checker configuration
- **.gitignore**: Version control exclusions

### Environment Variables
- **REPLICATE_API_TOKEN**: API authentication (fallback to UI entry)
- **REPLICATE_DEFAULT_MODEL**: Default model selection

## Platform-Specific Considerations

### Linux
- **Plugin path**: `~/.config/GIMP/3.0/plug-ins/`
- **Python path**: Usually `/usr/bin/python3`
- **Permissions**: Standard user permissions sufficient

### macOS
- **Plugin path**: `~/Library/Application Support/GIMP/3.0/plug-ins/`
- **Python path**: `/Applications/GIMP.app/Contents/MacOS/python3`
- **Dependencies**: May need custom pip installation

### Windows
- **Plugin path**: `%APPDATA%\GIMP\3.0\plug-ins\`
- **Python path**: Embedded in GIMP installation
- **Permissions**: Windows-specific file security considerations