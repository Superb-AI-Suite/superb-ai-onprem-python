"""Chicago-style TDD tests for caption support in update_data.

Real params/query/entity objects are used throughout; only the
BaseService network boundary (request_gql) is mocked.
"""
from unittest.mock import Mock

from spb_onprem.data.service import DataService
from spb_onprem.data.queries import Queries, Schemas
from spb_onprem.data.params.update_data import update_params
from spb_onprem.data.entities import Data


class TestUpdateParamsCaption:
    """update_params must follow Undefined/None/value semantics for caption."""

    def test_caption_undefined_is_omitted(self):
        variables = update_params(
            dataset_id="dataset-123",
            data_id="data-456",
        )
        assert "caption" not in variables

    def test_caption_none_is_sent_as_null(self):
        variables = update_params(
            dataset_id="dataset-123",
            data_id="data-456",
            caption=None,
        )
        assert "caption" in variables
        assert variables["caption"] is None

    def test_caption_string_is_sent_exactly(self):
        caption = "a synthetic caption for a test image"
        variables = update_params(
            dataset_id="dataset-123",
            data_id="data-456",
            caption=caption,
        )
        assert variables["caption"] == caption


class TestUpdateParamsExpectedCaption:
    """update_params must follow Undefined/None/value semantics for expected_caption."""

    def test_expected_caption_undefined_is_omitted(self):
        variables = update_params(
            dataset_id="dataset-123",
            data_id="data-456",
        )
        assert "expectedCaption" not in variables

    def test_expected_caption_none_is_sent_as_null(self):
        variables = update_params(
            dataset_id="dataset-123",
            data_id="data-456",
            expected_caption=None,
        )
        assert "expectedCaption" in variables
        assert variables["expectedCaption"] is None

    def test_expected_caption_empty_string_is_preserved(self):
        variables = update_params(
            dataset_id="dataset-123",
            data_id="data-456",
            expected_caption="",
        )
        assert variables["expectedCaption"] == ""

    def test_expected_caption_string_is_sent_exactly(self):
        expected_caption = "a synthetic expected caption"
        variables = update_params(
            dataset_id="dataset-123",
            data_id="data-456",
            expected_caption=expected_caption,
        )
        assert variables["expectedCaption"] == expected_caption


class TestUpdateQueryCaption:
    """The updateData GraphQL document must carry the caption variable."""

    def test_caption_source_is_sent_with_the_v2_slot_name(self):
        variables = update_params(
            dataset_id="ds-1",
            data_id="d-1",
            caption="generated",
            caption_source="VLM_GENERATED",
        )
        assert variables["captionSource"] == "VLM_GENERATED"

    def test_caption_source_undefined_is_omitted(self):
        variables = update_params(
            dataset_id="ds-1",
            data_id="d-1",
            caption="generated",
        )
        assert "captionSource" not in variables

    def test_update_queries_declare_caption_source_variable(self):
        from spb_onprem.data.queries import Queries
        assert "$captionSource: CaptionSource" in Queries.UPDATE["query"]
        assert (
            "$captionSource: CaptionSource"
            in Queries.UPDATE_WITH_EXPECTED_CAPTION["query"]
        )

    def test_update_query_declares_caption_variable(self):
        query = Queries.UPDATE["query"]
        assert "$caption: String" in query
        assert "caption: $caption" in query

    def test_data_schema_selects_caption_field(self):
        assert "caption" in Schemas.DATA.split()


class TestUpdateQueryExpectedCaption:
    """expectedCaption only appears in the guarded query variant."""

    def test_unguarded_update_query_omits_expected_caption(self):
        query = Queries.UPDATE["query"]
        assert "$expectedCaption" not in query
        assert "expectedCaption" not in query

    def test_guarded_update_query_declares_expected_caption_variable(self):
        query = Queries.UPDATE_WITH_EXPECTED_CAPTION["query"]
        assert "$expectedCaption: String" in query
        assert "expectedCaption: $expectedCaption" in query

    def test_guarded_update_query_keeps_caption_argument(self):
        query = Queries.UPDATE_WITH_EXPECTED_CAPTION["query"]
        assert "$caption: String" in query
        assert "caption: $caption" in query

    def test_guarded_update_query_shares_name_and_params(self):
        assert Queries.UPDATE_WITH_EXPECTED_CAPTION["name"] == "updateData"
        assert Queries.UPDATE_WITH_EXPECTED_CAPTION["variables"] is update_params


class TestDataEntityCaption:
    """The Data entity must map the caption field from a response."""

    def test_data_maps_caption(self):
        data = Data.model_validate({
            "id": "data-456",
            "datasetId": "dataset-123",
            "caption": "a synthetic caption",
        })
        assert data.caption == "a synthetic caption"

    def test_data_caption_defaults_to_none(self):
        data = Data.model_validate({
            "id": "data-456",
            "datasetId": "dataset-123",
        })
        assert data.caption is None


