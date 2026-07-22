import logging
from typing import List

from data_types import StoryCluster


logger = logging.getLogger(__name__)


SOURCE_WEIGHT = 100


def score_cluster(
    cluster: StoryCluster,
) -> int:
    """
    Score a story cluster by coverage.

    Independent sources are weighted more heavily
    than repeated articles from the same source.

    Args:
        cluster:
            Related stories.

    Returns:
        Importance score.
    """

    unique_sources = len(
        {
            story["source"]
            for story in cluster
        }
    )

    article_count = len(
        cluster
    )

    return (
        unique_sources * SOURCE_WEIGHT
        + article_count
    )


def rank(
    clusters: List[StoryCluster],
    limit: int = 3,
) -> List[StoryCluster]:
    """
    Rank clusters by news coverage.

    Args:
        clusters:
            Story clusters.

        limit:
            Maximum number of clusters returned.

    Returns:
        Highest-ranked story clusters.
    """

    if not clusters:
        logger.warning(
            "No clusters to rank"
        )
        return []

    ranked = sorted(
        clusters,
        key=score_cluster,
        reverse=True,
    )

    top_clusters = ranked[:limit]

    logger.info(
        "Ranked %d clusters, returning top %d",
        len(clusters),
        len(top_clusters),
    )

    for index, cluster in enumerate(
        top_clusters,
        start=1,
    ):
        logger.debug(
            "Rank %d: %d articles from %d sources",
            index,
            len(cluster),
            len(
                {
                    story["source"]
                    for story in cluster
                }
            ),
        )

    return top_clusters