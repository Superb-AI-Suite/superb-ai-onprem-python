import pytest
from unittest.mock import Mock

from spb_onprem.predictions.service import PredictionService
from spb_onprem.predictions.queries import Queries
from spb_onprem.predictions.entities import PredictionSet
from spb_onprem.exceptions import BadParameterError


class TestPredictionService:
    """Test cases for PredictionService methods."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.prediction_service = PredictionService()
        self.prediction_service.request_gql = Mock()

    def test_get_prediction_sets_success(self):
        """Test successful prediction sets list retrieval."""
        # Arrange
        dataset_id = "dataset-123"
        filter_dict = {"name": "test"}
        cursor = "cursor-abc"
        length = 25
        
        mock_response = {
            "predictionSets": [
                {"id": "pred-1", "name": "Prediction Set 1"},
                {"id": "pred-2", "name": "Prediction Set 2"}
            ],
            "next": "cursor-def",
            "totalCount": 100
        }
        self.prediction_service.request_gql.return_value = mock_response

        # Act
        result = self.prediction_service.get_prediction_sets(
            dataset_id=dataset_id,
            filter=filter_dict,
            cursor=cursor,
            length=length
        )

        # Assert
        prediction_sets, next_cursor, total_count = result
        assert len(prediction_sets) == 2
        assert prediction_sets[0].id == "pred-1"
        assert prediction_sets[0].name == "Prediction Set 1"
        assert prediction_sets[1].id == "pred-2"
        assert prediction_sets[1].name == "Prediction Set 2"
        assert next_cursor == "cursor-def"
        assert total_count == 100
        self.prediction_service.request_gql.assert_called_once_with(
            Queries.GET_PREDICTION_SETS,
            Queries.GET_PREDICTION_SETS["variables"](
                dataset_id=dataset_id,
                filter=filter_dict,
                cursor=cursor,
                length=length
            )
        )

    def test_get_prediction_sets_without_filter(self):
        """Test prediction sets retrieval without filter."""
        # Arrange
        dataset_id = "dataset-123"
        
        mock_response = {
            "predictionSets": [{"id": "pred-1", "name": "Test"}],
            "next": None,
            "totalCount": 1
        }
        self.prediction_service.request_gql.return_value = mock_response

        # Act
        result = self.prediction_service.get_prediction_sets(dataset_id=dataset_id)

        # Assert
        prediction_sets, next_cursor, total_count = result
        assert total_count == 1
        assert next_cursor is None
        assert len(prediction_sets) == 1

    def test_get_prediction_sets_missing_dataset_id(self):
        """Test prediction sets with missing dataset_id."""
        # Act & Assert
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.prediction_service.get_prediction_sets(dataset_id=None)

    def test_get_prediction_sets_empty_response(self):
        """Test prediction sets with empty response."""
        # Arrange
        dataset_id = "dataset-123"
        mock_response = {}
        self.prediction_service.request_gql.return_value = mock_response

        # Act
        result = self.prediction_service.get_prediction_sets(dataset_id=dataset_id)

        # Assert
        prediction_sets, next_cursor, total_count = result
        assert len(prediction_sets) == 0
        assert next_cursor is None
        assert total_count == 0

    def test_get_prediction_set_success(self):
        """Test successful single prediction set retrieval."""
        # Arrange
        dataset_id = "dataset-123"
        prediction_set_id = "pred-set-456"
        
        mock_response = {
            "predictionSet": {
                "id": prediction_set_id,
                "name": "Test Prediction Set",
                "annotationsContents": ["content-1", "content-2"],
                "evaluationResultContent": {"id": "eval-result-1"}
            }
        }
        self.prediction_service.request_gql.return_value = mock_response

        # Act
        result = self.prediction_service.get_prediction_set(
            dataset_id=dataset_id,
            prediction_set_id=prediction_set_id
        )

        # Assert
        assert isinstance(result, PredictionSet)
        assert result.id == prediction_set_id
        assert result.name == "Test Prediction Set"
        assert result.annotations_contents == ["content-1", "content-2"]
        assert result.evaluation_result_content == {"id": "eval-result-1"}
        self.prediction_service.request_gql.assert_called_once_with(
            Queries.GET_PREDICTION_SET,
            Queries.GET_PREDICTION_SET["variables"](
                dataset_id=dataset_id,
                prediction_set_id=prediction_set_id
            )
        )

    def test_get_prediction_set_missing_dataset_id(self):
        """Test get prediction set with missing dataset_id."""
        # Arrange
        prediction_set_id = "pred-set-456"

        # Act & Assert
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.prediction_service.get_prediction_set(
                dataset_id=None,
                prediction_set_id=prediction_set_id
            )

    def test_get_prediction_set_missing_prediction_set_id(self):
        """Test get prediction set with missing prediction_set_id."""
        # Arrange
        dataset_id = "dataset-123"

        # Act & Assert
        with pytest.raises(BadParameterError, match="prediction_set_id is required"):
            self.prediction_service.get_prediction_set(
                dataset_id=dataset_id,
                prediction_set_id=None
            )

    def test_get_prediction_set_minimal_response(self):
        """Test get prediction set with minimal response."""
        # Arrange
        dataset_id = "dataset-123"
        prediction_set_id = "pred-set-456"
        
        mock_response = {"predictionSet": {"id": prediction_set_id}}
        self.prediction_service.request_gql.return_value = mock_response

        # Act
        result = self.prediction_service.get_prediction_set(
            dataset_id=dataset_id,
            prediction_set_id=prediction_set_id
        )

        # Assert
        assert isinstance(result, PredictionSet)
        assert result.id == prediction_set_id
        assert result.name is None  # Optional fields should be None

    def test_delete_prediction_set_success(self):
        """Test successful prediction set deletion."""
        # Arrange
        dataset_id = "dataset-123"
        prediction_set_id = "pred-set-456"
        
        mock_response = {"deletePredictionSet": True}
        self.prediction_service.request_gql.return_value = mock_response

        # Act
        result = self.prediction_service.delete_prediction_set(
            dataset_id=dataset_id,
            prediction_set_id=prediction_set_id
        )

        # Assert
        assert result is True
        self.prediction_service.request_gql.assert_called_once_with(
            Queries.DELETE_PREDICTION_SET,
            Queries.DELETE_PREDICTION_SET["variables"](
                dataset_id=dataset_id,
                prediction_set_id=prediction_set_id
            )
        )

    def test_delete_prediction_set_failure(self):
        """Test prediction set deletion failure."""
        # Arrange
        dataset_id = "dataset-123"
        prediction_set_id = "nonexistent-pred-set"
        
        mock_response = {"deletePredictionSet": False}
        self.prediction_service.request_gql.return_value = mock_response

        # Act
        result = self.prediction_service.delete_prediction_set(
            dataset_id=dataset_id,
            prediction_set_id=prediction_set_id
        )

        # Assert
        assert result is False

    def test_delete_prediction_set_missing_response(self):
        """Test prediction set deletion with missing response field."""
        # Arrange
        dataset_id = "dataset-123"
        prediction_set_id = "pred-set-456"
        
        mock_response = {}
        self.prediction_service.request_gql.return_value = mock_response

        # Act
        result = self.prediction_service.delete_prediction_set(
            dataset_id=dataset_id,
            prediction_set_id=prediction_set_id
        )

        # Assert
        assert result is False

    def test_delete_prediction_set_missing_dataset_id(self):
        """Test delete prediction set with missing dataset_id."""
        # Arrange
        prediction_set_id = "pred-set-456"

        # Act & Assert
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.prediction_service.delete_prediction_set(
                dataset_id=None,
                prediction_set_id=prediction_set_id
            )

    def test_delete_prediction_set_missing_prediction_set_id(self):
        """Test delete prediction set with missing prediction_set_id."""
        # Arrange
        dataset_id = "dataset-123"

        # Act & Assert
        with pytest.raises(BadParameterError, match="prediction_set_id is required"):
            self.prediction_service.delete_prediction_set(
                dataset_id=dataset_id,
                prediction_set_id=None
            )

    def test_delete_prediction_from_data_success(self):
        """Test successful prediction deletion from data."""
        # Arrange
        dataset_id = "dataset-123"
        data_id = "data-456"
        prediction_set_id = "pred-set-789"
        
        mock_response = {"deletePrediction": {"id": data_id, "dataset_id": dataset_id}}
        self.prediction_service.request_gql.return_value = mock_response

        # Act
        result = self.prediction_service.delete_prediction_from_data(
            dataset_id=dataset_id,
            data_id=data_id,
            prediction_set_id=prediction_set_id
        )

        # Assert
        assert result is True
        self.prediction_service.request_gql.assert_called_once_with(
            Queries.DELETE_PREDICTION_FROM_DATA,
            Queries.DELETE_PREDICTION_FROM_DATA["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                prediction_set_id=prediction_set_id
            )
        )

    def test_delete_prediction_from_data_failure(self):
        """Test prediction deletion from data failure."""
        # Arrange
        dataset_id = "dataset-123"
        data_id = "data-456"
        prediction_set_id = "pred-set-789"
        
        mock_response = {"deletePrediction": None}
        self.prediction_service.request_gql.return_value = mock_response

        # Act
        result = self.prediction_service.delete_prediction_from_data(
            dataset_id=dataset_id,
            data_id=data_id,
            prediction_set_id=prediction_set_id
        )

        # Assert
        assert result is False

    def test_delete_prediction_from_data_missing_dataset_id(self):
        """Test delete prediction from data with missing dataset_id."""
        # Arrange
        data_id = "data-456"
        prediction_set_id = "pred-set-789"

        # Act & Assert
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.prediction_service.delete_prediction_from_data(
                dataset_id=None,
                data_id=data_id,
                prediction_set_id=prediction_set_id
            )

    def test_delete_prediction_from_data_missing_data_id(self):
        """Test delete prediction from data with missing data_id."""
        # Arrange
        dataset_id = "dataset-123"
        prediction_set_id = "pred-set-789"

        # Act & Assert
        with pytest.raises(BadParameterError, match="data_id is required"):
            self.prediction_service.delete_prediction_from_data(
                dataset_id=dataset_id,
                data_id=None,
                prediction_set_id=prediction_set_id
            )

    def test_delete_prediction_from_data_missing_prediction_set_id(self):
        """Test delete prediction from data with missing prediction_set_id."""
        # Arrange
        dataset_id = "dataset-123"
        data_id = "data-456"

        # Act & Assert
        with pytest.raises(BadParameterError, match="prediction_set_id is required"):
            self.prediction_service.delete_prediction_from_data(
                dataset_id=dataset_id,
                data_id=data_id,
                prediction_set_id=None
            )