# Dream Prompter - GIMP Plugin

**This is a WIP fork of [the original Dream Prompter GIMP plugin by zquests](https://github.com/zquestz/dream-prompter).**

This plugin brings Replicate-hosted image generation models directly into GIMP for intelligent image creation and editing. Switch between Replicate model versions to explore different aesthetics without leaving your editing workflow.

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

1. **Download the latest release**

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
