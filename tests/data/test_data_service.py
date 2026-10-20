import pytest
from unittest.mock import Mock

from spb_onprem.activities.entities import ActivityHistory
from spb_onprem.activities.queries import Queries as ActivityQueries
from spb_onprem.data.params import DataFilterOptions, DataListFilter
from spb_onprem.data.service import DataService
from spb_onprem.data.queries import Queries
from spb_onprem.exceptions import BadDeletionTargetError, BadParameterError


def _history():
    return {"id": "history-1", "jobId": "job-1", "datasetId": "dataset-123", "status": "PENDING"}


class TestDataService:
    """Test cases for DataService."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.data_service = DataService()
        self.data_service.request_gql = Mock(return_value=_history())

    def _sent(self):
        query, variables = self.data_service.request_gql.call_args[0]
        assert query is ActivityQueries.START_ACTIVITY
        return variables

    def test_delete_data_query_structure(self):
        """The old deleteData mutation definition is kept unchanged."""
        dataset_id = "dataset-123"
        data_id = "data-456"

        query = Queries.DELETE["query"]
        variables = Queries.DELETE["variables"](dataset_id=dataset_id, data_id=data_id)

        assert "mutation (" in query
        assert "$dataset_id: ID!" in query
        assert "$data_id: ID!," in query  # GraphQL allows trailing commas
        assert "deleteData(" in query
        assert "datasetId: $dataset_id" in query
        assert "id: $data_id," in query  # GraphQL allows trailing commas
        assert variables == {
            "dataset_id": dataset_id,
            "data_id": data_id
        }

    def test_delete_data_one_id_starts_activity(self):
        """delete_data starts a DELETE_DATA activity for one data (2.0.0)."""
        result = self.data_service.delete_data(dataset_id="dataset-123", data_id="data-456")

        assert isinstance(result, ActivityHistory)
        assert result.id == "history-1"
        assert result
        self.data_service.request_gql.assert_called_once()
        assert self._sent() == {
            "datasetId": "dataset-123",
            "jobType": "DELETE_DATA",
            "parameters": {
                "dataset_id": "dataset-123",
                "data_filter": {"must": {"idIn": ["data-456"]}},
            },
        }

    def test_delete_data_positional_data_id(self):
        """The old positional call still works."""
        self.data_service.delete_data("dataset-123", "data-456")

        assert self._sent()["parameters"]["data_filter"] == {"must": {"idIn": ["data-456"]}}

    def test_delete_data_many_ids_one_activity(self):
        """Several ids go in one activity."""
        self.data_service.delete_data(dataset_id="dataset-123", data_ids=["a", "b", "c"])

        self.data_service.request_gql.assert_called_once()
        assert self._sent()["parameters"]["data_filter"] == {"must": {"idIn": ["a", "b", "c"]}}

    def test_delete_data_with_model_filter(self):
        """A DataListFilter is sent with its camelCase aliases."""
        data_filter = DataListFilter(
            must_filter=DataFilterOptions(key_contains="sample_", type_in=["SUPERB_IMAGE"])
        )

        self.data_service.delete_data(dataset_id="dataset-123", data_filter=data_filter)

        assert self._sent()["parameters"]["data_filter"] == {
            "must": {"keyContains": "sample_", "typeIn": ["SUPERB_IMAGE"]}
        }

    def test_delete_data_with_dict_filter_is_sent_as_is(self):
        """A dict filter is sent unchanged (the server rejects unknown fields)."""
        data_filter = {"must": {"keyContains": "sample_"}, "not": {"idIn": ["keep"]}}

        self.data_service.delete_data(dataset_id="dataset-123", data_filter=data_filter)

        sent = self._sent()["parameters"]["data_filter"]
        assert sent == data_filter
        assert sent is not data_filter

    @pytest.mark.parametrize(
        "kwargs",
        [
            {},
            {"data_id": "a", "data_ids": ["b"]},
            {"data_id": "a", "data_filter": {"must": {"idIn": ["b"]}}},
            {"data_ids": ["a"], "data_filter": {"must": {"idIn": ["b"]}}},
        ],
    )
    def test_delete_data_needs_exactly_one_target(self, kwargs):
        """Exactly one of data_id, data_ids and data_filter is accepted."""
        with pytest.raises(BadDeletionTargetError, match="exactly one"):
            self.data_service.delete_data(dataset_id="dataset-123", **kwargs)
        self.data_service.request_gql.assert_not_called()

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"data_id": ""},
            {"data_ids": []},
            {"data_ids": ["a", ""]},
            {"data_ids": "data-456"},
            {"data_filter": {}},
            {"data_filter": {"must": {}}},
            {"data_filter": {"must": {"idIn": []}, "not": {"keyContains": ""}}},
            {"data_filter": DataListFilter()},
            {"data_filter": DataListFilter(must_filter=DataFilterOptions())},
            {"data_filter": "must"},
            {"data_filter": {"must": {"keyContains": "   "}}},
            {"data_filter": DataListFilter(must_filter=DataFilterOptions(key_contains=" "))},
            {"data_filter": {"must": {"keyContains": "", "idIn": ["a"]}}},
        ],
    )
    def test_delete_data_refuses_empty_targets(self, kwargs):
        """Empty ids or filters would select too much and are refused."""
        with pytest.raises(ValueError):
            self.data_service.delete_data(dataset_id="dataset-123", **kwargs)
        self.data_service.request_gql.assert_not_called()

    def test_delete_data_missing_dataset_id(self):
        """Test delete_data with missing dataset_id."""
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.data_service.delete_data(dataset_id=None, data_id="data-456")
        self.data_service.request_gql.assert_not_called()

    def test_delete_data_missing_data_id(self):
        """No target is a BadParameterError (and a ValueError), as before."""
        with pytest.raises(BadParameterError):
            self.data_service.delete_data(dataset_id="dataset-123", data_id=None)
        with pytest.raises(ValueError):
            self.data_service.delete_data(dataset_id="dataset-123", data_id=None)

    def test_remove_data_from_slice_starts_activity(self):
        """remove_data_from_slice starts a REMOVE_DATA_FROM_SLICE activity (2.0.0)."""
        result = self.data_service.remove_data_from_slice(
            dataset_id="dataset-123", data_id="data-456", slice_id="slice-789"
        )

        assert isinstance(result, ActivityHistory)
        assert self._sent() == {
            "datasetId": "dataset-123",
            "jobType": "REMOVE_DATA_FROM_SLICE",
            "parameters": {
                "dataset_id": "dataset-123",
                "slice_id": "slice-789",
                "data_filter": {"must": {"idIn": ["data-456"]}},
            },
        }

    def test_remove_data_from_slice_positional(self):
        """The old positional call (dataset_id, data_id, slice_id) still works."""
        self.data_service.remove_data_from_slice("dataset-123", "data-456", "slice-789")

        parameters = self._sent()["parameters"]
        assert parameters["slice_id"] == "slice-789"
        assert parameters["data_filter"] == {"must": {"idIn": ["data-456"]}}

    def test_remove_data_from_slice_many(self):
        """Several data or a filter go in one activity."""
        self.data_service.remove_data_from_slice(
            dataset_id="dataset-123", slice_id="slice-789", data_ids=["a", "b"]
        )
        assert self._sent()["parameters"]["data_filter"] == {"must": {"idIn": ["a", "b"]}}

        self.data_service.request_gql.reset_mock()
        self.data_service.remove_data_from_slice(
            dataset_id="dataset-123",
            slice_id="slice-789",
            data_filter=DataListFilter(must_filter=DataFilterOptions(key_contains="x")),
        )
        assert self._sent()["parameters"]["data_filter"] == {"must": {"keyContains": "x"}}

    def test_remove_data_from_slice_requires_slice_id(self):
        with pytest.raises(BadParameterError, match="slice_id is required"):
            self.data_service.remove_data_from_slice(dataset_id="dataset-123", data_id="data-456")
        self.data_service.request_gql.assert_not_called()

    @pytest.mark.parametrize(
        "kwargs",
        [{}, {"data_ids": []}, {"data_filter": {}}, {"data_id": "a", "data_ids": ["b"]}],
    )
    def test_remove_data_from_slice_refuses_bad_targets(self, kwargs):
        with pytest.raises(BadDeletionTargetError):
            self.data_service.remove_data_from_slice(
                dataset_id="dataset-123", slice_id="slice-789", **kwargs
            )
        self.data_service.request_gql.assert_not_called()
