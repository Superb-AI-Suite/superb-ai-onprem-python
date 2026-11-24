"""The data list filter models have every field of the platform's filter inputs (MOD2-99).

Incident 2026-11-24: the platform sent ``{"must": {"captionSemanticQuery": "blue"}}``
to an action, the SDK did not know the field and dropped it, and the action
rewrote the captions of the whole dataset. These tests walk the GraphQL
``DataFilter`` input of the schema copy in ``tests/fixtures`` together with
``DataListFilter`` and fail when the schema has a field the SDK model lacks.
When the platform adds a filter field, refresh the schema copy (see
``tests/test_graphql_documents.py``) and these tests name the field to add.
"""
import typing
from pathlib import Path

import pytest
from pydantic import BaseModel

graphql = pytest.importorskip("graphql")  # graphql-core, a test-only dependency (MIT)

from spb_onprem.data.params import DataFilter, DataListFilter  # noqa: E402

SCHEMA_FILE = Path(__file__).parent.parent / "fixtures" / "zenith-schema-public.gql"


def _schema():
    return graphql.build_schema(SCHEMA_FILE.read_text())


def _sent_name(name, field) -> str:
    """The GraphQL field name the SDK sends for a model field (``model_dump(by_alias=True)``)."""
    return field.serialization_alias or field.alias or name


def _model_in(annotation):
    """The pydantic model inside ``Optional[List[Model]]`` and similar, or None."""
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return annotation
    for arg in typing.get_args(annotation):
        found = _model_in(arg)
        if found is not None:
            return found
    return None


def _pairs(schema, input_name, model, seen=None):
    """(GraphQL input type, SDK model) pairs reachable from one filter input."""
    seen = {} if seen is None else seen
    if input_name in seen:
        return seen
    seen[input_name] = model
    input_type = schema.get_type(input_name)
    fields = {_sent_name(name, field): field for name, field in model.model_fields.items()}
    for gql_name, gql_field in input_type.fields.items():
        named = graphql.get_named_type(gql_field.type)
        if not isinstance(named, graphql.GraphQLInputObjectType) or gql_name not in fields:
            continue
        nested = _model_in(fields[gql_name].annotation)
        if nested is not None:
            _pairs(schema, named.name, nested, seen)
    return seen


# Fields the schema has but the SDK deliberately does not accept: (GraphQL input, field) -> reason.
# test_not_accepted_list_is_current fails when an entry goes stale, so remove it then.
NOT_ACCEPTED = {
    # c349959 (2026-04-29) dropped direct sliceId so it does not overlap the slice filter.
    ("DataFilterOptions", "sliceId"): "c349959: overlaps the slice filter",
}

ROOTS = [("DataFilter", DataListFilter), ("DataFilter", DataFilter)]
PAIRS = sorted(
    {
        (input_name, model)
        for root, root_model in ROOTS
        for input_name, model in _pairs(_schema(), root, root_model).items()
    },
    key=lambda pair: (pair[0], pair[1].__name__),
)


def test_walk_reaches_every_filter_input():
    """Guards the walk itself: the nested inputs are found, not only the root."""
    reached = {input_name for input_name, _ in PAIRS}
    assert {
        "DataFilterOptions", "DataSliceFilter", "DataSlicePropertiesFilter", "FrameFilter",
        "FrameFilterOptions", "FrameCountsFilter", "AnnotationCountsFilter", "MetaFilter",
        "DateTimeRangeFilterOption", "RelativeDateOption", "UserFilterOption", "NumericRangeFilter",
        "DataSliceCommentFilterOption", "DistanceCountFilter", "GeoLocationFilter",
    } <= reached


@pytest.mark.parametrize("input_name,model", PAIRS, ids=[f"{i}-{m.__name__}" for i, m in PAIRS])
def test_model_has_every_schema_field(input_name, model):
    schema_fields = set(_schema().get_type(input_name).fields)
    model_fields = {_sent_name(name, field) for name, field in model.model_fields.items()}
    not_accepted = {field for (name, field) in NOT_ACCEPTED if name == input_name}
    missing = sorted(schema_fields - model_fields - not_accepted)
    assert missing == [], f"{model.__name__} lacks fields of GraphQL {input_name}: {missing}"


@pytest.mark.parametrize("input_name,field", sorted(NOT_ACCEPTED))
def test_not_accepted_list_is_current(input_name, field):
    """An entry is stale when the schema drops the field or the SDK starts accepting it."""
    models = [model for name, model in PAIRS if name == input_name]
    assert models, f"GraphQL {input_name} is not reached from DataFilter"
    assert field in _schema().get_type(input_name).fields, (
        f"GraphQL {input_name} no longer has {field}; remove it from NOT_ACCEPTED"
    )
    for model in models:
        model_fields = {_sent_name(name, f) for name, f in model.model_fields.items()}
        assert field not in model_fields, (
            f"{model.__name__} now has {field}; remove it from NOT_ACCEPTED"
        )


@pytest.mark.parametrize("input_name,model", PAIRS, ids=[f"{i}-{m.__name__}" for i, m in PAIRS])
def test_model_sends_only_schema_fields(input_name, model):
    schema_fields = set(_schema().get_type(input_name).fields)
    model_fields = {_sent_name(name, field) for name, field in model.model_fields.items()}
    extra = sorted(model_fields - schema_fields)
    assert extra == [], f"{model.__name__} sends fields GraphQL {input_name} does not have: {extra}"
