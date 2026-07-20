import logging
from typing import List

from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN

from data_types import Story, StoryCluster

logger = logging.getLogger(__name__)

model = SentenceTransformer("all-MiniLM-L6-v2")

def cluster(stories: List[Story]) -> List[StoryCluster]:
    """Cluster stories by semantic similarity using embeddings and DBSCAN.

    Args:
        stories: List of story dictionaries with a 'title' field.

    Returns:
        List[StoryCluster]: Clusters of related story objects.
    """
    if not stories:
        logger.warning("No stories to cluster")
        return []
    
    logger.info(f"Clustering {len(stories)} stories...")
    
    titles = [s["title"] for s in stories]
    
    try:
        logger.debug("Encoding titles with SentenceTransformer...")
        emb = model.encode(titles)
        
        logger.debug("Running DBSCAN clustering...")
        labels = DBSCAN(
            eps=0.35,
            min_samples=1,
            metric="cosine"
        ).fit_predict(emb)
        
        grouped = {}
        for label, story in zip(labels, stories):
            grouped.setdefault(label, []).append(story)
        
        clusters = list(grouped.values())
        logger.info(f"Created {len(clusters)} clusters")
        for i, c in enumerate(clusters):
            logger.debug(f"Cluster {i}: {len(c)} stories")
        
        return clusters
    
    except Exception as e:
        logger.error(f"Clustering failed: {e}", exc_info=True)
        # Fallback: return each story as its own cluster
        logger.warning("Falling back to individual stories as clusters")
        return [[s] for s in stories]
