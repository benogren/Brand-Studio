# ADK Migration - Rollback Procedures

This document provides step-by-step rollback procedures for each phase of the ADK migration.

## Overview

The migration has been organized in 4 phases with git tags for easy rollback:

- **Phase 1**: Critical Foundation (Tasks 1.0-4.0)
- **Phase 2**: Tools & Memory (Tasks 5.0-8.0)
- **Phase 3**: Observability & Evaluation (Tasks 9.0-11.0)
- **Phase 4**: Deployment Readiness (Tasks 12.0-15.0)

## Git Tags

Each phase completion should be tagged:

```bash
git tag phase-1-complete
git tag phase-2-complete
git tag phase-3-complete
git tag phase-4-complete
```

## Rollback Procedures

### Rollback from Phase 4 to Phase 3

**Reason**: Deployment configuration issues or documentation errors

**Steps**:

```bash
# 1. Checkout Phase 3 completion
git checkout phase-3-complete

# 2. Delete deployment structure
rm -rf brand_studio_agent/
rm -rf scripts/deploy.sh scripts/setup_gcp.sh
rm .agent_engine_config.json

# 3. Restore previous documentation (if needed)
git checkout HEAD~1 README.md TESTING.md CLAUDE.md

# 4. Verify system still works
python -m src.main

# 5. Create rollback branch
git checkout -b rollback-to-phase-3
git commit -am "Rollback from Phase 4 to Phase 3"
```

**Verification**:
- [ ] src/main.py runs successfully
- [ ] src/cli.py works
- [ ] All tests pass: `pytest`

### Rollback from Phase 3 to Phase 2

**Reason**: LoggingPlugin issues or evaluation framework problems

**Steps**:

```bash
# 1. Checkout Phase 2 completion
git checkout phase-2-complete

# 2. Remove LoggingPlugin from App
# Edit src/main.py and src/cli.py:
# Remove: plugins=[LoggingPlugin()]
# Remove: from google.adk.plugins.logging_plugin import LoggingPlugin

# 3. Delete evaluation config (optional)
rm tests/eval_config.json

# 4. Verify system works
python -m src.main

# 5. Commit rollback
git checkout -b rollback-to-phase-2
git commit -am "Rollback from Phase 3 to Phase 2"
```

**Verification**:
- [ ] App runs without LoggingPlugin
- [ ] Context compaction still works
- [ ] All agents execute correctly

### Rollback from Phase 2 to Phase 1

**Reason**: Context compaction issues or App wrapper problems

**Steps**:

```bash
# 1. Checkout Phase 1 completion
git checkout phase-1-complete

# 2. Remove App wrapper from src/main.py and src/cli.py
# Change from:
#   app = App(name="...", root_agent=orchestrator, ...)
#   runner = InMemoryRunner(app=app)
# Back to:
#   runner = InMemoryRunner(agent=orchestrator)

# Edit src/main.py
sed -i.bak 's/runner = InMemoryRunner(app=app)/runner = InMemoryRunner(agent=orchestrator)/' src/main.py

# Edit src/cli.py
sed -i.bak 's/runner = InMemoryRunner(app=app)/runner = InMemoryRunner(agent=orchestrator)/' src/cli.py

# 3. Remove App imports
# Remove: from google.adk.apps.app import App, EventsCompactionConfig

# 4. Verify
python -m src.main

# 5. Commit
git checkout -b rollback-to-phase-1
git commit -am "Rollback from Phase 2 to Phase 1"
```

**Verification**:
- [ ] InMemoryRunner works with agent parameter
- [ ] Orchestrator executes successfully
- [ ] All agents functional

### Rollback from Phase 1 to Pre-Migration

**Reason**: Critical issues with ADK migration, need mock ADK

**Steps**:

```bash
# 1. Checkout pre-migration state
git checkout <commit-before-migration>

# 2. Restore mock_adk.py
git checkout <commit-before-migration> src/utils/mock_adk.py

# 3. Update imports to use mock ADK
# In all agent files, change:
#   from google.adk.agents import Agent
# Back to:
#   from src.utils.mock_adk import Agent

# 4. Restore BrandStudioOrchestrator class
git checkout <commit-before-migration> src/agents/orchestrator.py

# 5. Restore custom SessionManager
git checkout <commit-before-migration> src/database/session_manager.py

# 6. Update requirements.txt
# Remove: google-adk, google-genai
# Add: google-generativeai (old version)

# 7. Reinstall dependencies
pip install -r requirements.txt

# 8. Verify
python -m src.main

# 9. Commit
git checkout -b rollback-to-pre-migration
git commit -am "Complete rollback to pre-ADK state"
```

