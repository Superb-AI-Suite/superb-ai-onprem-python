"""Behavioral tests for canonical Slice.caption read/write support.

Real params, query, entity, and service objects are used. Only the
BaseService HTTP/GraphQL transport boundary is stubbed.
"""
from unittest.mock import Mock

from spb_onprem.slices.entities import Slice
from spb_onprem.slices.params.update_slice import update_slice_params
from spb_onprem.slices.queries import Queries, Schemas
from spb_onprem.slices.service import SliceService


class TestSliceCaptionEntity:
    def test_slice_deserializes_caption(self):
        slice_obj = Slice.model_validate({
            "id": "slice-456",
            "datasetId": "dataset-123",
            "caption": "one aggregate caption",
        })

        assert slice_obj.caption == "one aggregate caption"

    def test_slice_caption_defaults_to_none(self):
        slice_obj = Slice.model_validate({
            "id": "slice-456",
            "datasetId": "dataset-123",
        })

        assert slice_obj.caption is None


class TestSliceCaptionQuery:
    def test_slice_schema_selects_caption(self):
        assert "caption" in Schemas.SLICE.split()

    def test_update_query_declares_and_sends_caption(self):
        query = Queries.UPDATE_SLICE["query"]

        assert "$caption: String" in query
        assert "caption: $caption" in query
        assert Queries.UPDATE_SLICE["variables"] is update_slice_params

    def test_unguarded_update_query_omits_expected_caption(self):
        query = Queries.UPDATE_SLICE["query"]

        assert "$expectedCaption" not in query
        assert "expectedCaption" not in query

    def test_guarded_update_query_declares_and_sends_expected_caption(self):
        query = Queries.UPDATE_SLICE_WITH_EXPECTED_CAPTION["query"]

        assert "$expectedCaption: String" in query
        assert "expectedCaption: $expectedCaption" in query
        assert Queries.UPDATE_SLICE_WITH_EXPECTED_CAPTION["name"] == "updateSlice"
        assert Queries.UPDATE_SLICE_WITH_EXPECTED_CAPTION["variables"] is update_slice_params


class TestUpdateSliceCaptionParams:
    def test_undefined_caption_is_omitted(self):
        variables = update_slice_params(
            dataset_id="dataset-123",
            slice_id="slice-456",
        )

        assert "caption" not in variables

    def test_none_caption_is_sent_as_null(self):
        variables = update_slice_params(
            dataset_id="dataset-123",
            slice_id="slice-456",
            slice_caption=None,
        )

        assert "caption" in variables
        assert variables["caption"] is None

    def test_string_caption_is_sent_exactly(self):
        variables = update_slice_params(
            dataset_id="dataset-123",
            slice_id="slice-456",
            slice_caption="one aggregate caption",
        )

        assert variables["caption"] == "one aggregate caption"

    def test_undefined_expected_caption_is_omitted(self):
        variables = update_slice_params(
            dataset_id="dataset-123",
            slice_id="slice-456",
        )

        assert "expectedCaption" not in variables

    def test_none_expected_caption_is_sent_as_null(self):
        variables = update_slice_params(
            dataset_id="dataset-123",
            slice_id="slice-456",
            expected_caption=None,
        )

        assert "expectedCaption" in variables
        assert variables["expectedCaption"] is None

    def test_empty_expected_caption_is_preserved(self):
        variables = update_slice_params(
            dataset_id="dataset-123",
            slice_id="slice-456",
            expected_caption="",
        )

        assert variables["expectedCaption"] == ""

    def test_string_expected_caption_is_sent_exactly(self):
        variables = update_slice_params(
            dataset_id="dataset-123",
            slice_id="slice-456",
            expected_caption="observed caption",
        )

        assert variables["expectedCaption"] == "observed caption"


