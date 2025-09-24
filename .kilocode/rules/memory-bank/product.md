# Product Description

## Why This Project Exists

Dream Prompter bridges the gap between traditional image editing workflows and modern AI-powered image generation and manipulation. It brings Replicate-hosted AI models directly into GIMP, allowing artists and designers to leverage cutting-edge AI capabilities without leaving their familiar editing environment.

## Problems It Solves

1. **Workflow Disruption**: Traditional AI image tools require users to export images from GIMP, process them externally, then re-import - breaking creative flow and introducing format conversion issues.

2. **Limited Access**: Many users lack the technical expertise or resources to set up and maintain separate AI processing pipelines.

3. **Cost and Complexity**: External AI services often require separate accounts, billing management, and technical setup that distracts from creative work.

4. **Integration Gaps**: Existing AI tools don't understand GIMP's layer system, selections, or native image formats.

## How It Should Work

### Core Functionality
- **Seamless Integration**: Appears as a native GIMP filter under `Filters → AI → Dream Prompter...`
- **Dual Modes**: 
  - **Edit Mode**: Transform existing layers/images using AI
  - **Generate Mode**: Create new images from text prompts
- **Reference Images**: Support for additional reference images to guide AI generation/editing
- **Real-time Feedback**: Progress indicators and status updates during AI processing

### User Workflow
1. Open/create image in GIMP
2. Select `Filters → AI → Dream Prompter...`
3. Enter Replicate API key (saved securely)
4. Choose mode (edit/generate)
5. Enter descriptive prompt
6. Optionally add reference images
7. Click generate - new layer appears automatically
8. Continue editing in GIMP

## User Experience Goals

### Seamless Integration
- Native GIMP feel with consistent UI patterns
- Automatic layer creation and positioning
- Preservation of GIMP's undo/redo system
- Support for selections and layer masks

### Accessibility
- Clear, jargon-free interface
- Comprehensive error messages and troubleshooting
- Multi-language support (i18n ready)
- Cross-platform compatibility (Linux/macOS/Windows)

### Performance
- Non-blocking UI during AI processing
- Efficient memory usage for large images
- Smart caching and validation
- Graceful handling of API limits and failures

### Security & Privacy
- Encrypted storage of API credentials
- Secure image transmission to Replicate
- Clear cost visibility and usage tracking
- No data retention beyond processing

### Flexibility
- Support for multiple Replicate models
- Configurable parameters per model
- Extensible architecture for new AI capabilities
- Backward compatibility with existing workflows