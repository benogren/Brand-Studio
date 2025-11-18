# Interactive Name Feedback Workflow

## Overview

An iterative feedback system that allows users to refine brand name suggestions based on their preferences before proceeding to validation and content generation.

## User Flow

```
1. Initial Generation
   ↓
2. Present Names (20-50 suggestions)
   ↓
3. Collect User Feedback
   ├─→ "I like these, proceed" → Move to validation
   ├─→ "Regenerate with feedback" → Loop back to generation
   └─→ "Refine specific aspects" → Loop back with context
```

## Feedback Types

### 1. Positive Feedback (What to Keep)
- **Specific names**: "I like options 3, 7, and 12"
- **Name elements**: "I like names with 'Flow' or 'Hub'"
- **Patterns**: "I prefer shorter names" or "I like the portmanteau style"
- **Themes**: "Keep the tech-forward feeling" or "More professional tone"

### 2. Negative Feedback (What to Avoid)
- **Disliked names**: "Remove anything with 'Pro' or 'Max'"
- **Styles**: "Too playful" or "Too corporate"
- **Patterns**: "No invented words" or "Avoid acronyms"
- **Themes**: "Less generic" or "Not enough personality"

### 3. Directional Feedback (What to Explore)
- **New directions**: "Try nature-themed names"
- **Combinations**: "Mix elements from names 5 and 8"
- **Industry shifts**: "Make it more B2B focused"
- **Tone adjustments**: "More innovative, less traditional"

### 4. Approval
- "These look great, let's move forward"
- "Proceed with validation"
- User selects specific names to validate

## Implementation Design

### A. Feedback Collection Module

```python
# src/feedback/name_feedback.py

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

class FeedbackType(Enum):
    APPROVE = "approve"  # Move to next step
    REGENERATE = "regenerate"  # Generate new batch
    REFINE = "refine"  # Refine with feedback

@dataclass
class NameFeedback:
    """User feedback on generated names."""
    feedback_type: FeedbackType

    # Positive signals
    liked_names: List[str] = None
    liked_elements: List[str] = None  # Words/parts user likes
    liked_patterns: List[str] = None  # "short", "portmanteau", etc.

    # Negative signals
    disliked_names: List[str] = None
    disliked_elements: List[str] = None
    disliked_patterns: List[str] = None

    # Directional guidance
    new_directions: List[str] = None  # New themes to explore
    tone_adjustments: str = None  # "more professional", etc.

    # Free-form feedback
    additional_feedback: str = None

    # Selected names (if approved)
    selected_names: List[str] = None
```

### B. Enhanced Orchestrator Logic

```python
# Pseudo-code for orchestrator enhancement

def generate_brand_names_with_feedback(brief: str, max_iterations: int = 3):
    """
    Generate brand names with iterative user feedback.

    Args:
        brief: Initial brand brief
        max_iterations: Max feedback loops allowed

    Returns:
        Final approved names
    """
    iteration = 0
    feedback_history = []
    current_names = []

    while iteration < max_iterations:
        # Generate names (incorporating feedback if available)
        if iteration == 0:
            # Initial generation
            names = name_generator.generate(brief)
        else:
            # Regenerate with feedback context
            names = name_generator.regenerate_with_feedback(
                brief=brief,
                previous_names=current_names,
                feedback=feedback_history[-1]
            )

        current_names = names

        # Present names to user
        display_names(names)

        # Collect feedback
        feedback = collect_user_feedback(names)
        feedback_history.append(feedback)

        if feedback.feedback_type == FeedbackType.APPROVE:
            return feedback.selected_names or names[:10]  # Top 10 if none selected

        iteration += 1

    # Max iterations reached - force approval or use best names
    return current_names[:10]
```

### C. Enhanced Name Generator Prompt

```python
# Enhanced prompt with feedback context

def build_generation_prompt_with_feedback(
    brief: str,
    feedback: Optional[NameFeedback] = None,
    previous_names: Optional[List[str]] = None
) -> str:
    """Build generation prompt incorporating user feedback."""

    prompt = f"""Generate brand names based on this brief:
{brief}

"""

    if feedback:
        # Add feedback context
        if feedback.liked_names:
            prompt += f"\nUser LIKED these names: {', '.join(feedback.liked_names)}"
            prompt += "\nGenerate more names with similar characteristics."

        if feedback.liked_elements:
            prompt += f"\nUser LIKES these elements: {', '.join(feedback.liked_elements)}"
            prompt += "\nIncorporate these elements or similar concepts."

        if feedback.disliked_names:
            prompt += f"\nUser DISLIKED these names: {', '.join(feedback.disliked_names)}"
            prompt += "\nAvoid similar patterns and styles."

        if feedback.disliked_elements:
            prompt += f"\nUser DISLIKES: {', '.join(feedback.disliked_elements)}"
            prompt += "\nDo NOT use these elements."

        if feedback.new_directions:
            prompt += f"\nUser wants to explore: {', '.join(feedback.new_directions)}"
            prompt += "\nGenerate names in these directions."

        if feedback.tone_adjustments:
            prompt += f"\nTone adjustment: {feedback.tone_adjustments}"

        if feedback.additional_feedback:
            prompt += f"\nAdditional feedback: {feedback.additional_feedback}"

    if previous_names:
        prompt += f"\n\nPreviously generated: {', '.join(previous_names[:10])}"
        prompt += "\nGenerate NEW names, avoiding duplicates."

    prompt += "\n\nGenerate 20-50 brand names..."

    return prompt
```

### D. CLI Interface for Feedback

