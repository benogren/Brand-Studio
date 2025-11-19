"""
Brand Name RAG (Retrieval Augmented Generation) System.

This module implements semantic search and retrieval of similar brand names
using embeddings and vector similarity. For Phase 2, we use a simplified
in-memory implementation. In production, this would use Vertex AI Vector Search.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger('brand_studio.brand_retrieval')


@dataclass
class BrandEmbedding:
    """Represents a brand name with its embedding vector."""
    brand_name: str
    embedding: np.ndarray
    metadata: Dict[str, Any]


class BrandRetrieval:
    """
    Semantic brand name retrieval system using embeddings.

    For Phase 2, uses simple text-based similarity. In production (Phase 3),
    this would integrate with Vertex AI Vector Search for scalable retrieval.
    """

    def __init__(self):
        """Initialize the brand retrieval system."""
        self.brand_embeddings: List[BrandEmbedding] = []
        logger.info("Initialized BrandRetrieval system")

    def _create_simple_embedding(self, text: str) -> np.ndarray:
        """
        Create a simple text embedding for development.

        In production, this should use Vertex AI Text Embeddings API or
        similar service for high-quality semantic embeddings.

        Args:
            text: Text to embed

        Returns:
            Numpy array representing the embedding
        """
        # Simple character-based embedding for Phase 2
        # This captures basic patterns like length, character distribution, etc.
        features = []

        # Feature 1: Text length (normalized)
        features.append(len(text) / 20.0)

        # Feature 2-3: Vowel and consonant ratios
        vowels = set('aeiouAEIOU')
        vowel_count = sum(1 for c in text if c in vowels)
        features.append(vowel_count / max(len(text), 1))
        features.append((len(text) - vowel_count) / max(len(text), 1))

        # Feature 4: Syllable estimate (simplified)
        syllable_count = max(1, vowel_count)
        features.append(syllable_count / 5.0)

        # Feature 5-9: Character type features
        features.append(sum(1 for c in text if c.isupper()) / max(len(text), 1))
        features.append(sum(1 for c in text if c.islower()) / max(len(text), 1))
        features.append(sum(1 for c in text if c.isdigit()) / max(len(text), 1))
        features.append(sum(1 for c in text if c.isspace()) / max(len(text), 1))
        features.append(sum(1 for c in text if not c.isalnum() and not c.isspace()) / max(len(text), 1))

        # Feature 10-14: Bigram features (common patterns)
        common_bigrams = ['th', 'er', 'on', 'an', 'in']
        text_lower = text.lower()
        for bigram in common_bigrams:
            features.append(text_lower.count(bigram) / max(len(text), 1))

        # Pad to fixed size
        while len(features) < 20:
            features.append(0.0)

        return np.array(features[:20], dtype=np.float32)

    def index_brands(self, brands: List[Dict[str, Any]]) -> None:
        """
        Index a list of brands for retrieval.

        Args:
            brands: List of brand dictionaries with metadata
        """
        logger.info(f"Indexing {len(brands)} brands...")

        self.brand_embeddings = []
        for brand in brands:
            brand_name = brand.get('brand_name', '')
            if not brand_name:
                continue

            # Create embedding
            embedding = self._create_simple_embedding(brand_name)

            # Store with metadata
            self.brand_embeddings.append(
                BrandEmbedding(
                    brand_name=brand_name,
                    embedding=embedding,
                    metadata=brand
                )
            )

        logger.info(f"Successfully indexed {len(self.brand_embeddings)} brands")

    def retrieve_similar_brands(
        self,
        query: str,
        top_k: int = 5,
        industry_filter: Optional[str] = None,
        personality_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve brands similar to the query.

        Args:
            query: Search query (e.g., product description or brand characteristics)
            top_k: Number of similar brands to return
            industry_filter: Optional industry filter
            personality_filter: Optional personality filter

        Returns:
            List of similar brand dictionaries with similarity scores

        Example:
            >>> retrieval = BrandRetrieval()
            >>> retrieval.index_brands(brand_dataset)
            >>> results = retrieval.retrieve_similar_brands(
            ...     "productivity app",
            ...     top_k=3,
            ...     industry_filter="technology"
            ... )
        """
        if not self.brand_embeddings:
            logger.warning("No brands indexed. Call index_brands() first.")
            return []

        logger.info(f"Retrieving top {top_k} similar brands for query: {query}")

        # Create query embedding
        query_embedding = self._create_simple_embedding(query)

        # Calculate similarity scores
        similarities = []
        for brand_emb in self.brand_embeddings:
            # Apply filters
            metadata = brand_emb.metadata
            if industry_filter and metadata.get('industry', '').lower() != industry_filter.lower():
                continue
            if personality_filter and metadata.get('personality', '').lower() != personality_filter.lower():
                continue

            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, brand_emb.embedding)

            similarities.append({
                'brand_name': brand_emb.brand_name,
                'similarity_score': float(similarity),
                'metadata': metadata
            })

        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        results = similarities[:top_k]

        logger.info(f"Retrieved {len(results)} similar brands")
        return results

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score (0-1)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def get_inspiration_from_brands(
        self,
        industry: str,
        personality: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get brand inspiration based on industry and personality.

        Args:
            industry: Target industry
            personality: Target brand personality
            top_k: Number of examples to return

        Returns:
            List of inspiring brand examples with analysis
        """
        logger.info(
            f"Getting brand inspiration for industry={industry}, "
            f"personality={personality}"
        )

        # Filter brands by criteria
        matching_brands = [
            brand_emb for brand_emb in self.brand_embeddings
            if (brand_emb.metadata.get('industry', '').lower() == industry.lower() or
                brand_emb.metadata.get('personality', '').lower() == personality.lower())
        ]

        # Return top matches
        results = [
            {
                'brand_name': brand.brand_name,
                'metadata': brand.metadata,
                'inspiration_reason': self._generate_inspiration_reason(brand.metadata)
            }
            for brand in matching_brands[:top_k]
        ]

        logger.info(f"Found {len(results)} inspiring brands")
        return results

    def _generate_inspiration_reason(self, metadata: Dict[str, Any]) -> str:
        """Generate a reason why this brand is inspiring."""
        strategy = metadata.get('naming_strategy', 'unknown')
        characteristics = ', '.join(metadata.get('characteristics', []))

        return (
            f"Uses {strategy} strategy with characteristics: {characteristics}"
        )


# Singleton instance for global use
_brand_retrieval_instance: Optional[BrandRetrieval] = None


def get_brand_retrieval() -> BrandRetrieval:
    """
    Get or create the global BrandRetrieval instance.

    Returns:
        BrandRetrieval singleton instance
    """
    global _brand_retrieval_instance

    if _brand_retrieval_instance is None:
        _brand_retrieval_instance = BrandRetrieval()

        # Auto-index with the dataset
        from src.data.brand_names_dataset import BRAND_NAMES_DATASET
        _brand_retrieval_instance.index_brands(BRAND_NAMES_DATASET)

    return _brand_retrieval_instance


def search_similar_brands(
    query: str,
    top_k: int = 5,
    industry: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for similar brands (convenience function for tool use).

    Args:
        query: Search query
        top_k: Number of results
        industry: Optional industry filter

    Returns:
        List of similar brands
    """
    retrieval = get_brand_retrieval()
    return retrieval.retrieve_similar_brands(
        query=query,
        top_k=top_k,
        industry_filter=industry
    )


# ADK FunctionTool Registration

def retrieve_similar_brands_tool(
    query: str,
    top_k: int = 5,
    industry: Optional[str] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    ADK FunctionTool for retrieving similar brand names from the database.

    This tool searches for brands similar to the query using semantic search
    and returns relevant examples with their metadata.

    Args:
        query: Search query describing the product, industry, or desired characteristics
        top_k: Number of similar brands to return (default: 5)
        industry: Optional industry filter to narrow results
        tool_context: ADK ToolContext for accessing session state

    Returns:
        Dictionary with 'similar_brands' list containing matching brand examples

    Example:
        >>> result = retrieve_similar_brands_tool("AI productivity app", top_k=3, industry="technology")
        >>> print(result['similar_brands'][0]['brand_name'])
        "Notion"
    """
    logger.info(f"RAG tool called with query='{query}', top_k={top_k}, industry={industry}")

    # Get the singleton retrieval instance
    retrieval = get_brand_retrieval()

    # Perform retrieval
    similar_brands = retrieval.retrieve_similar_brands(
        query=query,
        top_k=top_k,
        industry_filter=industry
    )

    # Log to tool_context if available
    if tool_context:
        logger.debug(f"Tool context available: session_id={getattr(tool_context, 'session_id', None)}")

    return {"similar_brands": similar_brands}


# Create the FunctionTool instance for use in agents
brand_retrieval_tool = FunctionTool(retrieve_similar_brands_tool)


# Legacy function for backward compatibility
def create_brand_retrieval_tool():
    """
    Create and return an ADK-compatible tool for brand retrieval.

    DEPRECATED: Use brand_retrieval_tool directly instead.

    Returns:
        FunctionTool instance that can be used by ADK agents
    """
    return brand_retrieval_tool
