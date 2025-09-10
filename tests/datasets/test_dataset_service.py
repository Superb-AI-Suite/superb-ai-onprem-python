import pytest
from unittest.mock import Mock

from spb_onprem.datasets.service import DatasetService
from spb_onprem.datasets.queries import Queries
from spb_onprem.exceptions import BadParameterError


class TestDatasetService:
    """Test cases for DatasetService delete_dataset method."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.dataset_service = DatasetService()
        self.dataset_service.request_gql = Mock()

    def test_delete_dataset_success(self):
        """Test successful dataset deletion."""
        # Arrange
        dataset_id = "dataset-123"
        mock_response = {"deleteDataset": True}
        self.dataset_service.request_gql.return_value = mock_response

        # Act
        result = self.dataset_service.delete_dataset(dataset_id)

        # Assert
        assert result is True
        self.dataset_service.request_gql.assert_called_once_with(
            Queries.DELETE_DATASET,
            Queries.DELETE_DATASET["variables"](dataset_id=dataset_id)
        )

    def test_delete_dataset_failure(self):
        """Test dataset deletion failure."""
        # Arrange
        dataset_id = "nonexistent-dataset"
        mock_response = {"deleteDataset": False}
        self.dataset_service.request_gql.return_value = mock_response

        # Act
        result = self.dataset_service.delete_dataset(dataset_id)

        # Assert
        assert result is False
        self.dataset_service.request_gql.assert_called_once_with(
            Queries.DELETE_DATASET,
            Queries.DELETE_DATASET["variables"](dataset_id=dataset_id)
        )

    def test_delete_dataset_missing_response(self):
        """Test dataset deletion with missing response field."""
        # Arrange
        dataset_id = "dataset-123"
        mock_response = {}
        self.dataset_service.request_gql.return_value = mock_response

        # Act
        result = self.dataset_service.delete_dataset(dataset_id)

        # Assert
        assert result is False

    def test_delete_dataset_missing_dataset_id(self):
        """Test delete dataset with missing dataset_id."""
        # Act & Assert
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.dataset_service.delete_dataset(dataset_id=None)

    def test_delete_dataset_empty_string_id(self):
        """Test delete dataset with empty string ID."""
        # Arrange
        dataset_id = ""

        # Act & Assert
        # Empty string should be allowed by the service, but would fail at GraphQL level
        mock_response = {"deleteDataset": False}
        self.dataset_service.request_gql.return_value = mock_response

        result = self.dataset_service.delete_dataset(dataset_id)
        assert result is False

    def test_delete_dataset_query_structure(self):
        """Test that delete dataset uses correct query structure."""
        # Arrange
        dataset_id = "test-dataset"
        mock_response = {"deleteDataset": True}
        self.dataset_service.request_gql.return_value = mock_response

        # Act
        self.dataset_service.delete_dataset(dataset_id)

        # Assert - Verify the query structure
        call_args = self.dataset_service.request_gql.call_args
        query = call_args[0][0]  # First positional argument
        variables = call_args[0][1]  # Second positional argument

        # Check query contains expected mutation
        assert query["name"] == "deleteDataset"
        assert "mutation DeleteDataset($dataset_id: ID!)" in query["query"]
        assert "deleteDataset(datasetId: $dataset_id)" in query["query"]

        # Check variables function is called correctly
        expected_variables = {"dataset_id": dataset_id}
        assert variables == expected_variables

    def test_delete_dataset_variables_function(self):
        """Test that variables function works correctly."""
        # Arrange
        dataset_id = "test-variables-dataset"

        # Act - Call the variables function directly
        variables = Queries.DELETE_DATASET["variables"](dataset_id)

        # Assert
        expected_variables = {"dataset_id": dataset_id}
        assert variables == expected_variables

    def test_delete_dataset_with_special_characters(self):
        """Test dataset deletion with special characters in ID."""
        # Arrange
        dataset_id = "dataset-with-special-chars_123@test"
        mock_response = {"deleteDataset": True}
        self.dataset_service.request_gql.return_value = mock_response

        # Act
        result = self.dataset_service.delete_dataset(dataset_id)

        # Assert
        assert result is True
        
        # Verify the special characters are passed through correctly
        call_args = self.dataset_service.request_gql.call_args
        variables = call_args[0][1]
        assert variables["dataset_id"] == dataset_id