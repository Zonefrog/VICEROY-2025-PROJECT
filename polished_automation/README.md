# VICEROY-2025-PROJECT: Polished Automation Core

## Overview

This is a clean, polished implementation of the setup and initialization phase for the VICEROY-2025-PROJECT AI-powered presentation generation system. This module handles all configuration, path setup, API initialization, and system preparation **before any AI prompts are executed**.

## Architecture

The polished automation core is built around several key components:

### 1. SystemConfig (dataclass)
Centralized configuration management for all system parameters:
- API settings (calls, model, temperature)
- Database configuration
- Presentation settings
- Input/output modes
- Logging preferences

### 2. PathManager
Handles all file and directory path management:
- API key file location
- Results, logs, and test output directories
- Automatic directory creation
- Log file path generation

### 3. APIManager
Manages OpenAI API interactions:
- Client initialization and validation
- Call limit tracking and enforcement
- Error handling and retry logic
- Usage monitoring and reporting
- **Manual API mode**: Copy/paste prompts and responses for external AI services

### 4. LoggingManager
Comprehensive logging system:
- Log file initialization with timestamps
- Configuration state logging
- Console and file output control
- Error tracking and reporting

### 5. DatabaseManager
Knowledge database initialization:
- AI database setup with configurable size limits
- Entry management preparation
- Search functionality initialization

### 6. PromptManager
Prompt input and processing:
- Multiple input modes (manual, hardcoded, file)
- AI-powered prompt rewriting
- Input validation and error handling

### 7. AutomationCore
Main orchestrator that coordinates all components:
- Sequential initialization of all subsystems
- State management and validation
- User confirmation handling
- System state reporting

## Key Improvements Over Original

### 1. **Separation of Concerns**
- Each component has a single, well-defined responsibility
- Clear interfaces between components
- Reduced coupling and improved maintainability

### 2. **Error Handling**
- Comprehensive exception handling at each level
- Meaningful error messages with context
- Graceful degradation when possible

### 3. **Configuration Management**
- Centralized configuration in a dataclass
- Type hints for better IDE support
- Easy modification of system parameters

### 4. **Resource Management**
- Proper initialization order
- Resource cleanup and validation
- Memory and API call efficiency

### 5. **Logging and Monitoring**
- Detailed logging of all operations
- System state tracking
- Performance monitoring capabilities

### 6. **Extensibility**
- Modular design allows easy addition of new features
- Clear interfaces for component replacement
- Configuration-driven behavior

### 7. **Manual API Mode**
- Support for external AI services via copy/paste interface
- No API key required when using manual mode
- Automatic retry on empty or accidental inputs ('v', 'V')
- Clear prompt display and response validation

### 8. **Complete Setup Flow**
- Comprehensive preparation for presentation generation
- Automatic calculation of research parameters
- Generation context preparation with all necessary data
- Step 1 prompt creation and formatting
- Ready-to-execute state for the main generation process

### 9. **Step 1 and Step 2 Execution**
- **Step 1**: Generate initial research topics via AI call
- **Step 2**: Research topics and populate knowledge database
- Automatic parsing and validation of AI responses
- Database entry management with proper error handling
- Progress tracking and detailed logging

## Usage

### Basic Usage

```python
from automation_core import AutomationCore, SystemConfig

# Create configuration
config = SystemConfig(
    max_api_calls=1000,
    slide_count_target=50,
    input_mode=2
)

# Initialize the system
core = AutomationCore(config)
if core.initialize():
    # Get the initial prompt
    prompt = core.get_initial_prompt()
    print(f"Retrieved prompt: {prompt}")
    
    # Get system state
    state = core.get_system_state()
    print(f"System state: {state}")
```

### Custom Configuration

```python
# Create custom configuration
config = SystemConfig(
    max_api_calls=500,
    slide_count_target=30,
    input_mode=1,  # Manual input
    rewrite_prompt=True,
    suppress_logs=False
)

core = AutomationCore(config)
```

### Manual API Mode

```python
# Enable manual API mode for external AI services
config = SystemConfig(
    max_api_calls=100,
    use_manual_api=True,  # Enable manual mode
    input_mode=2
)

core = AutomationCore(config)
if core.initialize():
    # When making API calls, user will be prompted to:
    # 1. Copy the prompt to their AI service
    # 2. Paste the response back
    # 3. Empty responses and 'v'/'V' inputs are automatically retried
    response = core.api_manager.make_call("What is 2+2?")
```

### Complete Setup Flow

```python
# Complete setup flow up to Step 1
config = SystemConfig(
    max_api_calls=100,
    slide_count_target=50,
    input_mode=2
)

core = AutomationCore(config)
if core.initialize():
    # Prepare for presentation generation
    generation_context = core.prepare_for_presentation_generation()
    
    # Create Step 1 prompt
    step_1_prompt = core.create_step_1_prompt(generation_context)
    
    # Now ready to execute Step 1
    print("Ready for Step 1 execution!")
    
    # Access all prepared data
    print(f"Initial topics: {generation_context['initial_topic_count']}")
    print(f"Database entries per topic: {generation_context['database_entries_per_topic']}")
    print(f"API manager: {generation_context['api_manager']}")
```

