#!/usr/bin/env python3
"""
Deploy Vertex AI Vector Search for existing embeddings.

This script assumes embeddings have already been generated.
It will:
1. Create/verify Cloud Storage bucket exists
2. Upload embeddings JSONL to GCS
3. Create Vector Search index
4. Create index endpoint
5. Deploy index to endpoint

Usage:
    python3 scripts/deploy_vector_search.py [--embeddings-file data/brand_embeddings.jsonl]
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.cloud import aiplatform
from google.cloud import storage
from google.api_core import exceptions as gcp_exceptions

# Load environment
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_bucket_if_not_exists(project_id: str, bucket_name: str, location: str) -> None:
    """Create GCS bucket if it doesn't exist."""
    storage_client = storage.Client(project=project_id)

    try:
        bucket = storage_client.get_bucket(bucket_name)
        logger.info(f"✅ Bucket '{bucket_name}' already exists")
    except gcp_exceptions.NotFound:
        logger.info(f"Creating bucket '{bucket_name}'...")
        bucket = storage_client.create_bucket(bucket_name, location=location)
        logger.info(f"✅ Bucket '{bucket_name}' created")


def upload_to_gcs(project_id: str, local_file: str, bucket_name: str, blob_name: str) -> str:
    """Upload file to GCS."""
    logger.info(f"Uploading {local_file} to gs://{bucket_name}/{blob_name}...")

    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.upload_from_filename(local_file)

    gcs_uri = f"gs://{bucket_name}/{blob_name}"
    logger.info(f"✅ Uploaded to {gcs_uri}")
    return gcs_uri


def create_index(project_id: str, location: str, gcs_uri: str, display_name: str):
    """Create Vector Search index."""
    logger.info(f"Creating Vector Search index '{display_name}'...")

    aiplatform.init(project=project_id, location=location)

    # Check if index already exists
    existing_indexes = aiplatform.MatchingEngineIndex.list(
        filter=f'display_name="{display_name}"'
    )

    if existing_indexes:
        logger.info(f"✅ Index '{display_name}' already exists")
        logger.info(f"   Resource name: {existing_indexes[0].resource_name}")
        return existing_indexes[0]

    # Create index with TREE_AH algorithm
    # - 768 dimensions (text-embedding-004)
    # - DOT_PRODUCT_DISTANCE
    # - TREE_AH for approximate nearest neighbor search
    logger.info("Creating new index (this will take 20-30 minutes)...")

    index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
        display_name=display_name,
        contents_delta_uri=gcs_uri,
        dimensions=768,
        approximate_neighbors_count=50,
        distance_measure_type="DOT_PRODUCT_DISTANCE",
        leaf_node_embedding_count=500,
        leaf_nodes_to_search_percent=7,
        description="Brand name vector search index with industry/category filtering",
        labels={"app": "brand-studio", "model": "text-embedding-004"}
    )

    logger.info(f"✅ Index created: {index.resource_name}")
    return index


def create_endpoint(project_id: str, location: str, display_name: str):
    """Create Vector Search endpoint."""
    logger.info(f"Creating index endpoint '{display_name}'...")

    aiplatform.init(project=project_id, location=location)

    # Check if endpoint already exists
    existing_endpoints = aiplatform.MatchingEngineIndexEndpoint.list(
        filter=f'display_name="{display_name}"'
    )

    if existing_endpoints:
        logger.info(f"✅ Endpoint '{display_name}' already exists")
        logger.info(f"   Resource name: {existing_endpoints[0].resource_name}")
        return existing_endpoints[0]

    # Create public endpoint
    logger.info("Creating new endpoint...")

    endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
        display_name=display_name,
        description="Public endpoint for brand name vector search",
        public_endpoint_enabled=True,
        labels={"app": "brand-studio"}
    )

    logger.info(f"✅ Endpoint created: {endpoint.resource_name}")
    return endpoint


