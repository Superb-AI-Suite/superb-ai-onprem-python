"""Dataset caption settings (3.0.0, MOD2-106).

Read with ``DatasetService.get_dataset_caption_settings`` (query
``datasetCaptionSettings``). ``Dataset`` has no ``caption_settings`` any more.
"""
import typing
from unittest.mock import Mock

import pytest

import spb_onprem
from spb_onprem.datasets.entities import CaptionTarget, Dataset, DatasetCaptionSettings
from spb_onprem.datasets.params import dataset_caption_settings_params
from spb_onprem.datasets.queries import Queries, Schemas
from spb_onprem.datasets.service import DatasetService
from spb_onprem.exceptions import BadParameterError

RESPONSE = {
    "datasetId": "dataset-1",
    "dataDefinition": "Street scenes from fixed traffic cameras",
    "captionTargets": [
        {"target": "vehicle type", "terms": ["truck", "bus"]},
        {"target": "time of day", "terms": []},
    ],
    "excludedTerms": ["road surface"],
}


class TestQuery:
    def test_document_calls_dataset_caption_settings(self):
        query = Queries.DATASET_CAPTION_SETTINGS
        assert query["name"] == "datasetCaptionSettings"
        assert query["variables"] is dataset_caption_settings_params
        text = query["query"]
        assert "$datasetId: ID!" in text
        assert "datasetCaptionSettings(datasetId: $datasetId)" in text
        for field in ("datasetId", "dataDefinition", "captionTargets", "target", "terms", "excludedTerms"):
            assert field in text.split()

    def test_params(self):
        assert dataset_caption_settings_params("dataset-1") == {"datasetId": "dataset-1"}

    @pytest.mark.parametrize("dataset_id", [None, ""])
    def test_dataset_id_is_required(self, dataset_id):
        with pytest.raises(BadParameterError):
            dataset_caption_settings_params(dataset_id)


class TestService:
    def setup_method(self):
        self.service = DatasetService()
        self.service.request_gql = Mock()

    def test_reads_and_parses_the_settings(self):
        self.service.request_gql.return_value = RESPONSE

        settings = self.service.get_dataset_caption_settings("dataset-1")

        args, _ = self.service.request_gql.call_args
        assert args[0] is Queries.DATASET_CAPTION_SETTINGS
        assert args[1] == {"datasetId": "dataset-1"}
        assert isinstance(settings, DatasetCaptionSettings)
        assert settings.dataset_id == "dataset-1"
        assert settings.data_definition == "Street scenes from fixed traffic cameras"
        assert settings.caption_targets == [
            CaptionTarget(target="vehicle type", terms=["truck", "bus"]),
            CaptionTarget(target="time of day", terms=[]),
        ]
        assert settings.caption_targets[0].terms == ["truck", "bus"]
        assert settings.excluded_terms == ["road surface"]

    def test_none_when_the_dataset_has_no_settings(self):
        self.service.request_gql.return_value = None
        assert self.service.get_dataset_caption_settings("dataset-1") is None

    def test_null_fields_stay_none(self):
        self.service.request_gql.return_value = {
            "datasetId": "dataset-1", "dataDefinition": None, "captionTargets": None, "excludedTerms": None,
        }
        settings = self.service.get_dataset_caption_settings("dataset-1")
        assert settings.data_definition is None
        assert settings.caption_targets is None
        assert settings.excluded_terms is None

    def test_missing_dataset_id_is_refused_before_the_request(self):
        with pytest.raises(BadParameterError):
            self.service.get_dataset_caption_settings("")
        self.service.request_gql.assert_not_called()

    def test_return_type_hint_resolves_to_the_entity(self):
        """Callers check the fields through the return annotation (typing.get_type_hints)."""
        hint = typing.get_type_hints(DatasetService.get_dataset_caption_settings)["return"]
        assert hint == typing.Optional[DatasetCaptionSettings]
        assert {"data_definition", "caption_targets", "excluded_terms"} <= set(
            DatasetCaptionSettings.model_fields
        )


class TestDatasetHasNoCaptionSettings:
    def test_entity_field_is_gone(self):
        assert "caption_settings" not in Dataset.model_fields

    @pytest.mark.parametrize("key", ["DATASET", "DATASETS", "CREATE_DATASET", "UPDATE_DATASET"])
    def test_dataset_documents_do_not_select_it(self, key):
        assert "captionSettings" not in Queries.__dict__[key]["query"]
        assert "captionSettings" not in Schemas.DATASET


def test_exported_at_the_top():
    assert spb_onprem.DatasetCaptionSettings is DatasetCaptionSettings
    assert spb_onprem.CaptionTarget is CaptionTarget
    assert "DatasetCaptionSettings" in spb_onprem.__all__
