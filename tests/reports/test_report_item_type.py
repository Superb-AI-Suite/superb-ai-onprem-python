"""AnalyticsReportItemType: the 12 platform values, and unknown values from a newer platform.

The platform added MARKDOWN and MEDIA_COMPARISON. Before this fix a diagnosis that
held a MARKDOWN item failed Diagnosis.model_validate, so update_diagnosis raised
even though the server call succeeded.
"""
from unittest.mock import Mock

import pytest

from spb_onprem.diagnoses.entities import Diagnosis, DiagnosisReportItem
from spb_onprem.diagnoses.enums import DiagnosisStatus
from spb_onprem.diagnoses.params.create_diagnosis_report_item import create_diagnosis_report_item_params
from spb_onprem.diagnoses.params.update_diagnosis_report_item import update_diagnosis_report_item_params
from spb_onprem.diagnoses.queries import Queries as DiagnosisQueries
from spb_onprem.diagnoses.service import DiagnosisService
from spb_onprem.models.entities import Model
from spb_onprem.models.params.create_training_report_item import create_training_report_item_params
from spb_onprem.models.params.update_training_report_item import update_training_report_item_params
from spb_onprem.reports.entities import AnalyticsReport, AnalyticsReportItem
from spb_onprem.reports.entities.analytics_report_item import AnalyticsReportItemType
from spb_onprem.reports.params.create_analytics_report_item import create_analytics_report_item_params

OLD_TYPES = [
    "PIE", "HORIZONTAL_BAR", "VERTICAL_BAR", "HEATMAP", "TABLE",
    "LINE_CHART", "SCATTER_PLOT", "HISTOGRAM", "METRICS", "CONFUSION_MATRIX",
]
NEW_TYPES = ["MARKDOWN", "MEDIA_COMPARISON"]
ALL_TYPES = OLD_TYPES + NEW_TYPES


def _diagnosis(*types):
    return {
        "id": "diag1",
        "datasetId": "d1",
        "name": "diagnosis",
        "status": "COMPLETED",
        "diagnosisReportItems": [
            {"id": f"item{i}", "diagnosisId": "diag1", "name": f"item {i}", "type": t, "contentId": None}
            for i, t in enumerate(types)
        ],
    }


class TestEnum:
    def test_has_exactly_the_platform_values(self):
        assert sorted(member.value for member in AnalyticsReportItemType) == sorted(ALL_TYPES)

    def test_matches_platform_schema_fixture(self):
        # tests/fixtures/zenith-schema-public.gql is the platform's public schema.
        from pathlib import Path

        schema = (Path(__file__).parent.parent / "fixtures" / "zenith-schema-public.gql").read_text()
        body = schema.split("enum AnalyticsReportItemType {", 1)[1].split("}", 1)[0]
        assert sorted(body.split()) == sorted(ALL_TYPES)

    @pytest.mark.parametrize("value", ALL_TYPES)
    def test_every_value_parses_to_the_enum(self, value):
        item = DiagnosisReportItem.model_validate({"id": "i1", "type": value})
        assert item.type is AnalyticsReportItemType(value)
        assert item.type.value == value

        item = AnalyticsReportItem.model_validate({"id": "i1", "type": value})
        assert item.type is AnalyticsReportItemType(value)


class TestUnknownTypeFromNewerPlatform:
    def test_diagnosis_with_unknown_type_validates(self):
        diagnosis = Diagnosis.model_validate(_diagnosis("METRICS", "MARKDOWN", "FUTURE_CHART", None))

        types = [item.type for item in diagnosis.diagnosis_report_items]
        assert types[0] is AnalyticsReportItemType.METRICS
        assert types[1] is AnalyticsReportItemType.MARKDOWN
        assert types[2] == "FUTURE_CHART" and not isinstance(types[2], AnalyticsReportItemType)
        assert types[3] is None

    def test_analytics_report_with_unknown_type_validates(self):
        report = AnalyticsReport.model_validate(
            {"id": "r1", "items": [{"id": "i1", "type": "PIE"}, {"id": "i2", "type": "FUTURE_CHART"}]}
        )
        assert report.items[0].type is AnalyticsReportItemType.PIE
        assert report.items[1].type == "FUTURE_CHART"

    def test_unknown_type_round_trips_through_dump(self):
        item = DiagnosisReportItem.model_validate({"id": "i1", "type": "FUTURE_CHART"})
        assert item.model_dump(mode="json", by_alias=True)["type"] == "FUTURE_CHART"

    def test_update_diagnosis_returns_diagnosis_with_new_and_unknown_types(self):
        # The prod failure: update_diagnosis(status=COMPLETED) on a diagnosis with a MARKDOWN item.
        service = DiagnosisService()
        service.request_gql = Mock(return_value=_diagnosis("CONFUSION_MATRIX", "MARKDOWN", "MEDIA_COMPARISON", "FUTURE_CHART"))

        result = service.update_diagnosis(dataset_id="d1", diagnosis_id="diag1", status=DiagnosisStatus.COMPLETED)

        assert isinstance(result, Diagnosis)
        assert [item.type for item in result.diagnosis_report_items] == [
            AnalyticsReportItemType.CONFUSION_MATRIX,
            AnalyticsReportItemType.MARKDOWN,
            AnalyticsReportItemType.MEDIA_COMPARISON,
            "FUTURE_CHART",
        ]

    def test_model_validate_rejects_non_string_type(self):
        # Leniency is for unknown strings only; a wrong JSON type is still an error.
        with pytest.raises(Exception):
            DiagnosisReportItem.model_validate({"id": "i1", "type": 3})


