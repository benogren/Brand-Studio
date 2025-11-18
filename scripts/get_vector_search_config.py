#!/usr/bin/env python3
"""
Get Vector Search configuration for .env file.

Retrieves the index endpoint and deployed index ID from your GCP project.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.cloud import aiplatform

# Load environment
load_dotenv()

def main():
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

    if not project_id:
        print("ERROR: GOOGLE_CLOUD_PROJECT environment variable not set")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("Vector Search Configuration")
    print("=" * 70)
    print(f"Project: {project_id}")
    print(f"Location: {location}")
    print("=" * 70 + "\n")

    # Initialize Vertex AI
    aiplatform.init(project=project_id, location=location)

    # Find index
    print("Looking for Vector Search index...")
    indexes = aiplatform.MatchingEngineIndex.list(
        filter='display_name="brand-names-index"'
    )

    if not indexes:
        print("❌ No index found with name 'brand-names-index'")
        print("   Run scripts/deploy_vector_search.py to create the index")
        sys.exit(1)

    index = indexes[0]
    print(f"✅ Found index: {index.display_name}")
    print(f"   Resource: {index.resource_name}")

    # Find endpoint
    print("\nLooking for Vector Search endpoint...")
    endpoints = aiplatform.MatchingEngineIndexEndpoint.list(
        filter='display_name="brand-names-endpoint"'
    )

    if not endpoints:
        print("❌ No endpoint found with name 'brand-names-endpoint'")
        print("   Run scripts/deploy_vector_search.py to create the endpoint")
        sys.exit(1)

    endpoint = endpoints[0]
    print(f"✅ Found endpoint: {endpoint.display_name}")
    print(f"   Resource: {endpoint.resource_name}")

    # Check deployed indexes
    print("\nChecking deployed indexes...")
    deployed_indexes = endpoint.deployed_indexes

    if not deployed_indexes:
        print("⚠️  No indexes deployed to this endpoint yet")
        print("   The deployment may still be in progress (takes 10-15 minutes)")
        print("   Run this script again after deployment completes")
    else:
        print(f"✅ Found {len(deployed_indexes)} deployed index(es):")
        for di in deployed_indexes:
            print(f"   - ID: {di.id}")
            print(f"     Display name: {di.display_name}")

    # Print .env configuration
    print("\n" + "=" * 70)
    print("Add these lines to your .env file:")
    print("=" * 70)
    print(f"VECTOR_SEARCH_INDEX_ENDPOINT={endpoint.resource_name}")

    if deployed_indexes:
        deployed_index_id = deployed_indexes[0].id
        print(f"VECTOR_SEARCH_DEPLOYED_INDEX_ID={deployed_index_id}")
    else:
        print("VECTOR_SEARCH_DEPLOYED_INDEX_ID=brand_names_deployed  # After deployment completes")

    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
