import pytest
from unittest.mock import Mock

from spb_onprem.activities.entities import ActivityHistory, ActivityStatus
from spb_onprem.activities.queries import Queries as ActivityQueries
from spb_onprem.datasets.service import DatasetService
from spb_onprem.datasets.queries import Queries
from spb_onprem.exceptions import BadParameterError


def _history(status="PENDING"):
    return {"id": "history-1", "jobId": "job-1", "datasetId": "dataset-123", "status": status}


class TestDatasetService:
    """Test cases for DatasetService delete_dataset method."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.dataset_service = DatasetService()
        self.dataset_service.request_gql = Mock()

    def test_delete_dataset_starts_activity(self):
        """delete_dataset starts a DELETE_DATASET activity (2.0.0)."""
        dataset_id = "dataset-123"
        self.dataset_service.request_gql.return_value = _history()

        result = self.dataset_service.delete_dataset(dataset_id)

        assert isinstance(result, ActivityHistory)
        assert result.id == "history-1"
        assert result.status == ActivityStatus.PENDING
        assert result  # truthy, so `if delete_dataset(...)` keeps working
        self.dataset_service.request_gql.assert_called_once_with(
            ActivityQueries.START_ACTIVITY,
            {
                "datasetId": dataset_id,
                "jobType": "DELETE_DATASET",
                "parameters": {"dataset_id": dataset_id},
            },
        )

    def test_delete_dataset_awaiting_approval(self):
        """A non-admin request comes back as AWAITING_APPROVAL."""
        self.dataset_service.request_gql.return_value = _history("AWAITING_APPROVAL")

        result = self.dataset_service.delete_dataset("dataset-123")

        assert result.status == ActivityStatus.AWAITING_APPROVAL

    def test_delete_dataset_does_not_call_delete_mutation(self):
        """The direct deleteDataset mutation is no longer used."""
        self.dataset_service.request_gql.return_value = _history()

        self.dataset_service.delete_dataset("dataset-123")

        query = self.dataset_service.request_gql.call_args[0][0]
        assert query["name"] == "startJob"
        assert query is not Queries.DELETE_DATASET

    def test_delete_dataset_missing_dataset_id(self):
        """Test delete dataset with missing dataset_id."""
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.dataset_service.delete_dataset(dataset_id=None)
        self.dataset_service.request_gql.assert_not_called()

    def test_delete_dataset_empty_string_id(self):
        """An empty dataset_id is refused before any request."""
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.dataset_service.delete_dataset("")
        self.dataset_service.request_gql.assert_not_called()

    def test_delete_dataset_variables_function(self):
        """The old mutation definition is kept and still builds its variables."""
        dataset_id = "test-variables-dataset"

        variables = Queries.DELETE_DATASET["variables"](dataset_id)

        assert variables == {"dataset_id": dataset_id}

    def test_delete_dataset_with_special_characters(self):
        """Test dataset deletion with special characters in ID."""
        dataset_id = "dataset-with-special-chars_123@test"
        self.dataset_service.request_gql.return_value = _history()

        self.dataset_service.delete_dataset(dataset_id)

        variables = self.dataset_service.request_gql.call_args[0][1]
        assert variables["datasetId"] == dataset_id
        assert variables["parameters"] == {"dataset_id": dataset_id}


class TestUpdateDataset:
    def test_sends_the_declared_id_variable(self):
        """The mutation declares $updateDatasetId; sending `id` gave HTTP 400 (variable not provided)."""
        service = DatasetService()
        service.request_gql = Mock(return_value={"id": "dataset-1", "name": "same"})

        service.update_dataset(dataset_id="dataset-1", name="same")

        query, variables = service.request_gql.call_args[0]
        assert query is Queries.UPDATE_DATASET
        assert "$updateDatasetId: ID!" in query["query"]
        assert variables == {"updateDatasetId": "dataset-1", "name": "same"}