**Verification**:
- [ ] Mock ADK imports work
- [ ] BrandStudioOrchestrator class functional
- [ ] Custom SessionManager works
- [ ] All tests pass with mock ADK

## Partial Rollbacks

### Rollback LoggingPlugin Only

```bash
# Remove from src/main.py
vim src/main.py
# Delete: from google.adk.plugins.logging_plugin import LoggingPlugin
# Delete: plugins=[LoggingPlugin()] from App constructor

# Remove from src/cli.py
vim src/cli.py
# Same changes

git commit -am "Remove LoggingPlugin"
```

### Rollback Context Compaction Only

```bash
# Edit src/main.py and src/cli.py
# Remove: events_compaction_config=EventsCompactionConfig(...)
# Remove: from google.adk.apps.app import EventsCompactionConfig

git commit -am "Remove context compaction"
```

### Rollback Deployment Structure

```bash
rm -rf brand_studio_agent/
rm scripts/deploy.sh scripts/setup_gcp.sh
rm .agent_engine_config.json
git commit -am "Remove deployment structure"
```

## Emergency Procedures

### Complete System Failure

If the system is completely non-functional:

```bash
# 1. Hard reset to last known good state
git reset --hard <last-good-commit>

# 2. Force clean
git clean -fdx

# 3. Recreate venv
rm -rf venv
python -m venv venv
source venv/bin/activate

# 4. Reinstall
pip install -r requirements.txt

# 5. Test
python -m src.main
```

### Dependency Conflicts

```bash
# 1. Clear all caches
pip cache purge
rm -rf venv

# 2. Fresh install
python -m venv venv
source venv/bin/activate
pip install --no-cache-dir -r requirements.txt

# 3. Verify versions
pip freeze | grep google
```

## Rollback Verification Checklist

After any rollback, verify:

- [ ] Python imports work (no ModuleNotFoundError)
- [ ] Main entry point runs: `python -m src.main`
- [ ] CLI works: `python -m src.cli --help`
- [ ] Unit tests pass: `pytest tests/`
- [ ] Integration tests pass (if applicable)
- [ ] No errors in logs
- [ ] Agent execution completes successfully
- [ ] Tools function correctly
- [ ] Environment variables are set

## Post-Rollback Actions

1. **Document the Issue**:
   - What went wrong?
   - Which component failed?
   - Error messages and stack traces

2. **Update Task List**:
   - Mark problematic tasks as failed
   - Document blockers
   - Plan fixes

3. **Communicate**:
   - Update team on rollback
   - Share error details
   - Coordinate fix timeline

4. **Fix Forward**:
   - Address root cause
   - Test fix in isolation
   - Re-attempt migration phase

## Testing Rollback Procedures

It's recommended to test rollback procedures in a separate branch:

```bash
# Create test branch
git checkout -b test-rollback
git checkout phase-4-complete

# Perform rollback steps
./test-rollback-to-phase-3.sh

# Verify it works
python -m src.main

# Delete test branch
git checkout main
git branch -D test-rollback
```

## Recovery Best Practices

1. **Always commit before major changes**
2. **Tag phase completions for easy rollback**
3. **Keep detailed migration notes**
4. **Test rollback procedures before migration**
5. **Maintain backup of working state**
6. **Document all custom changes**

## Support

If rollback procedures fail, check:

1. **Git History**: `git log --oneline --graph`
2. **Working Tree Status**: `git status`
3. **Stashed Changes**: `git stash list`
4. **Remote State**: `git fetch && git diff origin/main`

For complex issues, consider:
- Creating a fresh clone
- Consulting migration plan: `docs/ADK_MIGRATION_PLAN.md`
- Checking ADK documentation

## References

- Migration Plan: `docs/ADK_MIGRATION_PLAN.md`
- Task List: `tasks/tasks-adk-migration-plan.md`
- Architecture Guide: `CLAUDE.md`
