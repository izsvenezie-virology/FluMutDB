from peewee import prefetch

from .models import (
    Annotation,
    Effect,
    Marker,
    MarkerMutation,
    Mutation,
    MutationMapping,
    Paper,
    Protein,
    Reference,
    Segment,
)

_segments_cache: list[Segment] = []
_markers_cache: list[Marker] = []


def load_segments(force_reload: bool = False) -> list[Segment]:
    """Load Segment→MutationMapping into memory via prefetch, cached after first call.

    Args:
        force_reload: Re-fetch from the database even if already cached.
    """
    global _segments_cache
    if not _segments_cache or force_reload:
        _segments_cache = list(
            prefetch(
                Segment.select(),
                Reference.select(),
                Protein.select(),
                Annotation.select(),
                Mutation.select(),
                MutationMapping.select(),
            )
        )
    return _segments_cache


def load_markers(force_reload: bool = False) -> list[Marker]:
    """Load Markers into memory, cached after first call.

    Args:
        force_reload: Re-fetch from the database even if already cached.
    """
    global _markers_cache
    if not _markers_cache or force_reload:
        _markers_cache = list(
            prefetch(
                Marker.select(),
                Mutation.select(),
                MarkerMutation.select(),
                Paper.select(),
                Effect.select(),
            )
        )
    return _markers_cache


def _clear_cache() -> None:
    global _segments_cache
    global _markers_cache
    _segments_cache = []
    _markers_cache = []
