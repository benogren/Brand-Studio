"""
Embedding generation for brand names using Vertex AI text-embedding-004.

This module handles:
- Generating embeddings for brand names and metadata
- Batch processing for efficient embedding generation
- Integration with Vertex AI Text Embeddings API
"""

import logging
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
import time

logger = logging.getLogger('brand_studio.embeddings')


@dataclass
class BrandEmbeddingData:
    """Data structure for a brand with its embedding."""
    brand_name: str
    embedding: List[float]
    metadata: Dict[str, Any]
    embedding_id: str  # Unique ID for vector search


class EmbeddingGenerator:
    """
    Generate embeddings for brand names using Vertex AI text-embedding-004.

    The text-embedding-004 model produces 768-dimensional embeddings optimized
    for semantic similarity search.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        model_name: str = "text-embedding-004"
    ):
        """
        Initialize the embedding generator.

        Args:
            project_id: GCP project ID (defaults to GOOGLE_CLOUD_PROJECT env var)
            location: GCP location (defaults to GOOGLE_CLOUD_LOCATION env var)
            model_name: Embedding model to use (default: text-embedding-004)
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = location or os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        self.model_name = model_name

        if not self.project_id:
            raise ValueError(
                "project_id must be provided or GOOGLE_CLOUD_PROJECT must be set"
            )

        logger.info(
            f"Initialized EmbeddingGenerator with project={self.project_id}, "
            f"location={self.location}, model={self.model_name}"
        )

        # Initialize Vertex AI
        self._initialize_vertex_ai()

    def _initialize_vertex_ai(self) -> None:
        """Initialize Vertex AI with project and location."""
        try:
            from google.cloud import aiplatform

            aiplatform.init(
                project=self.project_id,
                location=self.location
            )
            logger.info("Vertex AI initialized successfully")
        except ImportError:
            logger.error(
                "google-cloud-aiplatform not installed. "
                "Install with: pip install google-cloud-aiplatform"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            raise

    def _create_embedding_text(self, brand: Dict[str, Any]) -> str:
        """
        Create rich text representation of a brand for embedding.

        Combines brand name with metadata to create semantic-rich text that
        captures the brand's characteristics for better retrieval.

        Args:
            brand: Brand dictionary with metadata

        Returns:
            Text string to embed
        """
        brand_name = brand.get('brand_name', '')
        industry = brand.get('industry', '')
        category = brand.get('category', '')
        naming_strategy = brand.get('naming_strategy', '')
        syllables = brand.get('syllables', 0)

        # Create semantic-rich text
        text_parts = [
            f"Brand name: {brand_name}",
        ]

        if industry:
            text_parts.append(f"Industry: {industry}")

        if category:
            text_parts.append(f"Category: {category}")

        if naming_strategy:
            text_parts.append(f"Naming strategy: {naming_strategy}")

        if syllables:
            text_parts.append(f"Syllables: {syllables}")

        return ". ".join(text_parts)

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate a single embedding for text.

        Args:
            text: Text to embed

        Returns:
            768-dimensional embedding vector
        """
        try:
            from vertexai.language_models import TextEmbeddingModel

            model = TextEmbeddingModel.from_pretrained(self.model_name)
            embeddings = model.get_embeddings([text])

            if not embeddings:
                raise ValueError("No embedding returned from API")

            embedding_vector = embeddings[0].values
            logger.debug(f"Generated embedding with {len(embedding_vector)} dimensions")

            return embedding_vector

        except ImportError:
            logger.error(
                "vertexai not installed. Install with: pip install google-cloud-aiplatform"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def generate_brand_embeddings(
        self,
        brands: List[Dict[str, Any]],
        batch_size: int = 250
    ) -> List[BrandEmbeddingData]:
        """
        Generate embeddings for a list of brands with batch processing.

        The text-embedding-004 API supports up to 250 texts per request.

        Args:
            brands: List of brand dictionaries with metadata
            batch_size: Number of brands to process per API call (max 250)

        Returns:
            List of BrandEmbeddingData objects
        """
        logger.info(f"Generating embeddings for {len(brands)} brands...")

        if batch_size > 250:
            logger.warning(f"batch_size {batch_size} exceeds API limit. Using 250.")
            batch_size = 250

        try:
            from vertexai.language_models import TextEmbeddingModel

            model = TextEmbeddingModel.from_pretrained(self.model_name)

            all_embeddings = []
            total_batches = (len(brands) + batch_size - 1) // batch_size

            for batch_idx in range(0, len(brands), batch_size):
                batch = brands[batch_idx:batch_idx + batch_size]
                batch_num = (batch_idx // batch_size) + 1

                logger.info(
                    f"Processing batch {batch_num}/{total_batches} "
                    f"({len(batch)} brands)..."
                )

                # Create texts for embedding
                texts = [self._create_embedding_text(brand) for brand in batch]

                # Generate embeddings for batch
                try:
                    embeddings = model.get_embeddings(texts)

                    # Create BrandEmbeddingData objects
                    for i, (brand, embedding) in enumerate(zip(batch, embeddings)):
                        embedding_id = f"brand_{batch_idx + i}"

                        all_embeddings.append(
                            BrandEmbeddingData(
                                brand_name=brand.get('brand_name', ''),
                                embedding=embedding.values,
                                metadata=brand,
                                embedding_id=embedding_id
                            )
                        )

                    logger.info(
                        f"Batch {batch_num}/{total_batches} completed successfully"
                    )

                except Exception as e:
                    logger.error(f"Error processing batch {batch_num}: {e}")
                    # Continue with next batch on error
                    continue

                # Rate limiting: small delay between batches to avoid quota issues
                if batch_num < total_batches:
                    time.sleep(0.5)

            logger.info(
                f"Successfully generated embeddings for {len(all_embeddings)} brands"
            )
            return all_embeddings

        except ImportError:
            logger.error(
                "vertexai not installed. Install with: pip install google-cloud-aiplatform"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise

    def save_embeddings_to_jsonl(
        self,
        embeddings: List[BrandEmbeddingData],
        output_path: str
    ) -> None:
        """
        Save embeddings to JSONL format for Vector Search upload.

        Each line contains:
        {
          "id": "brand_0",
          "embedding": [0.1, 0.2, ...],
          "restricts": [{"namespace": "industry", "allow": ["technology"]}],
          "crowding_tag": "brand_name"
        }

        Args:
            embeddings: List of BrandEmbeddingData objects
            output_path: Path to output JSONL file
        """
        logger.info(f"Saving {len(embeddings)} embeddings to {output_path}...")

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for emb in embeddings:
                    # Create Vector Search record
                    record = {
                        "id": emb.embedding_id,
                        "embedding": emb.embedding,
                        "restricts": [
                            {
                                "namespace": "industry",
                                "allow": [emb.metadata.get('industry', '')]
                            },
                            {
                                "namespace": "category",
                                "allow": [emb.metadata.get('category', '')]
                            }
                        ],
                        "crowding_tag": emb.brand_name
                    }

                    # Write as single line JSON
                    f.write(json.dumps(record) + '\n')

            logger.info(f"Embeddings saved successfully to {output_path}")

        except Exception as e:
            logger.error(f"Failed to save embeddings: {e}")
            raise

    def save_metadata_to_json(
        self,
        embeddings: List[BrandEmbeddingData],
        output_path: str
    ) -> None:
        """
        Save brand metadata to JSON for lookup after retrieval.

        Creates a mapping from embedding_id to full brand metadata.

        Args:
            embeddings: List of BrandEmbeddingData objects
            output_path: Path to output JSON file
        """
        logger.info(f"Saving metadata for {len(embeddings)} brands to {output_path}...")

        try:
            metadata_map = {
                emb.embedding_id: {
                    "brand_name": emb.brand_name,
                    **emb.metadata
                }
                for emb in embeddings
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_map, f, indent=2, ensure_ascii=False)

            logger.info(f"Metadata saved successfully to {output_path}")

        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            raise


def generate_embeddings_for_dataset(
    dataset_path: str,
    output_embeddings_path: str,
    output_metadata_path: str,
    batch_size: int = 250
) -> Tuple[int, int]:
    """
    Generate embeddings for entire brand dataset.

    Convenience function that loads the dataset, generates embeddings,
    and saves both embedding JSONL and metadata JSON files.

    Args:
        dataset_path: Path to brand_names.json
        output_embeddings_path: Path for output embeddings JSONL
        output_metadata_path: Path for output metadata JSON
        batch_size: Batch size for API calls

    Returns:
        Tuple of (total_brands, successful_embeddings)
    """
    logger.info(f"Loading dataset from {dataset_path}...")

    try:
        # Load brand dataset
        with open(dataset_path, 'r', encoding='utf-8') as f:
            brands = json.load(f)

        total_brands = len(brands)
        logger.info(f"Loaded {total_brands} brands from dataset")

        # Generate embeddings
        generator = EmbeddingGenerator()
        embeddings = generator.generate_brand_embeddings(
            brands=brands,
            batch_size=batch_size
        )

        # Save outputs
        generator.save_embeddings_to_jsonl(embeddings, output_embeddings_path)
        generator.save_metadata_to_json(embeddings, output_metadata_path)

        successful_embeddings = len(embeddings)
        logger.info(
            f"Embedding generation complete: {successful_embeddings}/{total_brands} brands"
        )

        return total_brands, successful_embeddings

    except Exception as e:
        logger.error(f"Failed to generate embeddings for dataset: {e}")
        raise


if __name__ == "__main__":
    # Example usage / testing
    import sys
    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        dataset_path = "data/brand_names.json"

    output_embeddings = "data/brand_embeddings.jsonl"
    output_metadata = "data/brand_metadata.json"

    logger.info("Starting embedding generation...")
    total, successful = generate_embeddings_for_dataset(
        dataset_path=dataset_path,
        output_embeddings_path=output_embeddings,
        output_metadata_path=output_metadata
    )

    logger.info(f"✅ Done! Generated {successful}/{total} embeddings")