class TestDataServiceUpdateDataCaption:
    """DataService.update_data must pass caption through to the request."""

    def setup_method(self):
        self.data_service = DataService()
        self.data_service.request_gql = Mock()

    def test_update_data_sends_caption(self):
        self.data_service.request_gql.return_value = {
            "id": "data-456",
            "datasetId": "dataset-123",
            "caption": "a synthetic caption",
        }

        result = self.data_service.update_data(
            dataset_id="dataset-123",
            data_id="data-456",
            caption="a synthetic caption",
        )

        _, kwargs = self.data_service.request_gql.call_args
        variables = kwargs.get("variables") or self.data_service.request_gql.call_args[0][1]
        assert variables["caption"] == "a synthetic caption"
        assert result.caption == "a synthetic caption"

    def test_update_data_caption_none_sends_null(self):
        self.data_service.request_gql.return_value = {
            "id": "data-456",
            "datasetId": "dataset-123",
        }

        self.data_service.update_data(
            dataset_id="dataset-123",
            data_id="data-456",
            caption=None,
        )

        _, kwargs = self.data_service.request_gql.call_args
        variables = kwargs.get("variables") or self.data_service.request_gql.call_args[0][1]
        assert "caption" in variables
        assert variables["caption"] is None

    def test_update_data_without_caption_stays_compatible(self):
        """Old call sites that never pass caption must be unaffected."""
        self.data_service.request_gql.return_value = {
            "id": "data-456",
            "datasetId": "dataset-123",
            "key": "new-key",
        }

        result = self.data_service.update_data(
            dataset_id="dataset-123",
            data_id="data-456",
            key="new-key",
        )

        args, kwargs = self.data_service.request_gql.call_args
        variables = kwargs.get("variables") or self.data_service.request_gql.call_args[0][1]
        assert variables == {
            "dataset_id": "dataset-123",
            "data_id": "data-456",
            "key": "new-key",
        }
        assert args[0] is Queries.UPDATE
        assert result.key == "new-key"


class TestDataServiceUpdateDataExpectedCaption:
    """DataService.update_data must route expected_caption through the guarded query."""

    def setup_method(self):
        self.data_service = DataService()
        self.data_service.request_gql = Mock()

    def _sent(self):
        args, kwargs = self.data_service.request_gql.call_args
        variables = kwargs.get("variables") or args[1]
        return args[0], variables

    def test_expected_caption_undefined_uses_unguarded_query_and_omits_variable(self):
        self.data_service.request_gql.return_value = {
            "id": "data-456",
            "datasetId": "dataset-123",
        }

        self.data_service.update_data(
            dataset_id="dataset-123",
            data_id="data-456",
            caption="a synthetic caption",
        )

        query, variables = self._sent()
        assert query is Queries.UPDATE
        assert variables == {
            "dataset_id": "dataset-123",
            "data_id": "data-456",
            "caption": "a synthetic caption",
        }

    def test_expected_caption_none_uses_guarded_query_and_sends_null(self):
        self.data_service.request_gql.return_value = {
            "id": "data-456",
            "datasetId": "dataset-123",
        }

        self.data_service.update_data(
            dataset_id="dataset-123",
            data_id="data-456",
            expected_caption=None,
        )

        query, variables = self._sent()
        assert query is Queries.UPDATE_WITH_EXPECTED_CAPTION
        assert variables == {
            "dataset_id": "dataset-123",
            "data_id": "data-456",
            "expectedCaption": None,
        }

    def test_expected_caption_empty_string_uses_guarded_query(self):
        self.data_service.request_gql.return_value = {
            "id": "data-456",
            "datasetId": "dataset-123",
        }

        self.data_service.update_data(
            dataset_id="dataset-123",
            data_id="data-456",
            caption="a synthetic caption",
            expected_caption="",
        )

        query, variables = self._sent()
        assert query is Queries.UPDATE_WITH_EXPECTED_CAPTION
        assert variables == {
            "dataset_id": "dataset-123",
            "data_id": "data-456",
            "caption": "a synthetic caption",
            "expectedCaption": "",
        }

    def test_expected_caption_string_uses_guarded_query_and_sends_value(self):
        self.data_service.request_gql.return_value = {
            "id": "data-456",
            "datasetId": "dataset-123",
            "caption": "a synthetic caption",
        }

        result = self.data_service.update_data(
            dataset_id="dataset-123",
            data_id="data-456",
            caption="a synthetic caption",
            expected_caption="a synthetic expected caption",
        )

        query, variables = self._sent()
        assert query is Queries.UPDATE_WITH_EXPECTED_CAPTION
        assert variables == {
            "dataset_id": "dataset-123",
            "data_id": "data-456",
            "caption": "a synthetic caption",
            "expectedCaption": "a synthetic expected caption",
        }
        assert result.caption == "a synthetic caption"
