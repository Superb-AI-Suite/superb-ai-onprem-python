"""Caption writes (3.0.0, MOD2-106).

The caption has its own mutation ``updateDataCaption`` and SDK function
``DataService.update_data_caption``. ``update_data`` takes no caption.
"""
import inspect
from unittest.mock import Mock

import pytest

from spb_onprem.data.entities import Data
from spb_onprem.data.params import update_data_caption_params, update_params
from spb_onprem.data.queries import Queries, Schemas
from spb_onprem.data.service import DataService
from spb_onprem.exceptions import BadParameterError


class TestUpdateDataTakesNoCaption:
    """The caption arguments of update_data are gone (no compatibility arguments)."""

    @pytest.mark.parametrize("name", ["caption", "expected_caption", "caption_source"])
    def test_service_signature_has_no_caption_argument(self, name):
        assert name not in inspect.signature(DataService.update_data).parameters

    @pytest.mark.parametrize("name", ["caption", "expected_caption", "caption_source"])
    def test_params_signature_has_no_caption_argument(self, name):
        assert name not in inspect.signature(update_params).parameters

    def test_update_data_rejects_caption_keyword(self):
        service = DataService()
        service.request_gql = Mock()
        with pytest.raises(TypeError):
            service.update_data(dataset_id="dataset-1", data_id="data-1", caption="x")
        service.request_gql.assert_not_called()

    def test_update_query_does_not_mention_caption(self):
        query = Queries.UPDATE["query"]
        for word in ("$caption", "captionSource", "expectedCaption"):
            assert word not in query

    def test_guarded_update_query_is_gone(self):
        assert not hasattr(Queries, "UPDATE_WITH_EXPECTED_CAPTION")

    def test_update_data_without_caption_sends_only_given_fields(self):
        service = DataService()
        service.request_gql = Mock(return_value={
            "id": "data-1", "datasetId": "dataset-1", "key": "new-key",
        })

        result = service.update_data(dataset_id="dataset-1", data_id="data-1", key="new-key")

        args, kwargs = service.request_gql.call_args
        assert args[0] is Queries.UPDATE
        assert kwargs["variables"] == {
            "dataset_id": "dataset-1",
            "data_id": "data-1",
            "key": "new-key",
        }
        assert result.key == "new-key"


class TestUpdateDataCaptionParams:
    def test_caption_text_is_sent_exactly(self):
        caption = "  a synthetic caption with spaces  "
        assert update_data_caption_params("dataset-1", "data-1", caption) == {
            "dataset_id": "dataset-1",
            "data_id": "data-1",
            "caption": caption,
        }

    def test_none_is_sent_as_null(self):
        variables = update_data_caption_params("dataset-1", "data-1", None)
        assert "caption" in variables
        assert variables["caption"] is None

    def test_empty_string_is_sent_as_is(self):
        """The server clears the caption for an empty string as for null (C46-4)."""
        assert update_data_caption_params("dataset-1", "data-1", "")["caption"] == ""

    @pytest.mark.parametrize("dataset_id,data_id", [(None, "data-1"), ("", "data-1"),
                                                    ("dataset-1", None), ("dataset-1", "")])
    def test_ids_are_required(self, dataset_id, data_id):
        with pytest.raises(BadParameterError):
            update_data_caption_params(dataset_id, data_id, "x")

    def test_caption_must_be_text(self):
        with pytest.raises(BadParameterError):
            update_data_caption_params("dataset-1", "data-1", 1)


class TestUpdateCaptionQuery:
    def test_document_calls_update_data_caption(self):
        query = Queries.UPDATE_CAPTION
        assert query["name"] == "updateDataCaption"
        assert query["variables"] is update_data_caption_params
        text = query["query"]
        assert "mutation updateDataCaption(" in text
        assert "$dataset_id: ID!" in text
        assert "$data_id: ID!" in text
        assert "$caption: String" in text
        assert "updateDataCaption(" in text
        assert "datasetId: $dataset_id" in text
        assert "id: $data_id" in text
        assert "caption: $caption" in text

    def test_document_selects_the_data_with_its_caption(self):
        assert Schemas.DATA in Queries.UPDATE_CAPTION["query"]
        assert "caption" in Schemas.DATA.split()


class TestDataServiceUpdateDataCaption:
    def setup_method(self):
        self.service = DataService()
        self.service.request_gql = Mock()

    def test_sends_the_caption_and_parses_the_data(self):
        self.service.request_gql.return_value = {
            "id": "data-1",
            "datasetId": "dataset-1",
            "key": "image-1.jpg",
            "caption": "a red truck parked next to a bus",
        }

        result = self.service.update_data_caption(
            dataset_id="dataset-1", data_id="data-1", caption="a red truck parked next to a bus",
        )

        args, kwargs = self.service.request_gql.call_args
        assert args[0] is Queries.UPDATE_CAPTION
        assert kwargs["variables"] == {
            "dataset_id": "dataset-1",
            "data_id": "data-1",
            "caption": "a red truck parked next to a bus",
        }
        assert isinstance(result, Data)
        assert result.id == "data-1"
        assert result.dataset_id == "dataset-1"
        assert result.caption == "a red truck parked next to a bus"

    def test_none_clears_the_caption(self):
        self.service.request_gql.return_value = {"id": "data-1", "datasetId": "dataset-1", "caption": None}

        result = self.service.update_data_caption("dataset-1", "data-1", None)

        _, kwargs = self.service.request_gql.call_args
        assert kwargs["variables"] == {"dataset_id": "dataset-1", "data_id": "data-1", "caption": None}
        assert result.caption is None

    def test_caption_is_a_required_argument(self):
        parameter = inspect.signature(DataService.update_data_caption).parameters["caption"]
        assert parameter.default is inspect.Parameter.empty

    def test_missing_id_is_refused_before_the_request(self):
        with pytest.raises(BadParameterError):
            self.service.update_data_caption("dataset-1", "", "x")
        self.service.request_gql.assert_not_called()


class TestDataEntityCaption:
    """Reading the caption stays: Data.caption maps the caption field."""

    def test_data_maps_caption(self):
        data = Data.model_validate({"id": "data-1", "datasetId": "dataset-1", "caption": "a synthetic caption"})
        assert data.caption == "a synthetic caption"

    def test_data_caption_defaults_to_none(self):
        data = Data.model_validate({"id": "data-1", "datasetId": "dataset-1"})
        assert data.caption is None
