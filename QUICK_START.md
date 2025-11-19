# Quick Start - Testing the ADK Migration

## ✅ Verification Complete!

Your system has been verified and is ready to use. All ADK components are working correctly.

## 🚀 Running the System

### Option 1: Interactive CLI (Recommended for Testing)

The interactive CLI lets you test with custom inputs:

```bash
python -m src.cli
```

Follow the prompts to enter:
- Product description
- Target audience  
- Brand personality (playful, professional, innovative, luxury)
- Industry category

**Or use command-line arguments:**

```bash
python -m src.cli \
  --product "AI-powered fitness tracking app" \
  --audience "Health-conscious millennials" \
  --personality innovative \
  --industry fitness \
  --verbose
```

###Option 2: Run the Full Pipeline

This runs with a pre-configured example (meal planning app):

```bash
python -m src.main
```

**What it does:**
1. Research Agent analyzes the industry
2. Name Generator creates 20-50 brand names
3. Validation Agent checks domains and trademarks
4. SEO Agent optimizes meta tags
5. Story Agent creates brand narrative

**Expected duration:** 1-3 minutes (makes real API calls)

## 📊 What You'll See

### Successful Output Structure:

```
AI BRAND STUDIO
============================================================
Loading configuration...
✓ Project: brand-agent-478519
✓ Location: us-central1

Initializing ADK orchestrator...
✓ Orchestrator initialized with ADK workflow patterns

Creating App with context compaction...
✓ App created with context compaction and LoggingPlugin enabled

EXECUTING WORKFLOW
------------------------------------------------------------
[Research phase...]
[Name generation phase...]
[Validation phase...]
[SEO optimization phase...]
[Brand story phase...]

BRAND IDENTITY GENERATED
============================================================
[Generated names, validation results, SEO data, brand story...]
```

## ⚠️ Known Warnings (Safe to Ignore)

You may see these warnings - they're expected and don't affect functionality:

1. **"Warning: ADK LoggingPlugin not available"** - From old custom logger code, doesn't affect the real LoggingPlugin
2. **"[EXPERIMENTAL] EventsCompactionConfig"** - Context compaction is experimental but stable
3. **"App name mismatch detected"** - Informational warning about ADK agent loading paths

## 🧪 Running Tests

### Quick Component Test:
```bash
python verify_setup.py
```

### Full Test Suite:
```bash
pytest tests/ -v
```

### Specific Tests:
```bash
# Test orchestrator
pytest tests/test_orchestrator.py

# Test agents
pytest tests/test_name_generator.py

# Test tools
pytest tests/test_domain_checker.py
```

## 🐛 Troubleshooting

### "No module named 'google.adk'"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "GOOGLE_CLOUD_PROJECT not set"
Check your `.env` file has:
```
GOOGLE_CLOUD_PROJECT=brand-agent-478519
GOOGLE_GENAI_USE_VERTEXAI=1
```

### Import Errors
```bash
# Ensure you're in the project root
cd /Users/benogren/Desktop/projects/Brand-Agent

# Activate venv
source venv/bin/activate

# Run from project root
python -m src.cli
```

### API Rate Limiting
If you hit rate limits:
- Wait a few minutes
- The system has automatic retry logic (5 attempts)
- Check your GCP quota: https://console.cloud.google.com/apis/api/aiplatform.googleapis.com/quotas

## 📈 Performance Expectations

- **Quick test (5 names):** ~30-60 seconds
- **Full pipeline (20-50 names):** ~1-3 minutes
- **With validation:** +30-60 seconds (domain/trademark checks)

## 🎯 Next Steps

1. **Test the CLI:** Try generating names for different products
2. **Review outputs:** Check the generated names, SEO data, and stories
3. **Run tests:** Ensure all unit tests pass
4. **Check documentation:** Review README.md, TESTING.md, and CLAUDE.md
5. **Try ADK Web UI** (when needed): `adk web brand_studio_agent`

## 📚 Documentation

- **README.md** - Full project documentation
- **TESTING.md** - Testing strategies and evaluation framework
- **CLAUDE.md** - Agent architecture and development guide
- **docs/MIGRATION_COMPLETION_CHECKLIST.md** - Verification checklist

## 🎉 Success Indicators

You'll know it's working when you see:
- ✓ All agents initialize without errors
- ✓ API calls complete successfully
- ✓ Brand names generated
- ✓ Validation results returned
- ✓ SEO metadata created
- ✓ Brand story generated

## 💬 Getting Help

If you encounter issues:

1. Check the error message carefully
2. Review the troubleshooting section above
3. Check your .env configuration
4. Verify API quotas in GCP console
5. Review the full documentation in README.md

---

**Status:** ✅ Migration Complete - System Ready for Testing!
