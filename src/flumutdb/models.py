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

    def __str__(self) -> str:
        return str(self.name)

    _cache: list[Segment] = []

    @staticmethod
    def all(force_reload: bool = False) -> list[Segment]:
        """Return all Segment instances, cached after first call.

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

    def __str__(self) -> str:
        return f"{self.segment}/{self.name}"


class Reference(BaseModel):
    name = CharField()
    segment = ForeignKeyField(Segment, backref="references")
    sequence = TextField()
    source = CharField()
    annotations: list[Annotation]
    mappings: list[Mapping]

    def __str__(self) -> str:
        return f"{self.segment}/{self.name}"

    _cache: list[Reference] = []

    @staticmethod
    def all(force_reload: bool = False) -> list[Reference]:
        """Return all Reference instances, cached after first call.

        Args:
            force_reload: Re-fetch from the database even if already cached.
        """
        if not Reference._cache or force_reload:
            Reference._cache = [ref for seg in Segment.all() for ref in seg.references]
        return Reference._cache


class Annotation(BaseModel):
    protein = ForeignKeyField(Protein, backref="annotations")
    reference = ForeignKeyField(Reference, backref="annotations")
    start = IntegerField()
    end = IntegerField()

    def __str__(self) -> str:
        return f"{self.protein} @ {self.reference}: {self.start}-{self.end}"


class Mutation(BaseModel):
    name = CharField(unique=True)
    type = CharField(choices=[(t.value, t.name) for t in MutationType])
    protein = ForeignKeyField(Protein, backref="mutations")
    default_position = IntegerField(null=True)
    mappings: list[Mapping]
    markers: list[Marker]

    def __str__(self) -> str:
        return str(self.name)


class Mapping(BaseModel):
    mutation = ForeignKeyField(Mutation, backref="mappings")
    reference = ForeignKeyField(Reference, backref="mappings")
    mutation_name = CharField(null=True)
    position = IntegerField()
    alteration = CharField()

    def __str__(self) -> str:
        return f"{self.mutation} @ {self.reference} (pos {self.position}, {self.alteration})"


class Effect(BaseModel):
    name = CharField()
    evidences: list[Evidence]

    def __str__(self) -> str:
        return str(self.name)


class Subtype(BaseModel):
    name = CharField()
    evidences: list[Evidence]

    def __str__(self) -> str:
        return str(self.name)


class Host(BaseModel):
    name = CharField()
    evidences: list[Evidence]

    def __str__(self) -> str:
        return str(self.name)


class Paper(BaseModel):
    short_name = CharField(unique=True)
    title = TextField()
    authors = TextField()
    year = IntegerField(null=True)
    journal = CharField(null=True)
    url = CharField(null=True)
    doi = CharField(null=True)
    evidences: list[Evidence]

    def __str__(self) -> str:
        return str(self.short_name)


class Marker(BaseModel):
    name = CharField(unique=True, null=True)
    mutations = ManyToManyField(Mutation, backref="markers")
    evidences: list[Evidence]

    def __str__(self) -> str:
        mutations = ", ".join(str(m) for m in self.mutations)
        return f"Marker({mutations})"

    _cache: List[Marker] = []

    @staticmethod
    def all(force_reload: bool = False) -> list[Marker]:
        """Returns a list of all Marker instances, cached after first call.

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

    def __str__(self) -> str:
        return f"{self.marker}: {self.effect} in {self.subtype} ({self.paper})"


class DbVersion(BaseModel):
    major = IntegerField()
    minor = IntegerField()
    date = CharField()

    def __str__(self) -> str:
        return f"{self.major}.{self.minor} ({self.date})"

    @staticmethod
    def is_compatible() -> bool:
        version: DbVersion = DbVersion.get_or_none()
        if version is None:
            raise MissingVersionError()
        if version.major != REQUIRED_MAJOR_VERSION:
            raise IncompatibleVersionError(version, REQUIRED_MAJOR_VERSION)
        return True
