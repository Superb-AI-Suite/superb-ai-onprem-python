"""The data list queries always send a fixed createdAt order (FDE-361).

Without ``orderBy`` the server orders ``dataList`` by ``updatedAt DESC`` and
pages with a cursor on that value, so data updated during paging is skipped or
returned twice. The SDK fixes the order to ``createdAt`` ascending (oldest first);
callers cannot change it.
"""
from pathlib import Path
from unittest.mock import Mock

import pytest

from spb_onprem.data.params import DataListFilter, get_data_id_list_params, get_data_list_params
from spb_onprem.data.queries import Queries
from spb_onprem.data.service import DataService

EXPECTED_ORDER_BY = {"field": "createdAt", "direction": "ASC"}
SCHEMA_FILE = Path(__file__).parent.parent / "fixtures" / "zenith-schema-public.gql"


@pytest.mark.parametrize("make_params", [get_data_list_params, get_data_id_list_params])
def test_params_always_order_by_created_at(make_params):
    assert make_params(dataset_id="dataset-1")["order_by"] == EXPECTED_ORDER_BY
    with_everything = make_params(
        dataset_id="dataset-1",
        data_filter=DataListFilter.model_validate({"must": {"keyContains": "a"}}),
        cursor="cursor-1",
        length=50,
    )
    assert with_everything["order_by"] == EXPECTED_ORDER_BY


@pytest.mark.parametrize("make_params", [get_data_list_params, get_data_id_list_params])
def test_params_return_a_fresh_order_by_each_call(make_params):
    first = make_params(dataset_id="dataset-1")
    first["order_by"]["direction"] = "changed"
    assert make_params(dataset_id="dataset-1")["order_by"] == EXPECTED_ORDER_BY


@pytest.mark.parametrize("key", ["GET_LIST", "GET_ID_LIST"])
def test_queries_pass_the_order_to_data_list(key):
    query = " ".join(getattr(Queries, key)["query"].split())
    assert "$order_by: DataOrderBy" in query
    assert "orderBy: $order_by" in query


def test_order_is_a_valid_data_order_by_in_the_schema():
    graphql = pytest.importorskip("graphql")
    schema = graphql.build_schema(SCHEMA_FILE.read_text())
    assert EXPECTED_ORDER_BY["field"] in schema.get_type("DataOrderField").values
    assert EXPECTED_ORDER_BY["direction"] in schema.get_type("OrderDirection").values
    for key in ("GET_LIST", "GET_ID_LIST"):
        received = {}

        def data_list(info, **args):
            received.update(args)
            return {"data": [], "next": None, "totalCount": 0, "selectedFrames": []}

        # Executes the real document with the real variables against the schema, so the
        # server-side variable coercion (DataOrderBy, enum values) runs as it would on zenith.
        result = graphql.graphql_sync(
            schema,
            getattr(Queries, key)["query"],
            root_value={"dataList": data_list},
            variable_values=getattr(Queries, key)["variables"](dataset_id="dataset-1"),
        )
        assert not result.errors, [error.message for error in result.errors]
        assert received["orderBy"] == EXPECTED_ORDER_BY


class TestServiceSendsOrder:
    def setup_method(self):
        self.service = DataService()
        self.service.request_gql = Mock(return_value={
            "data": [{"id": "data-1"}],
            "next": "cursor-2",
            "totalCount": 3,
            "selectedFrames": [],
        })

    def _sent(self, expected_query):
        query, variables = self.service.request_gql.call_args[0]
        assert query is expected_query
        return variables

    def test_get_data_list_sends_created_at_order(self):
        result = self.service.get_data_list(dataset_id="dataset-1", cursor="cursor-1", length=2)
        variables = self._sent(Queries.GET_LIST)
        assert variables["order_by"] == EXPECTED_ORDER_BY
        assert variables["cursor"] == "cursor-1"
        assert variables["length"] == 2
        data, next_cursor, total = result
        assert [item.id for item in data] == ["data-1"]
        assert (next_cursor, total) == ("cursor-2", 3)

    def test_get_data_id_list_sends_created_at_order(self):
        data_filter = DataListFilter.model_validate({"slice": {"id": "slice-1"}})
        result = self.service.get_data_id_list(
            dataset_id="dataset-1", data_filter=data_filter, include_selected_frames=True
        )
        variables = self._sent(Queries.GET_ID_LIST)
        assert variables["order_by"] == EXPECTED_ORDER_BY
        assert variables["filter"] == {"slice": {"id": "slice-1"}}
        assert len(result) == 4
