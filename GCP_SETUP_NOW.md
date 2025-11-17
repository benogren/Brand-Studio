# Google Cloud Setup - Get Real LLM Brand Names Now!

Follow these steps to enable real Gemini LLM generation (takes ~5 minutes).

## Step 1: Authenticate with Google Cloud

```bash
gcloud auth login
```

This will:
- Open your browser
- Ask you to sign in with your Google account
- Grant permissions to gcloud CLI

**After you see "You are now logged in", come back to the terminal.**

---

## Step 2: List Your Existing Projects (or Create New One)

### Option A: Use Existing Project

```bash
# List your projects
gcloud projects list

# Pick one and copy the PROJECT_ID (not the name!)
# Set it as default:
gcloud config set project YOUR_PROJECT_ID
```

### Option B: Create New Project

```bash
# Create a new project for Brand Studio
gcloud projects create ai-brand-studio-$(date +%s) --name="AI Brand Studio"

# The command will output your new PROJECT_ID
# Set it as default:
gcloud config set project ai-brand-studio-XXXXXXXXX
```

**Note:** Replace `ai-brand-studio-XXXXXXXXX` with the actual PROJECT_ID from the output.

---

## Step 3: Enable Billing (Required for Vertex AI)

You need to link a billing account to use Vertex AI:

1. **Check if billing is enabled:**
   ```bash
   gcloud beta billing projects describe $(gcloud config get-value project)
   ```

2. **If not enabled, do this:**

   Go to: https://console.cloud.google.com/billing

   - Click "Link a billing account"
   - Select your project
   - Choose your billing account (or create one)

   **Don't worry about costs:**
   - Gemini 2.5 Flash Lite: ~$0.075 per 1M characters
   - Gemini 2.5 Pro: ~$3.50 per 1M characters
   - Generating 30 brand names ≈ $0.01-0.05
   - You get $300 free credits if you're new to GCP!

---

## Step 4: Enable Required APIs

```bash
# Enable Vertex AI API (for Gemini LLMs)
gcloud services enable aiplatform.googleapis.com

# Enable Cloud Logging (optional but helpful)
gcloud services enable logging.googleapis.com

# This takes 1-2 minutes...
```

---

## Step 5: Set Up Application Default Credentials

```bash
gcloud auth application-default login
```

This will:
- Open your browser again
- Grant credentials for your local applications
- Save credentials to your machine

**Wait for: "Credentials saved to file"**

---

## Step 6: Update Your .env File

```bash
# Get your project ID
gcloud config get-value project

# Copy the output and update .env:
# Replace: GOOGLE_CLOUD_PROJECT=test-project-local
# With: GOOGLE_CLOUD_PROJECT=your-actual-project-id
```

**Or edit .env directly:**

```bash
# Open .env in your editor
code .env
# or
nano .env

# Find the line:
GOOGLE_CLOUD_PROJECT=test-project-local

# Replace with your actual project ID:
GOOGLE_CLOUD_PROJECT=ai-brand-studio-1234567890
```

---

## Step 7: Test Real LLM Generation! 🎉

```bash
# Activate your virtual environment
source venv/bin/activate

# Generate real brand names!
python -m src.cli \
  --product "AI-powered meal planning app for busy millennial parents" \
  --personality playful \
  --count 30
```

**This will now use real Gemini 2.5 Pro to generate creative brand names!**

---

## Verification Checklist

Before running the CLI, verify:

```bash
# 1. Check you're authenticated
gcloud auth list
# Should show your email with an asterisk (*)

# 2. Check project is set
gcloud config get-value project
# Should show your project ID

# 3. Check Vertex AI is enabled
gcloud services list --enabled | grep aiplatform
# Should show: aiplatform.googleapis.com

# 4. Check .env has your project
grep GOOGLE_CLOUD_PROJECT .env
# Should show: GOOGLE_CLOUD_PROJECT=your-actual-project-id
```

---

## Quick Setup Script (All-in-One)

If you want to automate steps 2-4, run:

```bash
# Make the script executable
chmod +x scripts/setup_gcp.sh

# Run it
./scripts/setup_gcp.sh
```

**But first, make sure you've done Step 1 (gcloud auth login)!**

---

## Troubleshooting

### "billing has not been enabled"

**Fix:** Go to https://console.cloud.google.com/billing and link a billing account.

### "API not enabled"

**Fix:**
```bash
gcloud services enable aiplatform.googleapis.com
```

### "Could not automatically determine credentials"

**Fix:**
```bash
gcloud auth application-default login
```

### Still getting mock data?

**Check:**
1. Is your project ID correct in `.env`?
   ```bash
   cat .env | grep GOOGLE_CLOUD_PROJECT
   ```

2. Are credentials set up?
   ```bash
   ls -la ~/.config/gcloud/application_default_credentials.json
   ```

3. Is Vertex AI enabled?
   ```bash
   gcloud services list --enabled | grep aiplatform
   ```

---

## Estimated Costs

**For Phase 1 testing (generating 30 names):**
- Cost per request: $0.01 - $0.05
- 10 test runs: ~$0.50
- Monthly (100 generations): ~$5

**Free tier:**
- New GCP users get $300 free credits
- No charge for API calls within free tier limits

**Set up billing alerts:**
```bash
# Go to: https://console.cloud.google.com/billing/budgets
# Create alert at $10, $25, $50
```

---

## What Happens After Setup?

Once configured, the CLI will:
- ✅ Use real Gemini 2.5 Pro for name generation
- ✅ Generate creative, diverse brand names
- ✅ Use 4 naming strategies (portmanteau, descriptive, invented, acronym)
- ✅ Customize by brand personality
- ✅ Include rationales and taglines for each name

**No code changes needed** - the same CLI commands just work with real LLMs!

---

## Ready to Start?

**Start with Step 1:**

```bash
gcloud auth login
```

Let me know when you complete each step, and I can help you verify and troubleshoot! 🚀
