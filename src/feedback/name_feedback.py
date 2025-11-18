"""
Name feedback collection and management.

Handles user feedback on generated brand names for iterative refinement.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

logger = logging.getLogger('brand_studio.name_feedback')


class FeedbackType(Enum):
    """Type of feedback action."""
    APPROVE = "approve"  # User approves names, proceed to validation
    REGENERATE = "regenerate"  # Generate completely new batch
    REFINE = "refine"  # Refine with specific feedback


@dataclass
class NameFeedback:
    """
    User feedback on generated brand names.

    Captures positive signals (what to keep), negative signals (what to avoid),
    and directional guidance (what to explore).
    """
    feedback_type: FeedbackType

    # Positive signals - what user likes
    liked_names: Optional[List[str]] = None
    liked_elements: Optional[List[str]] = None  # Words/parts user likes
    liked_patterns: Optional[List[str]] = None  # "short names", "portmanteau", etc.
    liked_themes: Optional[List[str]] = None  # "tech-forward", "professional"

    # Negative signals - what to avoid
    disliked_names: Optional[List[str]] = None
    disliked_elements: Optional[List[str]] = None  # Words/parts to avoid
    disliked_patterns: Optional[List[str]] = None  # Styles to avoid
    disliked_themes: Optional[List[str]] = None

    # Directional guidance - what to explore
    new_directions: Optional[List[str]] = None  # New themes to explore
    tone_adjustments: Optional[str] = None  # "more professional", "more playful"
    style_preferences: Optional[List[str]] = None  # Preferred naming strategies

    # Free-form feedback
    additional_feedback: Optional[str] = None

    # Selected names (if approved)
    selected_names: Optional[List[str]] = None

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_prompt_context(self) -> str:
        """
        Convert feedback to prompt context for name generator.

        Returns:
            Formatted string with feedback for LLM prompt
        """
        context_parts = []

        if self.liked_names:
            context_parts.append(
                f"POSITIVE SIGNALS - User LIKED these names: {', '.join(self.liked_names)}\n"
                f"Generate more names with similar characteristics."
            )

        if self.liked_elements:
            context_parts.append(
                f"LIKED ELEMENTS: {', '.join(self.liked_elements)}\n"
                f"Incorporate these elements or similar concepts in new names."
            )

        if self.liked_patterns:
            context_parts.append(
                f"LIKED PATTERNS: {', '.join(self.liked_patterns)}\n"
                f"Follow these patterns in new suggestions."
            )

        if self.liked_themes:
            context_parts.append(
                f"LIKED THEMES: {', '.join(self.liked_themes)}\n"
                f"Maintain these thematic elements."
            )

        if self.disliked_names:
            context_parts.append(
                f"NEGATIVE SIGNALS - User DISLIKED: {', '.join(self.disliked_names)}\n"
                f"Avoid similar patterns, styles, and characteristics."
            )

        if self.disliked_elements:
            context_parts.append(
                f"AVOID these elements: {', '.join(self.disliked_elements)}\n"
                f"Do NOT use these words or similar concepts."
            )

        if self.disliked_patterns:
            context_parts.append(
                f"AVOID these patterns: {', '.join(self.disliked_patterns)}"
            )

        if self.new_directions:
            context_parts.append(
                f"NEW DIRECTIONS to explore: {', '.join(self.new_directions)}\n"
                f"Generate names exploring these new themes and concepts."
            )

        if self.tone_adjustments:
            context_parts.append(
                f"TONE ADJUSTMENT: {self.tone_adjustments}\n"
                f"Adjust the overall tone and style of suggestions accordingly."
            )

        if self.style_preferences:
            context_parts.append(
                f"PREFERRED STYLES: {', '.join(self.style_preferences)}\n"
                f"Focus on these naming strategies."
            )

        if self.additional_feedback:
            context_parts.append(
                f"ADDITIONAL FEEDBACK: {self.additional_feedback}"
            )

        return "\n\n".join(context_parts)


@dataclass
class NameGenerationSession:
    """
    Tracks state across feedback iterations for a single brand naming session.
    """
    session_id: str
    brief: str
    iteration: int = 0
    max_iterations: int = 3

    # History
    generated_names: List[List[str]] = field(default_factory=list)
    feedback_history: List[NameFeedback] = field(default_factory=list)

    # Final selection
    approved_names: Optional[List[str]] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None

    def add_generation(self, names: List[str]) -> None:
        """Add a batch of generated names to history."""
        self.generated_names.append(names)
        self.iteration += 1
        logger.info(f"Session {self.session_id}: Added iteration {self.iteration} with {len(names)} names")

    def add_feedback(self, feedback: NameFeedback) -> None:
        """Add user feedback to history."""
        self.feedback_history.append(feedback)
        logger.info(f"Session {self.session_id}: Added feedback type={feedback.feedback_type.value}")

    def approve(self, names: List[str]) -> None:
        """Mark session as approved with final name selection."""
        self.approved_names = names
        self.completed_at = datetime.utcnow().isoformat()
        logger.info(f"Session {self.session_id}: Approved {len(names)} names")

    def is_complete(self) -> bool:
        """Check if session is complete."""
        return self.approved_names is not None

    def has_iterations_remaining(self) -> bool:
        """Check if more iterations are allowed."""
        return self.iteration < self.max_iterations


def collect_feedback_interactive(names: List[str], iteration: int = 1, max_iterations: int = 3) -> NameFeedback:
    """
    Collect user feedback on generated names (CLI interface).

    Args:
        names: List of generated brand names
        iteration: Current iteration number
        max_iterations: Maximum iterations allowed

    Returns:
        NameFeedback object with user's feedback
    """
    print("\n" + "=" * 70)
    print(f"Generated Brand Names (Iteration {iteration}/{max_iterations})")
    print("=" * 70)

    # Display names in columns for better readability
    for i in range(0, len(names), 2):
        left = f"{i+1:2}. {names[i]:30}"
        right = f"{i+2:2}. {names[i+1]:30}" if i+1 < len(names) else ""
        print(f"{left}  {right}")

    print("\n" + "=" * 70)
    print("What would you like to do?")
    print("=" * 70)
    print("1. Select names and proceed to validation")
    print("2. Regenerate names with feedback")
    if iteration < max_iterations:
        print("3. Generate a completely fresh batch (ignore previous)")
    print("=" * 70)

    choice = input("\nYour choice: ").strip()

    # Option 1: Select names and proceed
    if choice == "1":
        while True:
            selections = input("\nEnter numbers of names you like (at least 1, e.g., 1,5,7,12) or 'all' for top 10: ").strip()

            if selections.lower() == 'all':
                selected = names[:10]
                logger.info("User approved top 10 names")
                break
            else:
                try:
                    indices = [int(x.strip()) - 1 for x in selections.split(",")]
                    selected = [names[i] for i in indices if 0 <= i < len(names)]

                    if not selected:
                        print("⚠️  No valid selections. Please enter at least one valid number.\n")
                        continue

                    logger.info(f"User selected {len(selected)} specific names")
                    break
                except (ValueError, IndexError) as e:
                    print(f"⚠️  Invalid input: {e}. Please enter comma-separated numbers (e.g., 1,5,7).\n")
                    continue

        return NameFeedback(
            feedback_type=FeedbackType.APPROVE,
            selected_names=selected
        )

    # Option 3: Completely fresh regeneration
    elif choice == "3" and iteration < max_iterations:
        logger.info("User requested fresh generation")
        return NameFeedback(
            feedback_type=FeedbackType.REGENERATE,
            additional_feedback="Generate completely new names, fresh start"
        )

    # Option 2 (default): Refine with feedback
    else:
        print("\n" + "=" * 70)
        print("Let's refine the names. Provide feedback:")
        print("(Press Enter to skip any question)")
        print("=" * 70)

        # Liked names
        liked_input = input("\n🟢 Which names do you like? (numbers, comma-separated): ").strip()
        liked_names = []
        if liked_input:
            try:
                indices = [int(x.strip()) - 1 for x in liked_input.split(",")]
                liked_names = [names[i] for i in indices if 0 <= i < len(names)]
            except (ValueError, IndexError):
                print("⚠️  Invalid format, skipping")

        # Liked elements
        liked_elem = input("🟢 What elements/words do you like? (comma-separated): ").strip()
        liked_elements = [x.strip() for x in liked_elem.split(",") if x.strip()] if liked_elem else None

        # Disliked elements
        disliked_elem = input("🔴 What should we avoid? (words/themes): ").strip()
        disliked_elements = [x.strip() for x in disliked_elem.split(",") if x.strip()] if disliked_elem else None

        # New directions
        directions = input("🔵 Any new directions to explore? (themes/concepts): ").strip()
        new_directions = [x.strip() for x in directions.split(",") if x.strip()] if directions else None

        # Tone adjustments
        tone = input("🎨 Tone adjustments? (e.g., 'more professional', 'more playful'): ").strip()

        # Additional feedback
        additional = input("💬 Any other feedback? ").strip()

        logger.info("User provided refinement feedback")
        return NameFeedback(
            feedback_type=FeedbackType.REFINE,
            liked_names=liked_names if liked_names else None,
            liked_elements=liked_elements,
            disliked_elements=disliked_elements,
            new_directions=new_directions,
            tone_adjustments=tone if tone else None,
            additional_feedback=additional if additional else None
        )


def build_feedback_summary(feedback_history: List[NameFeedback]) -> str:
    """
    Build a summary of all feedback for context.

    Args:
        feedback_history: List of feedback from all iterations

    Returns:
        Summary string for prompt context
    """
    if not feedback_history:
        return ""

    summary_parts = ["\n=== FEEDBACK HISTORY ===\n"]

    for i, feedback in enumerate(feedback_history, 1):
        summary_parts.append(f"\nIteration {i}:")
        summary_parts.append(feedback.to_prompt_context())

    return "\n".join(summary_parts)


def collect_post_validation_choice(validated_names: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Collect user choice after validation stage.

    Presents three options:
    1. Regenerate new names (completely fresh batch)
    2. Regenerate with feedback (refine existing names)
    3. Select names for brand narrative generation

    Args:
        validated_names: List of validated brand name dictionaries with metadata

    Returns:
        Dictionary with:
        - choice: 'regenerate', 'feedback', or 'narrative'
        - selected_names: List of selected names (if choice is 'narrative')
        - feedback: NameFeedback object (if choice is 'feedback')
    """
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)

    print("\nWhat would you like to do next?")
    print("=" * 70)
    print("1. Generate completely new names (fresh start)")
    print("2. Regenerate names with feedback (refine these names)")
    print("3. Select names to create brand narratives")
    print("=" * 70)

    while True:
        try:
            choice = input("\nYour choice (1-3): ").strip()

            if choice == '1':
                # Regenerate completely new names
                return {
                    'choice': 'regenerate',
                    'feedback': NameFeedback(
                        feedback_type=FeedbackType.REGENERATE,
                        general_comments="User requested completely new batch after validation"
                    )
                }

            elif choice == '2':
                # Collect feedback for refinement
                print("\n" + "=" * 70)
                print("PROVIDE FEEDBACK FOR REFINEMENT")
                print("=" * 70)

                # Show current names for reference
                print("\nCurrent validated names:")
                for i, name_data in enumerate(validated_names, 1):
                    brand_name = name_data.get('brand_name', 'Unknown')
                    print(f"  {i}. {brand_name}")

                # Collect feedback similar to the iterative feedback
                liked_input = input("\nWhich names do you like? (comma-separated numbers, or press Enter to skip): ").strip()
                liked_names = []
                if liked_input:
                    try:
                        indices = [int(x.strip()) - 1 for x in liked_input.split(',')]
                        liked_names = [validated_names[i]['brand_name'] for i in indices if 0 <= i < len(validated_names)]
                    except (ValueError, IndexError):
                        print("⚠️  Invalid input, skipping liked names.")

                disliked_input = input("Which names should we avoid? (comma-separated numbers, or press Enter to skip): ").strip()
                disliked_names = []
                if disliked_input:
                    try:
                        indices = [int(x.strip()) - 1 for x in disliked_input.split(',')]
                        disliked_names = [validated_names[i]['brand_name'] for i in indices if 0 <= i < len(validated_names)]
                    except (ValueError, IndexError):
                        print("⚠️  Invalid input, skipping disliked names.")

                new_directions = input("\nWhat new themes or directions should we explore? (optional): ").strip()
                tone_adjustment = input("Any tone adjustments? (e.g., 'more professional', 'shorter', 'more creative'): ").strip()

                feedback = NameFeedback(
                    feedback_type=FeedbackType.REFINE,
                    liked_names=liked_names if liked_names else None,
                    disliked_names=disliked_names if disliked_names else None,
                    new_directions=[new_directions] if new_directions else None,
                    tone_adjustments=tone_adjustment if tone_adjustment else None
                )

                return {
                    'choice': 'feedback',
                    'feedback': feedback
                }

            elif choice == '3':
                # Select names for brand narrative generation
                print("\n" + "=" * 70)
                print("SELECT NAMES FOR BRAND NARRATIVE")
                print("=" * 70)

                print("\nValidated names:")
                for i, name_data in enumerate(validated_names, 1):
                    brand_name = name_data.get('brand_name', 'Unknown')
                    strategy = name_data.get('naming_strategy', 'N/A')
                    tagline = name_data.get('tagline', 'N/A')
                    print(f"  {i}. {brand_name} ({strategy})")
                    print(f"     \"{tagline}\"")

                while True:
                    selection_input = input("\nEnter numbers of names to create narratives for (comma-separated, e.g., 1,3,5): ").strip()

                    try:
                        indices = [int(x.strip()) - 1 for x in selection_input.split(',')]

                        # Validate indices
                        if not all(0 <= i < len(validated_names) for i in indices):
                            print("⚠️  Some numbers are out of range. Please try again.")
                            continue

                        if len(indices) == 0:
                            print("⚠️  Please select at least one name.")
                            continue

                        # Get selected names
                        selected_names = [validated_names[i] for i in indices]

                        print(f"\n✓ Selected {len(selected_names)} name(s) for brand narrative generation")

                        return {
                            'choice': 'narrative',
                            'selected_names': selected_names
                        }

                    except (ValueError, IndexError):
                        print("⚠️  Invalid input. Please enter comma-separated numbers.")
                        continue

            else:
                print("⚠️  Please enter 1, 2, or 3.")
                continue

        except EOFError:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"Error collecting post-validation choice: {e}")
            print(f"⚠️  Error: {e}")
            continue