### Step 1 and Step 2 Execution

```python
# Execute Step 1 and Step 2
config = SystemConfig(
    max_api_calls=100,
    slide_count_target=50,
    input_mode=2
)

core = AutomationCore(config)
if core.initialize():
    # Prepare for generation
    generation_context = core.prepare_for_presentation_generation()
    
    # Execute Step 1: Generate research topics
    topics = core.execute_step_1(generation_context)
    print(f"Generated {len(topics)} topics: {topics}")
    
    # Execute Step 2: Research topics and populate database
    core.execute_step_2(generation_context, topics)
    print(f"Database now has {len(generation_context['knowledge_db'].entries)} entries")
    
    # Execute Step 3: Generate additional topics based on research
    additional_topics = core.execute_step_3(generation_context, topics)
    print(f"Generated {len(additional_topics)} additional topics")
    
    # Execute Step 4: Research additional topics
    core.execute_step_4(generation_context, additional_topics)
    print(f"Database now has {len(generation_context['knowledge_db'].entries)} total entries")
    
    # Execute Step 5: Plan presentation structure
    step_5_result = core.execute_step_5(generation_context)
    print(f"Created presentation structure with {step_5_result['total_topics_count']} topics")
    
    # Execute Step 6: Create presentation object
    presentation = core.execute_step_6(generation_context, step_5_result["presentation_topics_list"])
    print(f"Created presentation with {len(presentation.slides)} slides")
    
    # Execute Step 7: Generate slide content themes
    updated_presentation = core.execute_step_7(generation_context, step_4_5_result["slide_topics_list"], presentation)
    print(f"Generated content themes for {len(updated_presentation.slides)} slides")
    
    # Execute Step 8: Generate slide titles and overall presentation title
    final_presentation = core.execute_step_8(generation_context, step_4_5_result["slide_topics_list"], updated_presentation)
    print(f"Generated titles for {len(final_presentation.slides)} slides and overall presentation")
    
    # Execute Step 9: Associate sources and enhance content
    enhanced_presentation = core.execute_step_9(generation_context, step_4_5_result["slide_topics_list"], step_4_5_result["teaching_outline"], final_presentation)
    print(f"Associated sources and enhanced content for {len(enhanced_presentation.slides)} slides")
    
    # Execute Step 10: Finalize presentation structure
    finalized_presentation = core.execute_step_10(enhanced_presentation)
    print(f"Finalized presentation with {len(finalized_presentation.slides)} total slides")
    
    # Execute Step 11: Save presentation to file
    saved_file_path = core.execute_step_11(finalized_presentation)
    print(f"Presentation saved to {saved_file_path}")
```

### Component Access

```python
# Access individual components after initialization
if core.is_initialized:
    api_manager = core.api_manager
    database = core.database_manager.database
    path_manager = core.path_manager
```

## File Structure

```
polished_automation/
├── automation_core.py    # Main implementation
├── README.md            # This documentation
└── requirements.txt     # Dependencies (if needed)
```

## Dependencies

The polished automation core requires the following dependencies from the original project:
- `ai_database.py`
- `logging_funcs.py`
- `openai` library
- Standard Python libraries (os, sys, datetime, pathlib, typing, dataclasses)

## Configuration Options

### SystemConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_api_calls` | int | 1000 | Maximum OpenAI API calls allowed |
| `openai_model` | str | "gpt-3.5-turbo" | OpenAI model to use |
| `temperature` | float | 0.6 | AI response randomness |
| `use_manual_api` | bool | False | Enable manual copy/paste API mode |
| `knowledge_db_name` | str | "Knowledge Database" | Database name |
| `knowledge_db_max_size` | int | 80 | Maximum database entries |
| `slide_count_target` | int | 50 | Target number of slides |
| `input_mode` | int | 2 | 1=manual, 2=hardcoded, 3=file |
| `rewrite_prompt` | bool | False | Use AI to rewrite prompts |
| `suppress_logs` | bool | False | Disable file logging |
| `suppress_prints` | bool | False | Disable console output |

## Error Handling

The system provides comprehensive error handling:

1. **Initialization Errors**: Clear error messages for missing files, invalid configurations
2. **API Errors**: Graceful handling of network issues, rate limits, authentication failures
3. **File System Errors**: Proper handling of missing directories, permission issues
4. **Configuration Errors**: Validation of all configuration parameters

## Testing

The main function includes basic testing capabilities:

```python
if __name__ == "__main__":
    sys.exit(main())
```

This allows the module to be run directly for testing initialization and basic functionality.

## Integration

This polished automation core is designed to integrate seamlessly with the existing VICEROY-2025-PROJECT system. It can replace the setup functions in the original `automation program.py` while maintaining compatibility with the rest of the codebase.

## Future Enhancements

Potential improvements for future versions:
1. Configuration file support (JSON/YAML)
2. Environment variable configuration
3. Advanced logging with different levels
4. Performance metrics collection
5. Plugin system for custom components
6. Unit test suite
7. Configuration validation schemas
