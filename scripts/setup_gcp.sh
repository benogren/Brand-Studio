#!/bin/bash
set -e

echo "=========================================="
echo "AI Brand Studio - GCP Setup"
echo "=========================================="
echo ""

# Check if GOOGLE_CLOUD_PROJECT is set
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "❌ Error: GOOGLE_CLOUD_PROJECT environment variable is not set"
    echo "Please set it with: export GOOGLE_CLOUD_PROJECT=your-project-id"
    exit 1
fi

echo "Setting up GCP project: $GOOGLE_CLOUD_PROJECT"
echo ""

# Required APIs for Agent Engine deployment
REQUIRED_APIS=(
    "aiplatform.googleapis.com"          # Vertex AI Platform
    "storage-api.googleapis.com"         # Cloud Storage
    "logging.googleapis.com"             # Cloud Logging
    "cloudtrace.googleapis.com"          # Cloud Trace
    "monitoring.googleapis.com"          # Cloud Monitoring
    "cloudresourcemanager.googleapis.com" # Resource Manager
    "serviceusage.googleapis.com"        # Service Usage
    "generativelanguage.googleapis.com"  # Generative Language API
)

echo "Enabling required Google Cloud APIs..."
echo ""

for api in "${REQUIRED_APIS[@]}"; do
    echo "Enabling $api..."
    gcloud services enable "$api" --project="$GOOGLE_CLOUD_PROJECT" || {
        echo "⚠️  Warning: Failed to enable $api (may already be enabled or require permissions)"
    }
done

echo ""
echo "=========================================="
echo "✓ GCP Setup Complete!"
echo "=========================================="
echo ""
echo "All required APIs have been enabled."
echo ""
echo "Next steps:"
echo "1. Ensure your .env file has the correct GOOGLE_CLOUD_PROJECT value"
echo "2. Run 'source .env' to load environment variables"
echo "3. Create the deployment structure: see Task 13.0"
echo "4. Deploy using: ./scripts/deploy.sh"
echo ""
