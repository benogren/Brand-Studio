# AI Brand Studio - Quick Start Guide

Get the project running locally in under 5 minutes!

## Prerequisites

- Python 3.9+ (you have Python 3.14.0 ✓)
- Google Cloud account (for full functionality)

## Quick Local Setup (No GCP Required for Testing)

### 1. Create Virtual Environment

```bash
cd /Users/benogren/Desktop/projects/Brand-Agent

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment (Minimal)

```bash
# Copy example env file
cp .env.example .env

# Edit .env - add your Google Cloud project ID
# For now, you can use a dummy value for testing
echo "GOOGLE_CLOUD_PROJECT=test-project" >> .env
echo "GOOGLE_CLOUD_LOCATION=us-central1" >> .env
```

### 4. Run the CLI!

#### Option A: Interactive Mode (Easiest)

```bash
python -m src.cli
```

This will prompt you step-by-step for:
- Product description
- Target audience
- Brand personality (playful/professional/innovative/luxury)
- Industry
- Number of names to generate

#### Option B: Direct Command-Line

```bash
# Generate 30 brand names for an AI meal planning app
python -m src.cli \
  --product "AI-powered meal planning app for busy parents" \
  --audience "Parents aged 28-40" \
  --personality warm \
  --industry food_tech \
  --count 30
```

#### Option C: Quiet Mode (Names Only)

```bash
python -m src.cli \
  --product "Healthcare telemedicine app" \
  --personality professional \
  --quiet
```

#### Option D: Verbose Mode (Debugging)

```bash
python -m src.cli \
  --product "Fintech lending platform" \
  --personality innovative \
  --verbose
```

#### Option E: Save to JSON File

```bash
python -m src.cli \
  --product "E-commerce sustainable fashion marketplace" \
  --personality playful \
  --json output.json
```

## CLI Options

```
--product, -p          Product description (required in direct mode)
--audience, -a         Target audience (optional)
--personality, -P      Brand personality (playful/professional/innovative/luxury)
--industry, -i         Industry category (e.g., healthcare, fintech)
--count, -c            Number of names (20-50, default: 30)

--verbose, -v          Show detailed output
--quiet, -q            Minimal output (names only)
--json FILE            Save results to JSON file

--project-id           Google Cloud project ID (overrides .env)
--location             GCP region (default: us-central1)
```

## Phase 1 Limitations

Since this is **Phase 1 MVP**, the following features use **placeholder implementations**:

✅ **Working:**
- CLI interface (interactive + command-line)
- Name generator with 4 strategies (portmanteau, descriptive, invented, acronym)
- Brand personality customization
- Output formatting (normal, quiet, verbose, JSON)

⚠️ **Placeholder (returns sample data):**
- Orchestrator workflow coordination
- Domain availability checking (needs python-whois)
- Actual LLM generation (currently returns 30 placeholder names)

These will be fully functional in Phase 2 when:
- Google Cloud authentication is set up
- Vertex AI APIs are enabled
- Real LLM calls are activated

## Testing the Code

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_cli.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Example Workflows

### Example 1: Generate Names for Healthcare App

```bash
python -m src.cli \
  --product "AI-powered telemedicine app for remote consultations with specialists" \
  --audience "Patients aged 40-65 with chronic conditions" \
  --personality professional \
  --industry healthcare \
  --count 40
```

### Example 2: Fintech Startup (Verbose)

```bash
python -m src.cli \
  --product "Peer-to-peer lending platform for small business owners" \
  --audience "Small business owners seeking working capital" \
  --personality innovative \
  --industry fintech \
  --verbose
```

### Example 3: E-commerce (Save Results)

```bash
python -m src.cli \
  --product "Sustainable fashion marketplace connecting eco-conscious shoppers with ethical brands" \
  --audience "Women aged 25-40 who value sustainability" \
  --personality playful \
  --industry e_commerce \
  --json fashion_brands.json \
  --count 50
```

## Next Steps: Full GCP Setup

For **full functionality** (actual LLM generation, domain checking, etc.), follow the complete setup:

1. **Set up Google Cloud:**
   ```bash
   ./scripts/setup_gcp.sh
   ```

2. **Configure authentication:**
   ```bash
   gcloud auth application-default login
   ```

3. **Update .env with real project ID:**
   ```bash
   # Edit .env and set your actual GCP project ID
   GOOGLE_CLOUD_PROJECT=your-actual-project-id
   ```

4. **Enable Vertex AI API:**
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

5. **Run with real LLM generation:**
   The CLI will automatically use Gemini 2.5 Pro once authentication is configured!

## Troubleshooting

### "ModuleNotFoundError: No module named 'src'"

Make sure you're running from the project root:
```bash
cd /Users/benogren/Desktop/projects/Brand-Agent
python -m src.cli
```

### "GOOGLE_CLOUD_PROJECT environment variable is required"

Set it in `.env`:
```bash
echo "GOOGLE_CLOUD_PROJECT=test-project" >> .env
```

### Virtual environment not activated

```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

## Help

Get CLI help:
```bash
python -m src.cli --help
```

View detailed setup guide:
```bash
cat docs/setup.md
```

---

**Ready to generate some brand names?** Start with interactive mode:

```bash
python -m src.cli
```
