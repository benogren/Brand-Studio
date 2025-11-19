# Interactive CLI Guide

## Overview

The Brand Studio now has an **interactive, session-based CLI** that implements the correct workflow with user choice points.

Based on ADK Day 3 patterns (session management + state persistence).

## Workflow

```
1. generate → Generate 10-20 names
         ↓
2. USER CHOICE:
   - feedback → Provide feedback & regenerate (keeps context)
   - validate → Check domain/trademark/SEO
         ↓
3. validate → Run all validation checks
         ↓
4. USER CHOICE:
   - generate/feedback → Start over with context
   - story → Generate final brand story
         ↓
5. story → Taglines + Brand Story + Value Prop
```

## Commands

### 1. Generate Initial Names

```bash
python -m src.cli_interactive generate \
  --session my-brand \
  --product "AI fitness tracking app" \
  --personality innovative \
  --industry fitness \
  --count 15
```

**What it does:**
- Runs research agent
- Generates 10-20 brand names
- Saves to session state
- Shows next step options

### 2. Provide Feedback & Regenerate

```bash
python -m src.cli_interactive feedback \
  --session my-brand \
  --feedback "I like tech-focused names with strong verbs" \
  --keep "KinetiCore,Evolve.AI" \
  --count 10
```

**What it does:**
- Stores feedback in session
- Keeps names you liked
- Generates new names based on feedback
- Appends to existing names (doesn't replace)

**Can be run multiple times** for iterative refinement!

### 3. Validate Selected Names

```bash
python -m src.cli_interactive validate \
  --session my-brand \
  --names "KinetiCore,Evolve.AI,IntelliFit"
```

**What it does:**
- Domain availability check (.com, .ai, .io)
- Trademark search (USPTO)
- SEO analysis
- Search result collision check
- Saves validation results to session

### 4. Generate Brand Story

```bash
python -m src.cli_interactive story \
  --session my-brand \
  --name "KinetiCore"
```

**What it does:**
- Creates 5 tagline options (5-8 words each)
- Generates brand story (200-300 words)
- Creates value proposition (20-30 words)
- Marks session as complete

## Utility Commands

### Show Session Status

```bash
python -m src.cli_interactive status --session my-brand
```

Shows:
- Current workflow step
- Product info
- Number of generated names
- Feedback rounds
- Selected names

### List All Sessions

```bash
python -m src.cli_interactive list
```

Shows all active sessions with their status.

### Delete Session

```bash
python -m src.cli_interactive delete --session my-brand
```

Removes session and all state.

## Example Complete Workflow

```bash
# 1. Generate initial names
python -m src.cli_interactive generate \
  --session fitness-brand \
  --product "AI fitness tracking app" \
  --personality innovative \
  --industry fitness

# 2. Review names, provide feedback (optional, can skip to validate)
python -m src.cli_interactive feedback \
  --session fitness-brand \
  --feedback "More focus on movement and intelligence" \
  --keep "KinetiCore,FlowFit"

# 3. Validate top candidates
python -m src.cli_interactive validate \
  --session fitness-brand \
  --names "KinetiCore,FlowFit,CogniFit"

# 4. Check status
python -m src.cli_interactive status --session fitness-brand

# 5. Generate brand story for chosen name
python -m src.cli_interactive story \
  --session fitness-brand \
  --name "KinetiCore"
```

## Session Storage

Sessions are stored in `.brand-sessions/` as JSON files.

Each session contains:
- Product information
- Research insights
- All generated names (across multiple rounds)
- Feedback history
- Selected names
- Validation results
- Brand story

## Advantages Over Old CLI

| Feature | Old CLI | New Interactive CLI |
|---------|---------|---------------------|
| User choice points | ❌ None | ✅ After each step |
| Feedback loop | ❌ No | ✅ Yes, iterative |
| Session persistence | ❌ No | ✅ Yes, file-based |
| Workflow control | ❌ Fully automated | ✅ User-driven |
| Multiple iterations | ❌ No | ✅ Unlimited feedback rounds |
| Resume later | ❌ No | ✅ Yes, via session ID |

## Technical Implementation

Follows ADK coursework patterns:

1. **Day 3 Session Management**: File-based JSON storage
2. **State Persistence**: All workflow data saved between commands
3. **Agent Isolation**: Each command runs specific agents independently
4. **InMemoryRunner**: Simple execution without complex session services

## Next Steps

After testing the interactive CLI:

1. Improve name parsing from agent outputs (currently stores raw text)
2. Add formatted display of generated names
3. Implement proper JSON parsing for structured data
4. Add export command to save final brand identity
5. Consider adding web UI for visualization

## Troubleshooting

**Session not found:**
```bash
# Check if session exists
python -m src.cli_interactive list

# Create new session
python -m src.cli_interactive generate --session new-session ...
```

**Want to start over:**
```bash
# Delete old session
python -m src.cli_interactive delete --session my-brand

# Start fresh
python -m src.cli_interactive generate --session my-brand ...
```

**See detailed agent output:**
```bash
# Add --verbose flag to any command
python -m src.cli_interactive generate --session test --verbose ...
```