def deploy_index_to_endpoint(
    index: aiplatform.MatchingEngineIndex,
    endpoint: aiplatform.MatchingEngineIndexEndpoint,
    deployed_index_id: str
):
    """Deploy index to endpoint."""
    logger.info(f"Deploying index to endpoint...")

    # Check if already deployed
    for di in endpoint.deployed_indexes:
        if di.id == deployed_index_id:
            logger.info(f"✅ Index already deployed with ID '{deployed_index_id}'")
            return

    logger.info("Deploying index (this will take 10-15 minutes)...")

    endpoint.deploy_index(
        index=index,
        deployed_index_id=deployed_index_id,
        display_name=deployed_index_id,
        machine_type="e2-standard-16",  # Required for SHARD_SIZE_MEDIUM
        min_replica_count=1,
        max_replica_count=2
    )

    logger.info(f"✅ Index deployed with ID '{deployed_index_id}'")


def main():
    parser = argparse.ArgumentParser(description="Deploy Vector Search for brand embeddings")
    parser.add_argument(
        "--embeddings-file",
        default="data/brand_embeddings.jsonl",
        help="Path to embeddings JSONL file"
    )
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Skip upload step (assumes already uploaded)"
    )

    args = parser.parse_args()

    # Get config from environment
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    if not project_id:
        logger.error("GOOGLE_CLOUD_PROJECT environment variable not set")
        sys.exit(1)

    # Configuration
    bucket_name = f"{project_id}-brand-embeddings"
    gcs_blob_name = "embeddings/brand_embeddings.jsonl"
    index_display_name = "brand-names-index"
    endpoint_display_name = "brand-names-endpoint"
    deployed_index_id = "brand_names_deployed"

    print("\n" + "=" * 70)
    print("Vertex AI Vector Search Deployment")
    print("=" * 70)
    print(f"Project: {project_id}")
    print(f"Location: {location}")
    print(f"Embeddings file: {args.embeddings_file}")
    print(f"Bucket: {bucket_name}")
    print("=" * 70 + "\n")

    # Verify embeddings file exists
    if not Path(args.embeddings_file).exists():
        logger.error(f"Embeddings file not found: {args.embeddings_file}")
        logger.error("Run 'python3 src/rag/embeddings.py' to generate embeddings first")
        sys.exit(1)

    try:
        # Step 1: Create bucket
        logger.info("\n📦 Step 1: Create/verify Cloud Storage bucket")
        create_bucket_if_not_exists(project_id, bucket_name, location)

        # Step 2: Upload embeddings
        if not args.skip_upload:
            logger.info("\n📤 Step 2: Upload embeddings to Cloud Storage")
            gcs_uri = upload_to_gcs(project_id, args.embeddings_file, bucket_name, gcs_blob_name)
        else:
            gcs_uri = f"gs://{bucket_name}/{gcs_blob_name}"
            logger.info(f"\n📤 Step 2: Skipped (using existing {gcs_uri})")

        # Step 3: Create index
        logger.info("\n🔍 Step 3: Create Vector Search index")
        index = create_index(project_id, location, gcs_uri, index_display_name)

        # Step 4: Create endpoint
        logger.info("\n🌐 Step 4: Create index endpoint")
        endpoint = create_endpoint(project_id, location, endpoint_display_name)

        # Step 5: Deploy index
        logger.info("\n🚀 Step 5: Deploy index to endpoint")
        deploy_index_to_endpoint(index, endpoint, deployed_index_id)

        # Summary
        print("\n" + "=" * 70)
        print("✅ Vector Search Deployment Complete!")
        print("=" * 70)
        print(f"\nIndex: {index.resource_name}")
        print(f"Endpoint: {endpoint.resource_name}")
        print(f"Deployed Index ID: {deployed_index_id}")
        print(f"\n💡 Add to your .env file:")
        print(f"VECTOR_SEARCH_INDEX_ENDPOINT={endpoint.resource_name}")
        print(f"VECTOR_SEARCH_DEPLOYED_INDEX_ID={deployed_index_id}")
        print("=" * 70 + "\n")

    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
