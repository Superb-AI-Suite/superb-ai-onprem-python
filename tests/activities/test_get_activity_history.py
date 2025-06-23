import pytest
from unittest.mock import MagicMock

from spb_onprem.activities.service import ActivityService
from spb_onprem.activities.entities import ActivityHistory, ActivityStatus


@pytest.fixture
def activity_service():
    return ActivityService()


class TestGetActivityHistory:
    def test_get_activity_history(self, activity_service):
        # Given
        mock_response = {
            "id": "test_history_id",
            "jobId": "test_job_id",
            "status": "SUCCESS",
            "datasetId": "test_dataset_id",
            "parameters": {"param1": "value1"},
            "progress": {"current": 50, "total": 100},
            "createdAt": "2024-01-01T00:00:00Z",
            "createdBy": "test_user",
            "updatedAt": "2024-01-01T01:00:00Z",
            "updatedBy": "test_user",
            "meta": {"type": "export"}
        }
        activity_service.request_gql = MagicMock(return_value=mock_response)
        
        # When
        history = activity_service.get_activity_history(
            dataset_id="test_dataset_id",
            activity_history_id="test_history_id"
        )
        
        # Then
        assert isinstance(history, ActivityHistory)
        assert history.id == "test_history_id"
        assert history.activity_id == "test_job_id"
        assert history.status == ActivityStatus.SUCCESS
        assert history.dataset_id == "test_dataset_id"
        assert history.parameters == {"param1": "value1"}
        assert history.progress == {"current": 50, "total": 100}
        assert history.created_at == "2024-01-01T00:00:00Z"
        assert history.created_by == "test_user"
        assert history.updated_at == "2024-01-01T01:00:00Z"
        assert history.updated_by == "test_user"
        assert history.meta == {"type": "export"}
    
    def test_get_activity_history_minimal_data(self, activity_service):
        # Given
        mock_response = {
            "id": "test_history_id",
            "jobId": "test_job_id",
            "status": "PENDING",
            "datasetId": "test_dataset_id"
        }
        activity_service.request_gql = MagicMock(return_value=mock_response)
        
        # When
        history = activity_service.get_activity_history(
            dataset_id="test_dataset_id",
            activity_history_id="test_history_id"
        )
        
        # Then
        assert isinstance(history, ActivityHistory)
        assert history.id == "test_history_id"
        assert history.activity_id == "test_job_id"
        assert history.status == ActivityStatus.PENDING
        assert history.dataset_id == "test_dataset_id"
        assert history.parameters is None
        assert history.progress is None
        assert history.meta is None
    
    def test_activity_history_model_validation(self):
        # Given
        history_data = {
            "id": "test_history_id",
            "jobId": "test_job_id",
            "status": "RUNNING",
            "datasetId": "test_dataset_id",
            "parameters": {"param1": "value1"},
            "progress": {"current": 25, "total": 100},
            "createdAt": "2024-01-01T00:00:00Z",
            "createdBy": "test_user",
            "updatedAt": "2024-01-01T01:00:00Z",
            "updatedBy": "test_user",
            "meta": {"type": "export", "version": "1.0"}
        }
        
        # When
        history = ActivityHistory.model_validate(history_data)
        
        # Then
        assert isinstance(history, ActivityHistory)
        assert history.id == "test_history_id"
        assert history.activity_id == "test_job_id"
        assert history.status == ActivityStatus.RUNNING
        assert history.dataset_id == "test_dataset_id"
        assert history.parameters == {"param1": "value1"}
        assert history.progress == {"current": 25, "total": 100}
        assert history.created_at == "2024-01-01T00:00:00Z"
        assert history.created_by == "test_user"
        assert history.updated_at == "2024-01-01T01:00:00Z"
        assert history.updated_by == "test_user"
        assert history.meta == {"type": "export", "version": "1.0"}
    
    def test_get_activity_history_with_different_statuses(self, activity_service):
        # Test different status values
        statuses = [
            ("PENDING", ActivityStatus.PENDING),
            ("RUNNING", ActivityStatus.RUNNING),
            ("SUCCESS", ActivityStatus.SUCCESS),
            ("FAILED", ActivityStatus.FAILED),
            ("CANCELLED", ActivityStatus.CANCELLED),
        ]
        
        for status_value, expected_status in statuses:
            # Given
            mock_response = {
                "id": f"history_{status_value.lower()}",
                "jobId": "test_job_id",
                "status": status_value,
                "datasetId": "test_dataset_id"
            }
            activity_service.request_gql = MagicMock(return_value=mock_response)
            
            # When
            history = activity_service.get_activity_history(
                dataset_id="test_dataset_id",
                activity_history_id=f"history_{status_value.lower()}"
            )
            
            # Then
            assert history.status == expected_status
            assert history.id == f"history_{status_value.lower()}" 