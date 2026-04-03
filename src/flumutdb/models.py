from __future__ import annotations

from peewee import (
    AutoField,
    CharField,
    CompositeKey,
    DatabaseProxy,
    ForeignKeyField,
    IntegerField,
    Model,
    TextField,
)

database_proxy = DatabaseProxy()


class BaseModel(Model):
    pass


BaseModel._meta.database = database_proxy  # type: ignore[attr-defined]


class Segment(BaseModel):
    name = CharField(primary_key=True)
    number = IntegerField(null=True)
    references: list[Reference]
    proteins: list[Protein]

    class Meta:
        table_name = "segments"


class Reference(BaseModel):
    name = CharField(primary_key=True)
    segment = ForeignKeyField(Segment, column_name="segment_name", backref="references")
    sequence = TextField()
    sequence_id = CharField(null=True)
    annotations: list[Annotation]
    mutation_mappings: list[MutationMapping]

    class Meta:
        table_name = "references"


class Protein(BaseModel):
    name = CharField(primary_key=True)
    segment = ForeignKeyField(Segment, column_name="segment_name", backref="proteins")
    annotations: list[Annotation]
    mutations: list[Mutation]

    class Meta:
        table_name = "proteins"


class Annotation(BaseModel):
    start = IntegerField()
    end = IntegerField()
    protein = ForeignKeyField(
        Protein, column_name="protein_name", backref="annotations"
    )
    reference = ForeignKeyField(
        Reference, column_name="reference_name", backref="annotations"
    )

    class Meta:
        table_name = "annotations"
        primary_key = CompositeKey("start", "end", "protein", "reference")


class Mutation(BaseModel):
    name = CharField(primary_key=True)
    type = CharField()
    protein = ForeignKeyField(Protein, column_name="protein_name", backref="mutations")
    default_position = IntegerField(null=True)
    mappings: list[MutationMapping]
    markers: list[MarkerMutation]

    class Meta:
        table_name = "mutations"

    def __hash__(self):
        return hash(self.name)


class MutationMapping(BaseModel):
    id = AutoField()
    mutation = ForeignKeyField(
        Mutation, column_name="mutation_name", backref="mappings"
    )
    reference = ForeignKeyField(
        Reference, column_name="reference_name", backref="mutation_mappings"
    )
    position = IntegerField()
    ref_seq = CharField()
    alt_seq = CharField()

    class Meta:
        table_name = "mutation_mappings"


class Effect(BaseModel):
    name = CharField(primary_key=True)
    marker_effects: list[MarkerEffect]

    class Meta:
        table_name = "effects"


class Paper(BaseModel):
    id = CharField(primary_key=True)
    title = TextField()
    authors = TextField()
    year = IntegerField(null=True)
    journal = CharField(null=True)
    web_address = CharField(null=True)
    doi = CharField(null=True)
    marker_effects: list[MarkerEffect]

    class Meta:
        table_name = "papers"


class Marker(BaseModel):
    id = AutoField()
    notes = TextField(null=True)
    effects: list[MarkerEffect]
    marker_mutations: list[MarkerMutation]

    class Meta:
        table_name = "markers"


class MarkerEffect(BaseModel):
    marker = ForeignKeyField(Marker, column_name="marker_id", backref="effects")
    paper = ForeignKeyField(Paper, column_name="paper_id", backref="marker_effects")
    effect = ForeignKeyField(
        Effect, column_name="effect_name", backref="marker_effects"
    )
    subtype = CharField()
    in_vivo = IntegerField(null=True)
    in_vitro = IntegerField(null=True)

    class Meta:
        table_name = "markers_effects"
        primary_key = CompositeKey("marker", "paper", "effect", "subtype")


class MarkerMutation(BaseModel):
    marker = ForeignKeyField(
        Marker, column_name="marker_id", backref="marker_mutations"
    )
    mutation = ForeignKeyField(Mutation, column_name="mutation_name", backref="markers")

    class Meta:
        table_name = "markers_mutations"
        primary_key = False


class DbVersion(BaseModel):
    major = IntegerField()
    minor = IntegerField()
    date = CharField()

    class Meta:
        table_name = "db_version"
        primary_key = False
