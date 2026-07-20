from typing import List, TypedDict


class Story(TypedDict):
    title: str
    summary: str
    link: str
    source: str
    category: str


StoryCluster = List[Story]


class SummaryEntry(TypedDict):
    headline: str
    summary: str
    link: str


SectionMeta = List[tuple[str, List[SummaryEntry]]]