```python
# src/cli.py - Enhanced feedback collection

def collect_feedback_interactive(names: List[str]) -> NameFeedback:
    """
    Collect user feedback on generated names (CLI).

    Interactive prompts:
    1. Show all names with numbers
    2. Ask if user wants to proceed or refine
    3. If refine, collect specific feedback
    """

    print("\n" + "="*70)
    print("Generated Brand Names:")
    print("="*70)

    for i, name in enumerate(names, 1):
        print(f"{i:2}. {name}")

    print("\n" + "="*70)
    print("What would you like to do?")
    print("1. Approve and proceed to validation")
    print("2. Regenerate names with feedback")
    print("3. Select specific names and proceed")
    print("="*70)

    choice = input("\nYour choice (1-3): ").strip()

    if choice == "1":
        return NameFeedback(
            feedback_type=FeedbackType.APPROVE,
            selected_names=names[:10]  # Top 10
        )

    elif choice == "3":
        # Select specific names
        selections = input("\nEnter numbers of names you like (e.g., 1,5,7): ")
        indices = [int(x.strip())-1 for x in selections.split(",")]
        selected = [names[i] for i in indices if 0 <= i < len(names)]

        return NameFeedback(
            feedback_type=FeedbackType.APPROVE,
            selected_names=selected
        )

    else:  # choice == "2" or default
        print("\nLet's refine the names. Please provide feedback:")

        # Liked names
        liked = input("\nWhich names do you like? (numbers, comma-separated, or 'none'): ")
        liked_names = []
        if liked.lower() != 'none':
            indices = [int(x.strip())-1 for x in liked.split(",") if x.strip()]
            liked_names = [names[i] for i in indices if 0 <= i < len(names)]

        # Liked elements
        liked_elem = input("\nWhat elements/words do you like? (comma-separated, or skip): ")
        liked_elements = [x.strip() for x in liked_elem.split(",") if x.strip()]

        # Disliked elements
        disliked_elem = input("\nWhat should we avoid? (words/themes, or skip): ")
        disliked_elements = [x.strip() for x in disliked_elem.split(",") if x.strip()]

        # New directions
        directions = input("\nAny new directions to explore? (or skip): ")
        new_directions = [x.strip() for x in directions.split(",") if x.strip()]

        # Tone adjustments
        tone = input("\nTone adjustments? (e.g., 'more professional', or skip): ")

        # Additional feedback
        additional = input("\nAny other feedback? (or skip): ")

        return NameFeedback(
            feedback_type=FeedbackType.REFINE,
            liked_names=liked_names if liked_names else None,
            liked_elements=liked_elements if liked_elements else None,
            disliked_elements=disliked_elements if disliked_elements else None,
            new_directions=new_directions if new_directions else None,
            tone_adjustments=tone if tone else None,
            additional_feedback=additional if additional else None
        )
```

## UI/UX Considerations

### For CLI:
- Clear numbering of all names
- Simple numeric selection
- Guided prompts for feedback
- Allow skipping optional feedback
- Show iteration count (e.g., "Iteration 2 of 3")

### For Future Web UI:
- Checkboxes for selecting names
- Thumbs up/down per name
- Tag cloud for elements (click to add to liked/disliked)
- Slider for tone adjustments
- Text area for free-form feedback
- "Regenerate" vs "Proceed" buttons

## Session State Management

```python
@dataclass
class NameGenerationSession:
    """Track state across feedback iterations."""
    session_id: str
    brief: str
    iteration: int = 0
    max_iterations: int = 3

    # History
    generated_names: List[List[str]] = None  # List of name batches
    feedback_history: List[NameFeedback] = None

    # Final selection
    approved_names: List[str] = None
    timestamp: str = None
```

## Example Interaction

```
=== Iteration 1 ===
Generated 30 names for "AI-powered productivity tool"

1. FlowState    11. TaskPulse   21. WorkWave
2. FocusHub     12. DoMore      22. ProActive
...

What would you like to do?
> 2 (Regenerate with feedback)

Which names do you like? > 1,5,11
What elements do you like? > Flow, Pulse
What should we avoid? > Generic words like Pro, Max
New directions? > Nature-inspired, energy-related
Tone adjustments? > More innovative, less corporate

=== Iteration 2 ===
Generated 30 refined names...

1. StreamFlow   11. VitalPulse  21. EnergySync
2. RiverTask    12. MomentumAI  22. SparkWork
...

What would you like to do?
> 1 (Approve and proceed)

Great! Proceeding with validation for top 10 names...
```

## Benefits

1. **User Control**: Users guide the creative direction
2. **Higher Satisfaction**: Names align better with preferences
3. **Efficient**: Focused refinement vs. starting over
4. **Learning**: System learns user taste over time
5. **Flexibility**: Works for both minor tweaks and major pivots

## Implementation Priority

**Phase 1 (MVP)**:
- [x] Basic feedback collection (approve/regenerate)
- [ ] Simple liked/disliked tracking
- [ ] Iteration limit (3 loops max)

**Phase 2 (Enhanced)**:
- [ ] Element extraction from feedback
- [ ] Pattern recognition (what user likes)
- [ ] Smart suggestions based on feedback

**Phase 3 (Advanced)**:
- [ ] ML-based preference learning
- [ ] Automatic similarity analysis
- [ ] Predictive suggestions

## Integration Points

1. **Orchestrator Agent**: Add feedback loop logic
2. **Name Generator Agent**: Accept feedback context
3. **CLI**: Interactive feedback collection
4. **Session Manager**: Store feedback history
5. **RAG System**: Use feedback to refine retrieval

## Next Steps

1. Implement `NameFeedback` dataclass
2. Create feedback collection module
3. Update orchestrator with loop logic
4. Enhance name generator prompt
5. Add CLI feedback interface
6. Test with sample scenarios
7. Add session persistence
