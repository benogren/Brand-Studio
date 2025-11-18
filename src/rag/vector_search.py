"""
Vertex AI Vector Search integration for brand name RAG.

This module provides querying capabilities for the deployed Vector Search index,
including:
- K-NN (K-Nearest Neighbors) search
- Industry and category filtering
- Batch queries
"""

import logging
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger('brand_studio.vector_search')


@dataclass
class SearchResult:
    """Result from vector search query."""
    brand_id: str
    brand_name: str
    distance: float
    metadata: Dict[str, Any]


class VectorSearchClient:
    """
    Client for querying Vertex AI Vector Search index.

    Provides semantic search for brand names with metadata filtering.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        index_endpoint: Optional[str] = None,
        deployed_index_id: Optional[str] = None
    ):
        """
        Initialize Vector Search client.

        Args:
            project_id: GCP project ID (defaults to GOOGLE_CLOUD_PROJECT)
            location: GCP location (defaults to GOOGLE_CLOUD_LOCATION)
            index_endpoint: Full index endpoint resource name
            deployed_index_id: Deployed index ID
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = location or os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        self.index_endpoint_name = index_endpoint or os.getenv('VECTOR_SEARCH_INDEX_ENDPOINT')
        self.deployed_index_id = deployed_index_id or os.getenv(
            'VECTOR_SEARCH_DEPLOYED_INDEX_ID',
            'brand_names_deployed'
        )

        if not self.project_id:
            raise ValueError("project_id must be provided or GOOGLE_CLOUD_PROJECT must be set")

        if not self.index_endpoint_name:
            raise ValueError(
                "index_endpoint must be provided or VECTOR_SEARCH_INDEX_ENDPOINT must be set"
            )

        logger.info(
            f"Initialized VectorSearchClient for project={self.project_id}, "
            f"endpoint={self.index_endpoint_name}, "
            f"deployed_index={self.deployed_index_id}"
        )

        self._initialize_client()
        self._load_metadata()

    def _initialize_client(self) -> None:
        """Initialize Vertex AI and get endpoint."""
        try:
            from google.cloud import aiplatform

            aiplatform.init(project=self.project_id, location=self.location)

            # Get endpoint
            self.endpoint = aiplatform.MatchingEngineIndexEndpoint(
                index_endpoint_name=self.index_endpoint_name
            )

            logger.info("Vector Search client initialized successfully")

        except ImportError:
            logger.error(
                "google-cloud-aiplatform not installed. "
                "Install with: pip install google-cloud-aiplatform"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Vector Search client: {e}")
            raise

    def _load_metadata(self) -> None:
        """Load brand metadata from JSON file."""
        import json

        metadata_path = "data/brand_metadata.json"

        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            logger.info(f"Loaded metadata for {len(self.metadata)} brands")
        except FileNotFoundError:
            logger.warning(f"Metadata file not found: {metadata_path}")
            self.metadata = {}
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            self.metadata = {}

    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for query text.

        Args:
            query: Query text

        Returns:
            768-dimensional embedding vector
        """
        try:
            from vertexai.language_models import TextEmbeddingModel

            model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            embeddings = model.get_embeddings([query])

            if not embeddings:
                raise ValueError("No embedding returned from API")

            return embeddings[0].values

        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            raise

    def search(
        self,
        query: str,
        num_neighbors: int = 50,
        industry_filter: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search for similar brands using semantic search.

        Args:
            query: Search query (e.g., "productivity tools", "fintech startups")
            num_neighbors: Number of results to return (default: 50, max: 1000)
            industry_filter: Optional industry filter
            category_filter: Optional category filter

        Returns:
            List of SearchResult objects ordered by relevance

        Example:
            >>> client = VectorSearchClient()
            >>> results = client.search(
            ...     "productivity workspace tools",
            ...     num_neighbors=10,
            ...     industry_filter="productivity"
            ... )
            >>> for result in results:
            ...     print(f"{result.brand_name}: {result.distance:.3f}")
        """
        logger.info(
            f"Searching for query='{query}' with num_neighbors={num_neighbors}, "
            f"industry_filter={industry_filter}, category_filter={category_filter}"
        )

        try:
            # Generate query embedding
            query_embedding = self.generate_query_embedding(query)

            # Build filter constraints
            restricts = []
            if industry_filter:
                restricts.append({
                    "namespace": "industry",
                    "allow_list": [industry_filter]
                })
            if category_filter:
                restricts.append({
                    "namespace": "category",
                    "allow_list": [category_filter]
                })

            # Query Vector Search
            response = self.endpoint.find_neighbors(
                deployed_index_id=self.deployed_index_id,
                queries=[query_embedding],
                num_neighbors=num_neighbors,
                filter=restricts if restricts else None
            )

            # Parse results
            results = []
            if response and len(response) > 0:
                for neighbor in response[0]:
                    brand_id = neighbor.id
                    metadata = self.metadata.get(brand_id, {})

                    results.append(
                        SearchResult(
                            brand_id=brand_id,
                            brand_name=metadata.get('brand_name', brand_id),
                            distance=neighbor.distance,
                            metadata=metadata
                        )
                    )

            logger.info(f"Found {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def batch_search(
        self,
        queries: List[str],
        num_neighbors: int = 50,
        industry_filter: Optional[str] = None
    ) -> List[List[SearchResult]]:
        """
        Perform batch search for multiple queries.

        Args:
            queries: List of query strings
            num_neighbors: Number of results per query
            industry_filter: Optional industry filter

        Returns:
            List of result lists, one per query
        """
        logger.info(f"Performing batch search for {len(queries)} queries")

        try:
            # Generate embeddings for all queries
            from vertexai.language_models import TextEmbeddingModel

            model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            embeddings_response = model.get_embeddings(queries)
            query_embeddings = [emb.values for emb in embeddings_response]

            # Build filter
            restricts = []
            if industry_filter:
                restricts.append({
                    "namespace": "industry",
                    "allow_list": [industry_filter]
                })

            # Batch query
            response = self.endpoint.find_neighbors(
                deployed_index_id=self.deployed_index_id,
                queries=query_embeddings,
                num_neighbors=num_neighbors,
                filter=restricts if restricts else None
            )

            # Parse results for each query
            all_results = []
            for query_response in response:
                query_results = []
                for neighbor in query_response:
                    brand_id = neighbor.id
                    metadata = self.metadata.get(brand_id, {})

                    query_results.append(
                        SearchResult(
                            brand_id=brand_id,
                            brand_name=metadata.get('brand_name', brand_id),
                            distance=neighbor.distance,
                            metadata=metadata
                        )
                    )
                all_results.append(query_results)

            logger.info(f"Batch search complete: {len(all_results)} result sets")
            return all_results

        except Exception as e:
            logger.error(f"Batch search failed: {e}")
            raise

    def get_similar_brands(
        self,
        brand_name: str,
        num_neighbors: int = 10,
        same_industry: bool = True
    ) -> List[SearchResult]:
        """
        Find brands similar to a given brand name.

        Args:
            brand_name: Brand name to find similar brands for
            num_neighbors: Number of similar brands to return
            same_industry: If True, filter to same industry

        Returns:
            List of similar brands
        """
        logger.info(f"Finding brands similar to '{brand_name}'")

        # Find the brand in metadata
        brand_metadata = None
        for metadata in self.metadata.values():
            if metadata.get('brand_name', '').lower() == brand_name.lower():
                brand_metadata = metadata
                break

        if not brand_metadata:
            logger.warning(f"Brand '{brand_name}' not found in dataset")
            return []

        # Search with brand name and metadata as query
        industry = brand_metadata.get('industry') if same_industry else None

        query = f"{brand_name} {brand_metadata.get('category', '')}"

        return self.search(
            query=query,
            num_neighbors=num_neighbors + 1,  # +1 to exclude self
            industry_filter=industry
        )[1:]  # Skip first result (the brand itself)


# Singleton instance
_vector_search_instance: Optional[VectorSearchClient] = None


def get_vector_search() -> VectorSearchClient:
    """
    Get or create the global VectorSearchClient instance.

    Returns:
        VectorSearchClient singleton instance
    """
    global _vector_search_instance

    if _vector_search_instance is None:
        _vector_search_instance = VectorSearchClient()

    return _vector_search_instance


def search_brands(
    query: str,
    num_results: int = 50,
    industry: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for brands (convenience function for tool use).

    Args:
        query: Search query
        num_results: Number of results to return
        industry: Optional industry filter

    Returns:
        List of brand dictionaries
    """
    client = get_vector_search()
    results = client.search(
        query=query,
        num_neighbors=num_results,
        industry_filter=industry
    )

    return [
        {
            "brand_name": r.brand_name,
            "distance": r.distance,
            **r.metadata
        }
        for r in results
    ]


if __name__ == "__main__":
    # Test queries
    import sys
    from dotenv import load_dotenv

    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    if len(sys.argv) < 2:
        print("Usage: python3 src/rag/vector_search.py <query>")
        print("Example: python3 src/rag/vector_search.py 'productivity tools'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    logger.info("Testing Vector Search...")
    logger.info(f"Query: '{query}'")

    try:
        client = VectorSearchClient()
        results = client.search(query, num_neighbors=5)

        print("\n" + "=" * 70)
        print(f"Top 5 Results for: '{query}'")
        print("=" * 70)

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.brand_name}")
            print(f"   Distance: {result.distance:.4f}")
            print(f"   Industry: {result.metadata.get('industry', 'N/A')}")
            print(f"   Category: {result.metadata.get('category', 'N/A')}")
            print(f"   Strategy: {result.metadata.get('naming_strategy', 'N/A')}")

        print("\n" + "=" * 70)
        print("✅ Vector Search test complete!")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