class TestSliceServiceCaption:
    def setup_method(self):
        self.slice_service = SliceService()
        self.slice_service.request_gql = Mock()

    def _sent_variables(self):
        args, kwargs = self.slice_service.request_gql.call_args
        return kwargs.get("variables") or args[1]

    def _sent_query(self):
        args, _ = self.slice_service.request_gql.call_args
        return args[0]

    def test_get_slice_returns_caption(self):
        self.slice_service.request_gql.return_value = {
            "id": "slice-456",
            "datasetId": "dataset-123",
            "caption": "one aggregate caption",
        }

        result = self.slice_service.get_slice(
            dataset_id="dataset-123",
            slice_id="slice-456",
        )

        assert result.caption == "one aggregate caption"

    def test_get_slices_returns_caption_across_the_http_graphql_boundary(self):
        class ProjectingGraphQLResponse:
            status_code = 200
            elapsed = None

            def __init__(self, payload):
                slice_payload = {
                    "id": "slice-456",
                    "name": "training",
                }
                if "caption" in payload["query"].split():
                    slice_payload["caption"] = "one aggregate caption"
                self._body = {
                    "data": {
                        "slices": {
                            "slices": [slice_payload],
                            "next": None,
                            "totalCount": 1,
                        },
                    },
                }

            def raise_for_status(self):
                return None

            def json(self):
                return self._body

        class GraphQLSessionFake:
            def post(self, _endpoint, json, _headers=None, **kwargs):
                headers = kwargs.get("headers", _headers)
                assert headers is not None
                return ProjectingGraphQLResponse(json)

            def close(self):
                return None

        self.slice_service.request_gql = SliceService.request_gql.__get__(
            self.slice_service,
            SliceService,
        )
        self.slice_service.requests_retry_session = lambda: GraphQLSessionFake()

        slices, next_cursor, total_count = self.slice_service.get_slices(
            dataset_id="dataset-123",
        )

        assert slices[0].caption == "one aggregate caption"
        assert next_cursor is None
        assert total_count == 1

    def test_update_slice_sends_and_returns_caption(self):
        self.slice_service.request_gql.return_value = {
            "id": "slice-456",
            "datasetId": "dataset-123",
            "caption": "one aggregate caption",
        }

        result = self.slice_service.update_slice(
            dataset_id="dataset-123",
            slice_id="slice-456",
            caption="one aggregate caption",
        )

        assert self._sent_variables()["caption"] == "one aggregate caption"
        assert result.caption == "one aggregate caption"

    def test_update_slice_none_sends_null(self):
        self.slice_service.request_gql.return_value = {
            "id": "slice-456",
            "datasetId": "dataset-123",
        }

        self.slice_service.update_slice(
            dataset_id="dataset-123",
            slice_id="slice-456",
            caption=None,
        )

        variables = self._sent_variables()
        assert "caption" in variables
        assert variables["caption"] is None

    def test_update_slice_without_caption_stays_compatible(self):
        self.slice_service.request_gql.return_value = {
            "updateSlice": {
                "id": "slice-456",
                "datasetId": "dataset-123",
                "name": "renamed",
            },
        }

        result = self.slice_service.update_slice(
            dataset_id="dataset-123",
            slice_id="slice-456",
            name="renamed",
        )

        assert self._sent_variables() == {
            "dataset_id": "dataset-123",
            "id": "slice-456",
            "name": "renamed",
        }
        assert result.name == "renamed"

    def test_omitted_expected_caption_uses_unguarded_query(self):
        self.slice_service.request_gql.return_value = {
            "id": "slice-456",
            "datasetId": "dataset-123",
        }

        self.slice_service.update_slice(
            dataset_id="dataset-123",
            slice_id="slice-456",
            caption="next caption",
        )

        assert self._sent_query() is Queries.UPDATE_SLICE
        assert "expectedCaption" not in self._sent_variables()

    def test_none_expected_caption_uses_guarded_query_and_sends_null(self):
        self.slice_service.request_gql.return_value = {
            "id": "slice-456",
            "datasetId": "dataset-123",
        }

        self.slice_service.update_slice(
            dataset_id="dataset-123",
            slice_id="slice-456",
            caption="next caption",
            expected_caption=None,
        )

        assert self._sent_query() is Queries.UPDATE_SLICE_WITH_EXPECTED_CAPTION
        assert self._sent_variables()["expectedCaption"] is None

    def test_empty_expected_caption_uses_guarded_query(self):
        self.slice_service.request_gql.return_value = {
            "id": "slice-456",
            "datasetId": "dataset-123",
        }

        self.slice_service.update_slice(
            dataset_id="dataset-123",
            slice_id="slice-456",
            caption="next caption",
            expected_caption="",
        )

        assert self._sent_query() is Queries.UPDATE_SLICE_WITH_EXPECTED_CAPTION
        assert self._sent_variables()["expectedCaption"] == ""

    def test_value_expected_caption_uses_guarded_query(self):
        self.slice_service.request_gql.return_value = {
            "id": "slice-456",
            "datasetId": "dataset-123",
            "caption": "next caption",
        }

        result = self.slice_service.update_slice(
            dataset_id="dataset-123",
            slice_id="slice-456",
            caption="next caption",
            expected_caption="observed caption",
        )

        assert self._sent_query() is Queries.UPDATE_SLICE_WITH_EXPECTED_CAPTION
        assert self._sent_variables()["expectedCaption"] == "observed caption"
        assert result.caption == "next caption"

    def test_existing_positional_arguments_keep_their_meaning(self):
        self.slice_service.request_gql.return_value = {
            "id": "slice-456",
            "datasetId": "dataset-123",
            "name": "renamed",
            "description": "updated description",
            "caption": "next caption",
        }

        self.slice_service.update_slice(
            "dataset-123",
            "slice-456",
            "renamed",
            "updated description",
            "next caption",
        )

        assert self._sent_query() is Queries.UPDATE_SLICE
        assert self._sent_variables() == {
            "dataset_id": "dataset-123",
            "id": "slice-456",
            "name": "renamed",
            "description": "updated description",
            "caption": "next caption",
        }
