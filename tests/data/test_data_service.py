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
                "predictions": [
                    {
                        "id": "prediction-1",
                        "content": {"id": "content-3"}
                    }
                ],
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
        assert query_structure["name"] == "getDataDetail"
        assert "query GetDataDetail($datasetId: String!, $id: String!)" in query_structure["query"]
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
                "predictions": [
                    {
                        "id": "prediction-1",
                        "content": {"id": "prediction-content-1"}
                    }
                ],
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
        assert len(result.predictions) == 1
        assert result.thumbnail.id == "thumbnail-complex"

    @patch('spb_onprem.data.service.DataService.request_gql')
    def test_get_data_detail_exception_handling(self, mock_request):
        """Test get_data_detail exception handling."""
        # Arrange
        dataset_id = "dataset-error"
        data_id = "data-error"
        mock_request.side_effect = Exception("GraphQL error")

        # Act & Assert
        with pytest.raises(Exception, match="GraphQL error"):
            self.data_service.get_data_detail(dataset_id, data_id)

        mock_request.assert_called_once()