class TestParamsTakeEnumOrString:
    @pytest.mark.parametrize("value", [AnalyticsReportItemType.MARKDOWN, "MARKDOWN"])
    def test_create_diagnosis_report_item(self, value):
        params = create_diagnosis_report_item_params(
            dataset_id="d1", diagnosis_id="diag1", name="summary", type=value,
        )
        assert params["type"] == "MARKDOWN" and type(params["type"]) is str

    @pytest.mark.parametrize("value", [AnalyticsReportItemType.MEDIA_COMPARISON, "MEDIA_COMPARISON"])
    def test_update_diagnosis_report_item(self, value):
        params = update_diagnosis_report_item_params(
            dataset_id="d1", diagnosis_id="diag1", diagnosis_report_item_id="item1", type=value,
        )
        assert params["type"] == "MEDIA_COMPARISON" and type(params["type"]) is str

    def test_update_diagnosis_report_item_type_none_and_undefined_unchanged(self):
        base = {"dataset_id": "d1", "diagnosis_id": "diag1", "diagnosis_report_item_id": "item1"}
        assert update_diagnosis_report_item_params(**base, type=None)["type"] is None
        assert "type" not in update_diagnosis_report_item_params(**base)

    @pytest.mark.parametrize("value", [AnalyticsReportItemType.MARKDOWN, "MARKDOWN"])
    def test_create_and_update_training_report_item(self, value):
        created = create_training_report_item_params(dataset_id="d1", model_id="m1", name="r", type=value)
        updated = update_training_report_item_params(
            dataset_id="d1", model_id="m1", training_report_id="tr1", type=value,
        )
        assert created["type"] == updated["type"] == "MARKDOWN"
        assert type(created["type"]) is str and type(updated["type"]) is str

    @pytest.mark.parametrize("value", [AnalyticsReportItemType.MARKDOWN, "MARKDOWN"])
    def test_create_analytics_report_item(self, value):
        params = create_analytics_report_item_params(dataset_id="d1", report_id="r1", type=value)
        assert params["type"] == "MARKDOWN" and type(params["type"]) is str

    @pytest.mark.parametrize("value", OLD_TYPES)
    def test_existing_enum_values_send_the_same_string(self, value):
        params = create_diagnosis_report_item_params(
            dataset_id="d1", diagnosis_id="diag1", name="n", type=AnalyticsReportItemType(value),
        )
        assert params["type"] == value

    def test_service_sends_string_type(self):
        service = DiagnosisService()
        service.request_gql = Mock(return_value=_diagnosis("MARKDOWN"))

        result = service.create_diagnosis_report_item(
            dataset_id="d1", diagnosis_id="diag1", name="summary", type="MARKDOWN", content_id="c1",
        )

        assert result.diagnosis_report_items[0].type is AnalyticsReportItemType.MARKDOWN
        service.request_gql.assert_called_once_with(
            DiagnosisQueries.CREATE_REPORT_ITEM,
            {"dataset_id": "d1", "diagnosis_id": "diag1", "name": "summary", "type": "MARKDOWN",
             "content_id": "c1", "description": None, "discriminator_value": None},
        )


def test_training_report_item_entity_has_no_type_field():
    # Model.training_report items carry no type, so they were never affected.
    model = Model.model_validate({"id": "m1", "trainingReport": [{"id": "tr1", "type": "FUTURE_CHART"}]})
    assert model.training_report[0].id == "tr1"
