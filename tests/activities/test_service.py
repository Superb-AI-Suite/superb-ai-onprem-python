import pytest
from unittest.mock import MagicMock, patch

from spb_onprem.activities.service import ActivityService
from spb_onprem.activities.entities import Activity, ActivityHistory, ActivityStatus
from spb_onprem.base_types import Undefined


@pytest.fixture
def activity_service():
    return ActivityService()


class TestActivityService:
    def test_create_activity(self, activity_service):
        # Given
        mock_response = {
            "createJob": {
                "id": "test_id",
                "type": "test_type",
                "name": "test_name",
                "description": "test_description"
            }
        }
        activity_service.request_gql = MagicMock(return_value=mock_response)
        
        # When
        activity = activity_service.create_activity(
            activity_type="test_type",
            name="test_name",
            description="test_description"
        )
        
        # Then
        assert isinstance(activity, Activity)
        assert activity.id == "test_id"
        assert activity.type == "test_type"
        assert activity.name == "test_name"
        assert activity.description == "test_description"
    
    def test_get_activities(self, activity_service):
        # Given
        mock_response = {
            "jobs": {
                "activities": [
                    {
                        "id": "test_id_1",
                        "type": "test_type",
                        "name": "test_name_1"
                    },
                    {
                        "id": "test_id_2",
                        "type": "test_type",
                        "name": "test_name_2"
                    }
                ],
                "next": "next_cursor",
                "totalCount": 2
            }
        }
        activity_service.request_gql = MagicMock(return_value=mock_response)
        
        # When
        activities, next_cursor, total_count = activity_service.get_activities(
            dataset_id="test_dataset_id"
        )
        
        # Then
        assert len(activities) == 2
        assert all(isinstance(activity, Activity) for activity in activities)
        assert next_cursor == "next_cursor"
        assert total_count == 2
    
    def test_start_activity(self, activity_service):
        # Given
        mock_response = {
            "startJob": {
                "id": "test_history_id",
                "jobId": "test_activity_id",
                "status": ActivityStatus.RUNNING.value
            }
        }
        activity_service.request_gql = MagicMock(return_value=mock_response)
        
        # When
        activity_history = activity_service.start_activity(
            dataset_id="test_dataset_id",
            activity_id="test_activity_id"
        )
        
        # Then
        assert isinstance(activity_history, ActivityHistory)
        assert activity_history.id == "test_history_id"
        assert activity_history.activity_id == "test_activity_id"
        assert activity_history.status == ActivityStatus.RUNNING
    
    def test_update_activity_history_status(self, activity_service):
        # Given
        mock_response = {
            "updateJobHistory": {
                "id": "test_history_id",
                "jobId": "test_activity_id",
                "status": ActivityStatus.SUCCESS.value
            }
        }
        activity_service.request_gql = MagicMock(return_value=mock_response)
        
        # When
        activity_history = activity_service.update_activity_history_status(
            activity_history_id="test_history_id",
            status=ActivityStatus.SUCCESS
        )
        
        # Then
        assert isinstance(activity_history, ActivityHistory)
        assert activity_history.id == "test_history_id"
        assert activity_history.status == ActivityStatus.SUCCESS
    
    def test_update_activity_history_progress(self, activity_service):
        # Given
        mock_response = {
            "updateJobHistory": {
                "id": "test_history_id",
                "jobId": "test_activity_id",
                "progress": {"current": 50, "total": 100}
            }
        }
        activity_service.request_gql = MagicMock(return_value=mock_response)
        
        # When
        activity_history = activity_service.update_activity_history_progress(
            activity_history_id="test_history_id",
            progress={"current": 50, "total": 100}
        )
        
        # Then
        assert isinstance(activity_history, ActivityHistory)
        assert activity_history.id == "test_history_id"
        assert activity_history.progress == {"current": 50, "total": 100} 