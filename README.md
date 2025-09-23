# Dream Prompter - GIMP Plugin

Dream Prompter brings Replicate-hosted image generation models directly into GIMP for intelligent image creation and editing. Switch between Replicate model versions to explore different aesthetics without leaving your editing workflow.

![Dream Prompter](screenshots/dream-prompter.png)

## Features

- 🎨 **AI Image Generation**: Create new images from text descriptions
- ✨ **AI Image Editing**: Transform existing images with natural language prompts
- 🖼️ **Reference Images**: Use up to 3 reference images for generation, 2 for editing
- 🔄 **Smart Layer Management**: Automatically creates properly named layers
- 🎯 **Dual Operation Modes**: Seamlessly switch between editing and generation
- 🌍 **Multi-Language Support**: Setup to support multiple languages via i18n
- 🔒 **Safe File Handling**: Validates image formats and file sizes
- 🏗️ **Native GIMP Integration**: Works seamlessly within your GIMP workflow

## Installation

### Prerequisites

- **GIMP 3.0.x**
- **Python 3.8+**
- **Replicate account** with an active API token ([replicate.com/account/api-tokens](https://replicate.com/account/api-tokens))
- **`replicate` Python package** available to GIMP's embedded interpreter

Install the required Python library:

```bash
pip install replicate
```

### Quick Install

1. **Download the latest release** from [GitHub Releases](https://github.com/zquestz/dream-prompter/releases)

2. **Extract the release**

   This will create a folder named `dream-prompter-{version}` (e.g., `dream-prompter-1.0.3`)

3. **Move to your GIMP plugins folder with the correct name:**

   Rename and move the extracted folder to exactly `dream-prompter` in your GIMP plugins directory:
   - **Linux**: `~/.config/GIMP/3.0/plug-ins/dream-prompter/`
   - **Windows**: `%APPDATA%\GIMP\3.0\plug-ins\dream-prompter\`
   - **macOS**: `~/Library/Application Support/GIMP/3.0/plug-ins/dream-prompter/`

   Example for Linux:

   ```bash
   # Extract creates dream-prompter-1.0.3/
   unzip dream-prompter-1.0.3.zip
   # Move to correct location with correct name
   mv dream-prompter-1.0.3 ~/.config/GIMP/3.0/plug-ins/dream-prompter
   ```

4. **Make executable** (Linux/macOS only):

   ```bash
   chmod +x ~/.config/GIMP/3.0/plug-ins/dream-prompter/dream-prompter.py
   ```

5. **Restart GIMP**

**Building translations (optional):** If you need languages other than English, run `python3 scripts/build-translations.py` in the plugin directory after installation.

### Arch Linux Installation

To install Dream Prompter on Arch Linux, you can install it from the AUR.

```bash
yay -S dream-prompter
```

### Advanced Installation

#### Manual Installation from Source

1. **Find your GIMP plugins directory** (paths listed above)

2. **Create plugin directory:**

   ```bash
   mkdir -p ~/.config/GIMP/3.0/plug-ins/dream-prompter/
   ```

3. **Copy all Python files:**

   ```bash
   cp *.py ~/.config/GIMP/3.0/plug-ins/dream-prompter/
   ```

4. **Build and install translations (Optional):**

   ```bash
   python3 scripts/build-translations.py
   cp -r locale ~/.config/GIMP/3.0/plug-ins/dream-prompter/
   ```

5. **Make executable:**
   ```bash
   chmod +x ~/.config/GIMP/3.0/plug-ins/dream-prompter/dream-prompter.py
   ```

#### Development Setup

```bash
git clone https://github.com/zquestz/dream-prompter.git
cd dream-prompter
pip install replicate
python3 scripts/build-translations.py # optional, defaults to English
ln -s $(pwd) ~/.config/GIMP/3.0/plug-ins/dream-prompter
```

### Python Dependencies Note

**Important**: Use the same Python that GIMP uses. If `pip install replicate` doesn't work:

```bash
# System-wide installation
sudo pip install replicate

# User installation (recommended)
pip install --user replicate

# Ensure Python 3
pip3 install replicate
```

#### macOS Instructions

If you get the **"replicate not installed"** error on macOS:

1. **Locate GIMP's Python** by opening the Python Console: `Filters → Development → Python-Fu`
2. **Run this command** in the console:

   ```python
   import sys; print(sys.executable)
   ```

   You should see something like:

   ```
   /Applications/GIMP.app/Contents/MacOS/python3
   ```

3. **Install replicate using GIMP's Python** from Terminal:

   ```bash
   # Change to GIMP's Python directory
   cd /Applications/GIMP.app/Contents/MacOS

   # Ensure pip is installed
   ./python3 -m ensurepip

   # Install replicate
   ./python3 -m pip install replicate
   ```

## Getting Your API Key

**Important**: Replicate bills usage per prediction. Most featured models require paid credits, so ensure your Replicate account has an active billing method or sufficient prepaid credits before running jobs.

1. **Visit [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens)**
2. **Sign in or create a Replicate account**
3. **Click "Create token"** and optionally label it for Dream Prompter
4. **Copy the generated token** into the plugin or set it as the `REPLICATE_API_TOKEN` environment variable
5. **Monitor usage and spend** from the Replicate dashboard

### API Specifications

- **Model version format**: `owner/model:version_hash` (examples: `google/nano-banana`, `bytedance/seedream-4`, `qwen/qwen-image-edit`)
- **Billing**: Predictions deduct credits from your Replicate account
- **Image Limits**:
  - Generation mode: Up to 3 reference images
  - Edit mode: Up to 2 reference images (current image + 2 = 3 total)
- **File Size**: Maximum 7MB per image
- **Formats**: PNG, JPEG, WebP only

### Cost Considerations

- Each Replicate prediction (generation or edit) consumes credits based on the selected model
- Monitor usage, invoices, and credit balance at [replicate.com/account/billing](https://replicate.com/account/billing)
- Set spending alerts or auto top-ups in Replicate to avoid interrupted workflows

## Usage

### Basic Workflow

1. **Open an image in GIMP** (for editing) or create a new document (for generation)
2. **Launch Dream Prompter**: `Filters → AI → Dream Prompter...`
3. **Enter your API key** (saved automatically for future use)
4. **Select mode**:
   - **Edit Mode**: Transform the current layer
   - **Generate Mode**: Create a new image
5. **Write your prompt**: Be descriptive and specific
6. **Add reference images** (optional): Click "Select Images..." to add references
7. **Generate**: Click the generate button and watch the progress
8. **Result**: New layer appears with a descriptive name

### Example Prompts

**For Generation:**

- "A majestic dragon flying over snow-capped mountains at sunset"
- "Portrait of a woman in Victorian dress, oil painting style"
- "Cyberpunk cityscape with neon reflections on wet streets"

**For Editing:**

- "Change the background to a peaceful forest clearing"
- "Make this person wear a red Victorian dress"
- "Transform this into a watercolor painting style"
- "Add falling snow to this winter scene"

### Tips for Best Results

- **Be specific**: "Red sports car" vs "bright red Ferrari 488 GTB"
- **Include style**: "photorealistic", "oil painting", "digital art"
- **Describe lighting**: "golden hour", "dramatic shadows", "soft natural light"
- **Use reference images** to guide style and composition
- **Keep files under 7MB** for reference images

## Language Support

### Available Languages

Dream Prompter is fully translated and available in:

- **🇺🇸 English** (default)
- **🇪🇸 Spanish** (complete)
- **🇫🇷 French** (complete)
- **🇵🇹 Portuguese** (complete)
- **🇷🇺 Russian** (complete)
- **🇯🇵 Japanese** (complete)
- **🇮🇳 Hindi** (complete)
- **🇧🇩 Bengali** (complete)
- **🇨🇳 Chinese (Simplified)** (complete)
- **🇹🇼 Chinese (Traditional)** (complete)
- **🇰🇷 Korean** (complete)

The plugin automatically detects your system language and uses the appropriate translation. If your language isn't available, it defaults to English.

### For Developers

```bash
# Extract new translatable strings
python3 scripts/update-pot.py

# Update existing translations
python3 scripts/update-translations.py

# Build compiled translations
python3 scripts/build-translations.py
```

## Architecture

The plugin is organized into focused modules:

- **`dream-prompter.py`** - Main GIMP plugin entry point
- **`dialog_gtk.py`** - GTK user interface components
- **`dialog_events.py`** - Event handling and user interactions
- **`dialog_threads.py`** - Background processing and threading
- **`api.py`** - Replicate API integration
- **`integrator.py`** - GIMP-specific operations
- **`settings.py`** - Configuration persistence
- **`i18n.py`** - Internationalization support

## Troubleshooting

### Common Issues

**"`replicate` package not installed" warning**

- Install with: `pip install replicate`
- Ensure you're using GIMP's Python environment

**Plugin doesn't appear in menu**

- Check file permissions: `chmod +x dream-prompter.py`
- Restart GIMP after installation
- Verify files are in correct plugins directory

**API errors**

- Verify your Replicate API token is correct and not expired
- Confirm the selected model version exists and your account has sufficient credits
- Check [status.replicate.com](https://status.replicate.com/) for any ongoing incidents

**Image processing issues**

- Reference images must be under 7MB
- Only PNG, JPEG, WebP formats supported
- Maximum 3 images for generation, 2 for editing

**Interface problems**

- Check GIMP's Error Console: `Windows → Dockable Dialogs → Error Console`
- Ensure translations are built: `python3 scripts/build-translations.py`
- Report UI issues with screenshots

### Getting Help

1. **Check the Error Console** in GIMP for specific error messages
2. **Verify all requirements** are installed correctly
3. **Test with simple prompts** first
4. **Check file permissions** on the plugin directory
5. **Review API quotas** if getting timeout errors

## Contributing

### For Translators

We welcome translations! Here's how to contribute:

1. **Copy the template**: `cp locale/dream-prompter.pot locale/[YOUR_LANG].po`
2. **Translate the strings** using Poedit, Lokalize, or any text editor
3. **Test your translation**: Build with `python3 scripts/build-translations.py`
4. **Submit a pull request** with your `.po` file

**Translation Guidelines:**

- Keep UI text concise but clear
- Use GIMP's existing terminology for your language
- Preserve HTML tags and placeholders like `{count}`, `{url}`
- Test that text fits in the interface

### For Developers

1. **Fork the repository**
2. **Create a feature branch**
3. **Follow the existing code style**
4. **Update translations** if adding new strings
5. **Submit a pull request**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Powered by Replicate's hosted image generation models.
