import pytest
from spb_onprem.activities.params.update_activity_history import update_activity_history_params
from spb_onprem.activities.entities import ActivityStatus
from spb_onprem.exceptions import BadParameterError
from spb_onprem.base_types import Undefined


class TestUpdateActivityHistoryParams:
    def test_update_activity_history_params_with_status(self):
        # Given
        activity_history_id = "test_history_id"
        status = ActivityStatus.SUCCESS
        meta = {"key": "value"}
        
        # When
        params = update_activity_history_params(
            activity_history_id=activity_history_id,
            status=status,
            meta=meta
        )
        
        # Then
        assert params["activity_history_id"] == activity_history_id
        assert params["status"] == status
        assert params["meta"] == meta
        assert "progress" not in params
    
    def test_update_activity_history_params_with_progress(self):
        # Given
        activity_history_id = "test_history_id"
        progress = {"current": 50, "total": 100}
        
        # When
        params = update_activity_history_params(
            activity_history_id=activity_history_id,
            progress=progress
        )
        
        # Then
        assert params["activity_history_id"] == activity_history_id
        assert params["progress"] == progress
        assert "status" not in params
        assert "meta" not in params
    
    def test_update_activity_history_params_without_required_fields(self):
        # Given
        activity_history_id = None
        
        # When/Then
        with pytest.raises(BadParameterError) as exc_info:
            update_activity_history_params(
                activity_history_id=activity_history_id
            )
        assert str(exc_info.value) == "Activity history ID is required"
    
    def test_update_activity_history_params_without_status_or_progress(self):
        # Given
        activity_history_id = "test_history_id"
        
        # When/Then
        with pytest.raises(BadParameterError) as exc_info:
            update_activity_history_params(
                activity_history_id=activity_history_id,
                status=Undefined,
                progress=Undefined
            )
        assert str(exc_info.value) == "Either status or progress must be provided" 