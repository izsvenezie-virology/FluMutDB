from __future__ import annotations

from enum import Enum
from typing import List

from peewee import (
    CharField,
    DatabaseProxy,
    ForeignKeyField,
    IntegerField,
    ManyToManyField,
    Model,
    TextField,
    prefetch,
)

from flumutdb.exceptions import IncompatibleVersionError, MissingVersionError

REQUIRED_MAJOR_VERSION = 7

database_proxy = DatabaseProxy()


class MutationType(Enum):
    SNP = "SNP"


class BaseModel(Model):
    notes = TextField(null=True)


BaseModel._meta.database = database_proxy  # type: ignore[attr-defined]


class Segment(BaseModel):
    name = CharField()
    proteins: list[Protein]
    references: list[Reference]

    _cache: list[Segment] = []

    @staticmethod
    def load(force_reload: bool = False) -> list[Segment]:
        """Load Segment→MutationMapping into memory via prefetch, cached after first call.

        Args:
            force_reload: Re-fetch from the database even if already cached.
        """
        if not Segment._cache or force_reload:
            Segment._cache = list(
                prefetch(
                    Segment.select(),
                    Reference.select(),
                    Protein.select(),
                    Annotation.select(),
                    Mutation.select(),
                    Mapping.select(),
                )
            )
        return Segment._cache

    @staticmethod
    def clear_cache():
        """Clear the Segment cache, forcing a reload on next access."""
        Segment._cache = []


class Protein(BaseModel):
    name = CharField()
    segment = ForeignKeyField(Segment, backref="proteins")
    annotations: list[Annotation]
    mutations: list[Mutation]


class Reference(BaseModel):
    name = CharField()
    segment = ForeignKeyField(Segment, backref="references")
    sequence = TextField()
    source = CharField()
    annotations: list[Annotation]
    mappings: list[Mapping]


class Annotation(BaseModel):
    protein = ForeignKeyField(Protein, backref="annotations")
    reference = ForeignKeyField(Reference, backref="annotations")
    start = IntegerField()
    end = IntegerField()


class Mutation(BaseModel):
    name = CharField(unique=True)
    type = CharField(choices=[(t.value, t.name) for t in MutationType])
    protein = ForeignKeyField(Protein, backref="mutations")
    default_position = IntegerField(null=True)
    mappings: list[Mapping]
    markers: list[Marker]


class Mapping(BaseModel):
    mutation = ForeignKeyField(Mutation, backref="mappings")
    reference = ForeignKeyField(Reference, backref="mappings")
    mutation_name = CharField(null=True)
    position = IntegerField()
    alteration = CharField()


class Effect(BaseModel):
    name = CharField()
    evidences: list[Evidence]


class Subtype(BaseModel):
    name = CharField()
    evidences: list[Evidence]


class Host(BaseModel):
    name = CharField()
    evidences: list[Evidence]


class Paper(BaseModel):
    short_name = CharField(unique=True)
    title = TextField()
    authors = TextField()
    year = IntegerField(null=True)
    journal = CharField(null=True)
    url = CharField(null=True)
    doi = CharField(null=True)
    evidences: list[Evidence]


class Marker(BaseModel):
    _cache: List[Marker] = []
    mutations = ManyToManyField(Mutation, backref="markers")
    evidences: list[Evidence]

    @staticmethod
    def load(force_reload: bool = False) -> list[Marker]:
        """Load Markers into memory, cached after first call.

        Args:
            force_reload: Re-fetch from the database even if already cached.
        """
        if not Marker._cache or force_reload:
            Marker._cache = list(
                prefetch(
                    Marker.select(),
                    Mutation.select(),
                    Evidence.select(),
                    Paper.select(),
                    Effect.select(),
                )
            )
        return Marker._cache

    @staticmethod
    def clear_cache():
        """Clear the Marker cache, forcing a reload on next access."""
        Marker._cache = []


class Evidence(BaseModel):
    marker = ForeignKeyField(Marker, backref="evidences")
    paper = ForeignKeyField(Paper, backref="evidences")
    effect = ForeignKeyField(Effect, backref="evidences")
    subtype = ForeignKeyField(Subtype, backref="evidences")
    host = ForeignKeyField(Host, backref="evidences", null=True)


class DbVersion(BaseModel):
    major = IntegerField()
    minor = IntegerField()
    date = CharField()

    def __str__(self):
        return f"{self.major}.{self.minor} ({self.date})"

    @staticmethod
    def check_compatibility():
        version: DbVersion = DbVersion.get_or_none()
        if version is None:
            raise MissingVersionError()
        if version.major != REQUIRED_MAJOR_VERSION:
            raise IncompatibleVersionError(version, REQUIRED_MAJOR_VERSION)
