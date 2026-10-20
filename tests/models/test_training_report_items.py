"""ModelService training report items (moved from the removed TrainingReportService, 99dc576).

The real-server flow is in tests/models/test_workflow.py (RUN_MODEL_WORKFLOW_TESTS=1).
"""
from unittest.mock import Mock

import pytest

from spb_onprem.base_types import Undefined
from spb_onprem.exceptions import BadParameterError
from spb_onprem.models.entities import Model
from spb_onprem.models.queries import Queries
from spb_onprem.models.service import ModelService
from spb_onprem.reports.entities.analytics_report_item import AnalyticsReportItemType


def _model(items):
    return {"id": "m1", "datasetId": "d1", "name": "model-name", "trainingReport": items}


def _item(**fields):
    return {"id": "tr1", "name": "report", "type": "METRICS", "contentId": "c1", "description": None, **fields}


@pytest.fixture
def service():
    service = ModelService()
    service.request_gql = Mock()
    return service


class TestCreate:
    @pytest.mark.parametrize("missing", ["dataset_id", "model_id", "name", "type"])
    def test_required(self, service, missing):
        kwargs = {"dataset_id": "d1", "model_id": "m1", "name": "report", "type": AnalyticsReportItemType.METRICS}
        kwargs[missing] = None
        with pytest.raises(BadParameterError, match=f"{missing} is required"):
            service.create_training_report_item(**kwargs)
        service.request_gql.assert_not_called()

    def test_success(self, service):
        service.request_gql.return_value = _model([_item()])

        result = service.create_training_report_item(
            dataset_id="d1", model_id="m1", name="report", type=AnalyticsReportItemType.METRICS, content_id="c1",
        )

        assert isinstance(result, Model) and result.id == "m1"
        assert [item.id for item in result.training_report] == ["tr1"]
        service.request_gql.assert_called_once_with(
            Queries.CREATE_TRAINING_REPORT,
            {"dataset_id": "d1", "model_id": "m1", "name": "report", "type": "METRICS",
             "content_id": "c1", "description": None},
        )


class TestUpdate:
    @pytest.mark.parametrize("missing", ["dataset_id", "model_id", "training_report_id"])
    def test_required(self, service, missing):
        kwargs = {"dataset_id": "d1", "model_id": "m1", "training_report_id": "tr1"}
        kwargs[missing] = None
        with pytest.raises(BadParameterError, match=f"{missing} is required"):
            service.update_training_report_item(**kwargs, description="x")
        service.request_gql.assert_not_called()

    def test_only_given_fields_are_sent(self, service):
        service.request_gql.return_value = _model([_item(description="updated")])

        result = service.update_training_report_item(
            dataset_id="d1", model_id="m1", training_report_id="tr1", description="updated", name=Undefined,
        )

        assert result.training_report[0].description == "updated"
        service.request_gql.assert_called_once_with(
            Queries.UPDATE_TRAINING_REPORT,
            {"dataset_id": "d1", "model_id": "m1", "training_report_id": "tr1", "description": "updated"},
        )


class TestDelete:
    @pytest.mark.parametrize("missing", ["dataset_id", "model_id", "training_report_id"])
    def test_required(self, service, missing):
        kwargs = {"dataset_id": "d1", "model_id": "m1", "training_report_id": "tr1"}
        kwargs[missing] = None
        with pytest.raises(BadParameterError, match=f"{missing} is required"):
            service.delete_training_report_item(**kwargs)
        service.request_gql.assert_not_called()

    def test_success(self, service):
        service.request_gql.return_value = _model([])

        result = service.delete_training_report_item(dataset_id="d1", model_id="m1", training_report_id="tr1")

        assert isinstance(result, Model) and result.training_report == []
        service.request_gql.assert_called_once_with(
            Queries.DELETE_TRAINING_REPORT,
            {"dataset_id": "d1", "model_id": "m1", "training_report_id": "tr1"},
        )
