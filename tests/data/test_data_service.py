import pytest
from unittest.mock import Mock, patch

from spb_onprem.data.service import DataService
from spb_onprem.data.queries import Queries
from spb_onprem.data.entities import Data
from spb_onprem.exceptions import BadParameterError


class TestDataService:
    """Test cases for DataService with new get_data_detail method."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.data_service = DataService()
        self.data_service.request_gql = Mock()

    def test_get_data_detail_success(self):
        """Test successful data detail retrieval."""
        # Arrange
        dataset_id = "dataset-123"
        data_id = "data-456"
        mock_response = {
            "data": {
                "id": data_id,
                "datasetId": dataset_id,
                "scene": [
                    {
                        "id": "scene-1",
                        "content": {"id": "content-1"}
                    }
                ],
                "annotation": {
                    "versions": [
                        {
                            "id": "annotation-1",
                            "content": {"id": "content-2"}
                        }
                    ]
                },
                "thumbnail": {
                    "id": "thumbnail-1"
                }
            }
        }
        self.data_service.request_gql.return_value = mock_response

        # Act
        result = self.data_service.get_data_detail(dataset_id, data_id)

        # Assert
        assert isinstance(result, Data)
        assert result.id == data_id
        assert result.dataset_id == dataset_id
        self.data_service.request_gql.assert_called_once_with(
            Queries.GET_DETAIL,
            Queries.GET_DETAIL["variables"](dataset_id, data_id)
        )

    def test_get_data_detail_missing_dataset_id(self):
        """Test get_data_detail with missing dataset_id."""
        # Arrange
        dataset_id = None
        data_id = "data-456"

        # Act & Assert
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.data_service.get_data_detail(dataset_id, data_id)

    def test_get_data_detail_missing_data_id(self):
        """Test get_data_detail with missing data_id."""
        # Arrange
        dataset_id = "dataset-123"
        data_id = None

        # Act & Assert
        with pytest.raises(BadParameterError, match="data_id is required"):
            self.data_service.get_data_detail(dataset_id, data_id)

    def test_get_data_detail_empty_response(self):
        """Test get_data_detail with empty data response."""
        # Arrange
        dataset_id = "dataset-123"
        data_id = "data-456"
        mock_response = {"data": {}}
        self.data_service.request_gql.return_value = mock_response

        # Act
        result = self.data_service.get_data_detail(dataset_id, data_id)

        # Assert
        assert isinstance(result, Data)
        self.data_service.request_gql.assert_called_once_with(
            Queries.GET_DETAIL,
            Queries.GET_DETAIL["variables"](dataset_id, data_id)
        )

    def test_get_data_detail_missing_data_field(self):
        """Test get_data_detail with missing data field in response."""
        # Arrange
        dataset_id = "dataset-123"
        data_id = "data-456"
        mock_response = {}  # No data field
        self.data_service.request_gql.return_value = mock_response

        # Act
        result = self.data_service.get_data_detail(dataset_id, data_id)

        # Assert
        assert isinstance(result, Data)
        self.data_service.request_gql.assert_called_once_with(
            Queries.GET_DETAIL,
            Queries.GET_DETAIL["variables"](dataset_id, data_id)
        )

    def test_get_data_detail_query_structure(self):
        """Test that GET_DETAIL query has correct structure."""
        # Arrange & Act
        query_structure = Queries.GET_DETAIL

        # Assert
        assert query_structure["name"] == "data"
        assert "query GetDataDetail($datasetId: ID!, $id: ID!)" in query_structure["query"]
        assert "data(datasetId: $datasetId, id: $id)" in query_structure["query"]
        assert callable(query_structure["variables"])

    def test_get_data_detail_variables_function(self):
        """Test that variables function generates correct parameters."""
        # Arrange
        dataset_id = "dataset-789"
        data_id = "data-101"

        # Act
        variables = Queries.GET_DETAIL["variables"](dataset_id, data_id)

        # Assert
        assert variables == {
            "datasetId": dataset_id,
            "id": data_id
        }

    def test_get_data_detail_with_nested_relationships(self):
        """Test get_data_detail with complex nested relationships."""
        # Arrange
        dataset_id = "dataset-complex"
        data_id = "data-complex"
        mock_response = {
            "data": {
                "id": data_id,
                "datasetId": dataset_id,
                "scene": [
                    {
                        "id": "scene-1",
                        "content": {"id": "scene-content-1"}
                    },
                    {
                        "id": "scene-2", 
                        "content": {"id": "scene-content-2"}
                    }
                ],
                "annotation": {
                    "versions": [
                        {
                            "id": "annotation-v1",
                            "content": {"id": "annotation-content-1"}
                        },
                        {
                            "id": "annotation-v2",
                            "content": {"id": "annotation-content-2"}
                        }
                    ]
                },
                "thumbnail": {
                    "id": "thumbnail-complex"
                }
            }
        }
        self.data_service.request_gql.return_value = mock_response

        # Act
        result = self.data_service.get_data_detail(dataset_id, data_id)

        # Assert
        assert isinstance(result, Data)
        assert result.id == data_id
        assert len(result.scene) == 2
        assert len(result.annotation.versions) == 2
        assert result.thumbnail.id == "thumbnail-complex"

    def test_get_data_detail_exception_handling(self):
        """Test get_data_detail exception handling."""
        # Arrange
        dataset_id = "dataset-error"
        data_id = "data-error"
        self.data_service.request_gql.side_effect = Exception("GraphQL error")

        # Act & Assert
        with pytest.raises(Exception, match="GraphQL error"):
            self.data_service.get_data_detail(dataset_id, data_id)

        self.data_service.request_gql.assert_called_once()

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