import pytest
from unittest.mock import Mock

from spb_onprem.models.service import ModelService
from spb_onprem.models.queries import Queries
from spb_onprem.exceptions import BadParameterError


class TestModelService:
    """Test cases for ModelService methods."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.model_service = ModelService()
        self.model_service.request_gql = Mock()

    def test_get_models_success(self):
        """Test successful models list retrieval."""
        # Arrange
        dataset_id = "dataset-123"
        filter_dict = {"name": "test"}
        cursor = "cursor-abc"
        length = 25
        
        mock_response = {
            "models": [
                {"id": "model-1", "name": "Model 1"},
                {"id": "model-2", "name": "Model 2"}
            ],
            "next": "cursor-def",
            "totalCount": 50
        }
        self.model_service.request_gql.return_value = mock_response

        # Act
        result = self.model_service.get_models(
            dataset_id=dataset_id,
            filter=filter_dict,
            cursor=cursor,
            length=length
        )

        # Assert
        models, next_cursor, total_count = result
        assert len(models) == 2
        assert models[0].id == "model-1"
        assert models[0].name == "Model 1"
        assert models[1].id == "model-2"
        assert models[1].name == "Model 2"
        assert next_cursor == "cursor-def"
        assert total_count == 50
        self.model_service.request_gql.assert_called_once_with(
            Queries.GET_MODELS,
            Queries.GET_MODELS["variables"](
                dataset_id=dataset_id,
                filter=filter_dict,
                cursor=cursor,
                length=length
            )
        )

    def test_get_models_without_filter(self):
        """Test models retrieval without filter."""
        # Arrange
        dataset_id = "dataset-123"
        
        mock_response = {
            "models": [{"id": "model-1", "name": "Test Model"}],
            "next": None,
            "totalCount": 1
        }
        self.model_service.request_gql.return_value = mock_response

        # Act
        result = self.model_service.get_models(dataset_id=dataset_id)

        # Assert
        models, next_cursor, total_count = result
        assert total_count == 1
        assert next_cursor is None
        assert len(models) == 1
        assert models[0].name == "Test Model"

    def test_get_models_with_pagination(self):
        """Test models retrieval with pagination parameters."""
        # Arrange
        dataset_id = "dataset-123"
        cursor = "pagination-cursor"
        length = 10
        
        mock_response = {
            "models": [
                {"id": "model-3", "name": "Model 3"},
                {"id": "model-4", "name": "Model 4"}
            ],
            "next": "next-cursor",
            "totalCount": 20
        }
        self.model_service.request_gql.return_value = mock_response

        # Act
        result = self.model_service.get_models(
            dataset_id=dataset_id,
            cursor=cursor,
            length=length
        )

        # Assert
        models, next_cursor, total_count = result
        assert next_cursor == "next-cursor"
        assert total_count == 20
        assert len(models) == 2

    def test_get_models_missing_dataset_id(self):
        """Test models with missing dataset_id."""
        # Act & Assert
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.model_service.get_models(dataset_id=None)

    def test_get_models_empty_response(self):
        """Test models with empty response."""
        # Arrange
        dataset_id = "dataset-123"
        mock_response = {}
        self.model_service.request_gql.return_value = mock_response

        # Act
        result = self.model_service.get_models(dataset_id=dataset_id)

        # Assert
        models, next_cursor, total_count = result
        assert len(models) == 0
        assert next_cursor is None
        assert total_count == 0

    def test_get_models_zero_results(self):
        """Test models retrieval with zero results."""
        # Arrange
        dataset_id = "empty-dataset"
        
        mock_response = {
            "models": [],
            "next": None,
            "totalCount": 0
        }
        self.model_service.request_gql.return_value = mock_response

        # Act
        result = self.model_service.get_models(dataset_id=dataset_id)

        # Assert
        models, next_cursor, total_count = result
        assert total_count == 0
        assert next_cursor is None
        assert len(models) == 0

    def test_delete_model_success(self):
        """Test successful model deletion."""
        # Arrange
        dataset_id = "dataset-123"
        model_id = "model-456"
        
        mock_response = {"deleteModel": True}
        self.model_service.request_gql.return_value = mock_response

        # Act
        result = self.model_service.delete_model(
            dataset_id=dataset_id,
            model_id=model_id
        )

        # Assert
        assert result is True
        self.model_service.request_gql.assert_called_once_with(
            Queries.DELETE_MODEL,
            Queries.DELETE_MODEL["variables"](
                dataset_id=dataset_id,
                model_id=model_id
            )
        )

    def test_delete_model_failure(self):
        """Test model deletion failure."""
        # Arrange
        dataset_id = "dataset-123"
        model_id = "nonexistent-model"
        
        mock_response = {"deleteModel": False}
        self.model_service.request_gql.return_value = mock_response

        # Act
        result = self.model_service.delete_model(
            dataset_id=dataset_id,
            model_id=model_id
        )

        # Assert
        assert result is False

    def test_delete_model_missing_response(self):
        """Test model deletion with missing response field."""
        # Arrange
        dataset_id = "dataset-123"
        model_id = "model-456"
        
        mock_response = {}
        self.model_service.request_gql.return_value = mock_response

        # Act
        result = self.model_service.delete_model(
            dataset_id=dataset_id,
            model_id=model_id
        )

        # Assert
        assert result is False

    def test_delete_model_missing_dataset_id(self):
        """Test delete model with missing dataset_id."""
        # Arrange
        model_id = "model-456"

        # Act & Assert
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.model_service.delete_model(
                dataset_id=None,
                model_id=model_id
            )

    def test_delete_model_missing_model_id(self):
        """Test delete model with missing model_id."""
        # Arrange
        dataset_id = "dataset-123"

        # Act & Assert
        with pytest.raises(BadParameterError, match="model_id is required"):
            self.model_service.delete_model(
                dataset_id=dataset_id,
                model_id=None
            )

    def test_delete_model_both_missing_params(self):
        """Test delete model with both missing parameters."""
        # Act & Assert
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.model_service.delete_model(
                dataset_id=None,
                model_id=None
            )