import logging
from typing import List

from data_types import StoryCluster

logger = logging.getLogger(__name__)

def rank(clusters: List[StoryCluster]) -> List[StoryCluster]:
    """Rank clusters by size (most similar stories first).

    Args:
        clusters: List of story clusters.

    Returns:
        List[StoryCluster]: Sorted clusters by descending story count.
    """
    if not clusters:
        logger.warning("No clusters to rank")
        return []
    
    ranked = sorted(clusters, key=lambda c: len(c), reverse=True)
    logger.info(f"Ranked {len(ranked)} clusters")
    return ranked