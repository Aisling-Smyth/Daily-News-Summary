import logging
from typing import List

from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN

from config import (
    CLUSTER_EPS,
    CLUSTER_MIN_SAMPLES,
    EMBEDDING_MODEL,
)
from data_types import Story, StoryCluster


logger = logging.getLogger(__name__)


_model = None


def get_model() -> SentenceTransformer:
    """
    Load the embedding model lazily.

    Loading only when needed makes imports faster
    and avoids unnecessary model loading during tests.
    """

    global _model

    if _model is None:
        logger.info(
            "Loading embedding model: %s",
            EMBEDDING_MODEL,
        )
        _model = SentenceTransformer(
            EMBEDDING_MODEL
        )

    return _model


def cluster(
    stories: List[Story],
) -> List[StoryCluster]:
    """
    Group related stories using semantic similarity.

    Args:
        stories:
            Stories to cluster.

    Returns:
        List of related story groups.
    """

    if not stories:
        logger.warning(
            "No stories provided for clustering"
        )
        return []

    logger.info(
        "Clustering %d stories",
        len(stories),
    )

    titles = [
        story["title"]
        for story in stories
    ]

    try:
        model = get_model()

        embeddings = model.encode(
            titles,
            show_progress_bar=False,
        )

        labels = DBSCAN(
            eps=CLUSTER_EPS,
            min_samples=CLUSTER_MIN_SAMPLES,
            metric="cosine",
        ).fit_predict(
            embeddings
        )

        grouped = {}

        for label, story in zip(
            labels,
            stories,
        ):
            grouped.setdefault(
                label,
                [],
            ).append(
                story
            )

        clusters = list(
            grouped.values()
        )

        logger.info(
            "Created %d clusters",
            len(clusters),
        )

        for index, item in enumerate(
            clusters,
            start=1,
        ):
            logger.debug(
                "Cluster %d contains %d stories",
                index,
                len(item),
            )

        return clusters

    except Exception:
        logger.error(
            "Clustering failed",
            exc_info=True,
        )

        # Graceful fallback:
        # every story becomes its own cluster
        return [
            [story]
            for story in stories
        ]