# Warning Suppression in CLI

The following warnings have been suppressed in `src/cli.py` for a cleaner user experience:

## Suppressed Warnings

1. **App name mismatch detected** - Harmless ADK warning about runner configuration vs agent loading path
2. **Non-text parts in the response** - Expected behavior when agents use function calling (we extract only text)
3. **ADK LoggingPlugin not available** - Informational message about optional plugin

## Implementation

- Added `warnings.filterwarnings()` to suppress Python warnings
- Created `SuppressStderr` context manager to capture stderr during agent execution
- Configured `logging.getLogger('google.adk').setLevel(logging.ERROR)` to suppress debug messages

## Technical Details

These warnings appear because:
- **App name mismatch**: InMemoryRunner vs agent package structure - doesn't affect functionality
- **Non-text parts**: Agents use function calling, so responses contain both text and function_call objects - we intentionally extract only text
- **LoggingPlugin**: Optional ADK plugin for enhanced logging - not required for basic operation

All warnings are cosmetic and don't affect the brand generation process.
