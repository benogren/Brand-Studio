#!/bin/bash
set -e

echo "=========================================="
echo "AI Brand Studio - Agent Engine Deployment"
echo "=========================================="
echo ""

# Check if GOOGLE_CLOUD_PROJECT is set
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "❌ Error: GOOGLE_CLOUD_PROJECT environment variable is not set"
    echo "Please set it with: export GOOGLE_CLOUD_PROJECT=your-project-id"
    exit 1
fi

# Check if GOOGLE_CLOUD_LOCATION is set
if [ -z "$GOOGLE_CLOUD_LOCATION" ]; then
    echo "⚠️  Warning: GOOGLE_CLOUD_LOCATION not set, using default: us-central1"
    export GOOGLE_CLOUD_LOCATION="us-central1"
fi

echo "Project: $GOOGLE_CLOUD_PROJECT"
echo "Location: $GOOGLE_CLOUD_LOCATION"
echo ""

# Check if brand_studio_agent directory exists
if [ ! -d "brand_studio_agent" ]; then
    echo "❌ Error: brand_studio_agent/ directory not found"
    echo "Please run the restructuring script first to create the deployment structure"
    exit 1
fi

# Navigate to brand_studio_agent directory
cd brand_studio_agent

echo "Deploying to Agent Engine..."
echo ""

# Deploy using adk deploy command
adk deploy agent_engine \
    --project_id="$GOOGLE_CLOUD_PROJECT" \
    --location="$GOOGLE_CLOUD_LOCATION" \
    --deployment_name="brand-studio-agent" \
    --agent_path="." \
    --config_file=".agent_engine_config.json"

echo ""
echo "=========================================="
echo "✓ Deployment Complete!"
echo "=========================================="
echo ""
echo "Your agent is now deployed to Agent Engine."
echo "You can manage it using the Vertex AI console or Python SDK."
echo ""
echo "To test the deployed agent:"
echo "  python -m scripts.test_deployed_agent"
echo ""
echo "To delete the deployment:"
echo "  adk delete agent_engine --deployment_name=brand-studio-agent"
echo ""
