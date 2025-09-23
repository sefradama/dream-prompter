# Dream Prompter System Patterns

## Architecture Overview
The application follows a modular architecture with clear separation of concerns:
- **GUI Layer**: GTK-based user interface components
- **Business Logic Layer**: Core prompt management and processing
- **Integration Layer**: External service and API connections
- **Data Layer**: Settings management and prompt storage

## Core Design Patterns

### Dialog-Based Interaction
- Uses GTK dialog system for user interactions
- Modular dialog components for different functionalities
- Event-driven communication between dialogs

### Thread-Based Processing
- Asynchronous operations to maintain UI responsiveness
- Thread management for long-running tasks
- Event-based communication between threads

### Internationalization (i18n)
- gettext-based translation system
- PO file management for multiple languages
- Runtime language switching capabilities

### Settings Management
- Centralized configuration system
- Persistent settings storage
- Type-safe setting access

## Component Relationships

### Main Components
1. **dream-prompter.py** - Main application entry point
2. **dialog.py** - Base dialog functionality
3. **dialog_gtk.py** - GTK-specific dialog implementations
4. **dialog_events.py** - Event handling system
5. **dialog_threads.py** - Threading and async processing
6. **settings.py** - Configuration management
7. **i18n.py** - Internationalization support

### Integration Points
- **GIMP Integration**: Plugin interface for image processing workflows
- **Replicate API**: Connection to AI model platforms
- **File System**: Local prompt storage and management

## Data Flow Patterns

### Prompt Creation Flow
```
User Input → Dialog Processing → Prompt Generation → Model Integration → Result Display
```

### Settings Management Flow
```
Settings Load → Runtime Configuration → UI Updates → Persistent Storage
```

### Internationalization Flow
```
Language Selection → Resource Loading → UI Text Replacement → Runtime Updates
```

## Error Handling Patterns
- Graceful degradation for optional features
- User-friendly error messages
- Logging for debugging and monitoring
- Recovery mechanisms for failed operations

## Extensibility Patterns
- Plugin architecture for new AI models
- Modular dialog system for new features
- Configuration-driven behavior customization
- API abstraction for external integrations
