from typing import List, Tuple, TypedDict


class Story(TypedDict):
    """
    Individual RSS story.
    """

    title: str
    summary: str
    link: str
    source: str
    category: str


StoryCluster = List[Story]


class SummaryEntry(TypedDict):
    """
    Generated newsletter story summary.
    """

    headline: str
    summary: str
    link: str


SectionMeta = List[
    Tuple[str, List[SummaryEntry]]
]