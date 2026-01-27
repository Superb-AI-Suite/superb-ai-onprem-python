import pytest
from unittest.mock import Mock

from spb_onprem.data.service import DataService
from spb_onprem.data.queries import Queries
from spb_onprem.exceptions import BadParameterError


class TestDataService:
    """Test cases for DataService."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.data_service = DataService()
        self.data_service.request_gql = Mock()

    def test_delete_data_query_structure(self):
        """Test DELETE query structure and parameters."""
        # Arrange
        dataset_id = "dataset-123"
        data_id = "data-456"
        
        # Act
        query = Queries.DELETE["query"]
        variables = Queries.DELETE["variables"](dataset_id=dataset_id, data_id=data_id)
        
        # Assert
        assert "mutation (" in query
        assert "$dataset_id: ID!" in query
        assert "$data_id: ID!" in query
        assert "$data_id: ID!," in query  # GraphQL allows trailing commas
        assert "deleteData(" in query
        assert "datasetId: $dataset_id" in query
        assert "id: $data_id," in query  # GraphQL allows trailing commas
        assert variables == {
            "dataset_id": dataset_id,
            "data_id": data_id
        }

    def test_delete_data_success(self):
        """Test successful data deletion."""
        # Arrange
        dataset_id = "dataset-123"
        data_id = "data-456"
        mock_response = True
        self.data_service.request_gql.return_value = mock_response

        # Act
        result = self.data_service.delete_data(dataset_id=dataset_id, data_id=data_id)

        # Assert
        assert result is True
        self.data_service.request_gql.assert_called_once_with(
            Queries.DELETE,
            Queries.DELETE["variables"](dataset_id=dataset_id, data_id=data_id)
        )

    def test_delete_data_failure(self):
        """Test data deletion failure."""
        # Arrange
        dataset_id = "dataset-123"
        data_id = "nonexistent-data"
        mock_response = False
        self.data_service.request_gql.return_value = mock_response

        # Act
        result = self.data_service.delete_data(dataset_id=dataset_id, data_id=data_id)

        # Assert
        assert result is False
        self.data_service.request_gql.assert_called_once_with(
            Queries.DELETE,
            Queries.DELETE["variables"](dataset_id=dataset_id, data_id=data_id)
        )

    def test_delete_data_missing_response(self):
        """Test data deletion with missing response field."""
        # Arrange
        dataset_id = "dataset-123"
        data_id = "data-456"
        mock_response = False
        self.data_service.request_gql.return_value = mock_response

        # Act
        result = self.data_service.delete_data(dataset_id=dataset_id, data_id=data_id)

        # Assert
        assert result is False

    def test_delete_data_missing_dataset_id(self):
        """Test delete_data with missing dataset_id."""
        # Arrange
        data_id = "data-456"

        # Act & Assert
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.data_service.delete_data(dataset_id=None, data_id=data_id)

    def test_delete_data_missing_data_id(self):
        """Test delete_data with missing data_id."""
        # Arrange
        dataset_id = "dataset-123"

        # Act & Assert
        with pytest.raises(BadParameterError, match="data_id is required"):
            self.data_service.delete_data(dataset_id=dataset_id, data_id=None)