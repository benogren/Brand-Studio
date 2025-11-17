# 🚀 Run AI Brand Studio Locally - Quick Guide

## You're All Set! ✅

Your environment is ready:
- ✅ Python 3.14.0 with virtual environment
- ✅ All dependencies installed
- ✅ Google AI API configured
- ✅ All Phase 2 features working

## 3 Ways to Run

### Option 1: Interactive Mode (Best for First Time)

```bash
# Activate environment
source venv/bin/activate

# Start interactive mode
python -m src.cli
```

You'll be prompted for:
1. Product description
2. Target audience (optional)
3. Brand personality (playful/professional/innovative/luxury)
4. Industry category
5. Number of names (20-50)

**Example session:**
```
Product description: AI-powered fitness tracking app
Target audience: Gym enthusiasts aged 25-40
Brand personality: 3 (innovative)
Industry: health-tech
Number of names: 20
```

### Option 2: Command Line Mode (Fast)

```bash
source venv/bin/activate

python -m src.cli \
  --product "AI meal planning app for busy parents" \
  --audience "Parents aged 28-40" \
  --personality innovative \
  --industry food-tech \
  --count 15
```

**Quick examples:**

```bash
# Healthcare app
python -m src.cli \
  --product "Mental wellness app with AI coaching" \
  --personality playful \
  --count 10

# Fintech startup
python -m src.cli \
  --product "Cryptocurrency portfolio tracker" \
  --audience "Crypto investors" \
  --personality innovative \
  --industry fintech \
  --count 20

# E-commerce
python -m src.cli \
  --product "Sustainable fashion marketplace" \
  --personality professional \
  --industry retail \
  --json my-brands.json
```

### Option 3: Test All Features (Demo)

```bash
source venv/bin/activate

# Run comprehensive Phase 2 tests
python test_phase2.py
```

This will test:
1. ✅ Research Agent - Industry insights
2. ✅ RAG System - Brand retrieval (31 brands)
3. ✅ Validation Agent - Domain + trademark checking
4. ✅ SEO Optimizer - Keywords and meta tags
5. ✅ Story Generator - Real LLM-powered narratives
6. ✅ Session Management - History tracking
7. ✅ Name Generation - Complete workflow

**Expected output:** All tests pass in ~30-40 seconds

## What You Get

Each generated brand includes:

```
Brand Name: FitFlow
├── Naming Strategy: portmanteau
├── Tagline: "Where fitness meets innovation"
├── Rationale: Combines 'fitness' and 'flow' to convey...
├── Syllables: 2
├── Memorable Score: 8/10
└── SEO Optimization: 85/100
```

## CLI Options Reference

| Flag | Description | Example |
|------|-------------|---------|
| `--product, -p` | Product description (required in direct mode) | `--product "AI app"` |
| `--audience, -a` | Target audience | `--audience "Millennials"` |
| `--personality, -P` | Brand tone | `--personality innovative` |
| `--industry, -i` | Industry category | `--industry tech` |
| `--count, -c` | Number of names (20-50) | `--count 25` |
| `--verbose, -v` | Detailed output | `--verbose` |
| `--quiet, -q` | Minimal output (names only) | `--quiet` |
| `--json, -j` | Save to JSON file | `--json results.json` |

## Brand Personalities

Choose from:
- **playful**: Fun, whimsical, lighthearted
- **professional**: Authoritative, trustworthy
- **innovative**: Forward-thinking, tech-savvy
- **luxury**: Elegant, sophisticated, premium

## Supported Industries

Optimized for:
- `tech` / `technology`
- `health` / `health-tech`
- `food` / `food-tech`
- `fintech` / `finance`
- `retail` / `ecommerce`
- `general` (default)

## Common Usage Patterns

### 1. Quick Test (Minimal Output)

```bash
python -m src.cli \
  --product "Your product idea" \
  --quiet
```

### 2. Full Analysis (With JSON Export)

```bash
python -m src.cli \
  --product "Healthcare telemedicine platform" \
  --audience "Patients 40-65" \
  --personality professional \
  --count 30 \
  --json healthcare-brands.json \
  --verbose
```

### 3. Multiple Industries

```bash
# Tech startup
python -m src.cli --product "Developer tools SaaS" --industry tech --count 15

# Food delivery
python -m src.cli --product "Farm-to-table meal kits" --industry food-tech --count 20

# Fintech
python -m src.cli --product "SMB lending platform" --industry fintech --count 25
```

## View Generated Brands

Results are saved to:
- **Console**: Displayed immediately
- **JSON file**: If `--json` flag used
- **Session history**: `.sessions/` directory

```bash
# View recent sessions
ls -lt .sessions/ | head -5

# Read a session
cat .sessions/YOUR_SESSION_ID.json | python -m json.tool
```

## Performance

- **Name generation**: ~10-15 seconds for 20 names
- **Uses**: Google AI API (Gemini 2.5 Flash)
- **Features active**:
  - ✅ Real LLM generation
  - ✅ Domain availability checking
  - ✅ Trademark risk assessment
  - ✅ SEO optimization
  - ✅ Brand story generation
  - ✅ Session tracking

## Troubleshooting

### "Vertex AI 404 NOT_FOUND" warning
**This is normal!** The app automatically falls back to Google AI API. You can safely ignore this.

### No names generated
Check that `.env` file has:
```bash
GOOGLE_CLOUD_PROJECT=brand-agent-478519
GOOGLE_API_KEY=your-api-key
```

### Module not found
Make sure you're in the project directory and virtual environment is activated:
```bash
pwd  # Should show: /Users/benogren/Desktop/projects/Brand-Agent
source venv/bin/activate  # Should see (venv) in prompt
```

## Example Output

```
GENERATED BRAND NAMES (20 total)
======================================================================

1. FitGenius
   Rationale: Combines 'fitness' with 'genius' to convey intelligent,
              personalized workout planning powered by AI.
   Tagline: "Your AI-powered path to peak performance"

2. WorkoutIQ
   Rationale: 'IQ' suggests intelligence and data-driven insights for
              optimal fitness results.
   Tagline: "Smart training, real results"

3. PulsAI
   Rationale: Merges 'pulse' (heartbeat, vitality) with 'AI' for a
              modern, tech-forward fitness brand.
   Tagline: "Feel the rhythm of smarter fitness"

... and 17 more names

======================================================================
✓ Successfully generated 20 brand names
======================================================================
```

## Next Steps

1. **Generate your first brands**: Try interactive mode
2. **Experiment**: Test different personalities and industries
3. **Save favorites**: Use `--json` to export results
4. **Check validation**: Review domain/trademark status
5. **Get marketing copy**: Brand stories included automatically

## Getting Help

```bash
# Show all options
python -m src.cli --help

# Run feature tests
python test_phase2.py

# Check environment
source venv/bin/activate && python --version
```

---

## Ready to Start?

**Simplest way:**
```bash
source venv/bin/activate
python -m src.cli
```

**Quick example:**
```bash
source venv/bin/activate
python -m src.cli --product "Your awesome product idea" --count 10
```

Enjoy creating amazing brands! 🎨
