import time
from typing import Optional, Union, List, Tuple

from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import BadParameterError
from spb_onprem.base_types import (
    Undefined,
    UndefinedType,
)

from .entities import (
    Activity,
    ActivitySchema,
    ActivityHistory,
    ActivityStatus,
    TERMINAL_ACTIVITY_STATUSES,
    TaskDetail,
    TaskLogChunk,
    TaskLogDownload,
    TaskMonitoring,
    TaskMonitoringRunType,
    TaskRenderedTemplates,
)
from .params import (
    ActivitiesFilter,
)
from .queries import (
    Queries,
)


class ActivityService(BaseService):
    """Service class for handling activity-related operations."""
    
    def create_activity(
        self,
        activity_type: str,
        name: str,
        dataset_id: Union[
            UndefinedType,
            str
        ] = Undefined,
        description: Union[
            UndefinedType,
            str
        ] = Undefined,
        progress_schema: Optional[List[ActivitySchema]] = None,
        parameter_schema: Optional[List[ActivitySchema]] = None,
        settings: Optional[dict] = None,
        meta: Optional[dict] = None,
    ) -> Activity:
        """Create an activity.
        
        Args:
            activity_type (str): The type of the activity to create.
            name (str): The name of the activity to create.
            dataset_id (Optional[str]): The ID of the dataset to create the activity for.
            description (Optional[str]): The description of the activity to create.
            progress_schema (Optional[List[ActivitySchema]]): The progress schema of the activity to create.
            parameter_schema (Optional[List[ActivitySchema]]): The parameter schema of the activity to create.
            settings (Optional[dict]): The settings of the activity to create.
            meta (Optional[dict]): The meta of the activity to create.
        """
        response = self.request_gql(
            Queries.CREATE_ACTIVITY,
            Queries.CREATE_ACTIVITY["variables"](
                activity_type=activity_type,
                name=name,
                dataset_id=dataset_id,
                description=description,
                progress_schema=progress_schema,
                parameter_schema=parameter_schema,
                settings=settings,
                meta=meta,
            )
        )
        return Activity.model_validate(response)
    
    def get_activities(
        self,
        dataset_id: Optional[str] = None,
        activity_filter: Optional[ActivitiesFilter] = None,
        cursor: Optional[str] = None,
        length: int = 10
    ) -> Tuple[List[Activity], Optional[str], int]:
        """Get activities.
        
        Args:
            dataset_id (str): The ID of the dataset to get activities for.
            activity_filter (Optional[ActivitiesFilter]): The filter to apply to the activities.
            cursor (Optional[str]): The cursor to use for pagination.
            length (int): The number of activities to get.
        
        Returns:
            Tuple[List[Activity], Optional[str], int]: A tuple containing the activities, the next cursor, and the total count of activities.
        """
        response = self.request_gql(
            Queries.GET_ACTIVITIES,
            Queries.GET_ACTIVITIES["variables"](
                dataset_id=dataset_id,
                activity_filter=activity_filter,
                cursor=cursor,
                length=length,
            )
        )
        activities_dict = response.get("jobs", [])
        return (
            [Activity.model_validate(activity_dict) for activity_dict in activities_dict],
            response.get("next"),
            response.get("totalCount"),
        )

    def get_activity(
        self,
        activity_id: Optional[str] = None,
        activity_name: Optional[str] = None,
        dataset_id: Optional[str] = None,
    ) -> Activity:
        """Get an activity.
        
        Args:
            activity_id (str): The ID of the activity to get.
            dataset_id (Optional[str]): The ID of the dataset to get the activity for.
        
        Returns:
            Activity: The activity object.
        """
        response = self.request_gql(
            Queries.GET_ACTIVITY,
            Queries.GET_ACTIVITY["variables"](
                activity_id=activity_id,
                activity_name=activity_name,
                dataset_id=dataset_id,
            )
        )
        return Activity.model_validate(response)

    def get_activity_history(
        self,
        dataset_id: str,
        activity_history_id: str,
    ) -> ActivityHistory:
        """Get an activity history.
        
        Args:
            dataset_id (str): The ID of the dataset to get the activity history for.
            activity_history_id (str): The ID of the job to get the activity history for.
        
        Returns:
            ActivityHistory: The activity history object.
        """
        response = self.request_gql(
            Queries.GET_ACTIVITY_HISTORY,
            Queries.GET_ACTIVITY_HISTORY["variables"](
                dataset_id=dataset_id,
                activity_history_id=activity_history_id,
            )
        )
        return ActivityHistory.model_validate(response)

    def wait_for_activity(
        self,
        activity_history_id: str,
        dataset_id: Optional[str] = None,
        timeout: float = 600.0,
        poll_interval: float = 5.0,
    ) -> ActivityHistory:
        """Wait until an activity history ends.

        Polls ``get_activity_history`` until the status is SUCCESS, FAILED,
        CANCELED or REJECTED and returns that history. It does not raise for
        FAILED, CANCELED or REJECTED; check ``status`` (and ``meta``) yourself.
        AWAITING_APPROVAL is not an end state: the wait goes on until an admin
        approves or rejects the activity, or the timeout passes.

        Args:
            activity_history_id (str): The activity history ID, e.g. the ``id``
                of what a delete function returned.
            dataset_id (Optional[str]): The dataset of the activity, if known.
            timeout (float): Seconds to wait in total. Defaults to 600.
            poll_interval (float): Seconds between two polls. Defaults to 5.

        Raises:
            BadParameterError: If activity_history_id is missing.
            ValueError: If timeout or poll_interval is not positive.
            TimeoutError: If the activity has not ended within ``timeout``. The
                message has the last status seen.

        Returns:
            ActivityHistory: The ended activity history.
        """
        if not activity_history_id:
            raise BadParameterError("activity_history_id is required.")
        if timeout <= 0:
            raise ValueError("timeout must be positive.")
        if poll_interval <= 0:
            raise ValueError("poll_interval must be positive.")

        deadline = time.monotonic() + timeout
        while True:
            history = self.get_activity_history(
                dataset_id=dataset_id,
                activity_history_id=activity_history_id,
            )
            if history.status in TERMINAL_ACTIVITY_STATUSES:
                return history
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                status = history.status.value if history.status else None
                raise TimeoutError(
                    f"Activity history {activity_history_id} did not end within "
                    f"{timeout:g}s (last status: {status})."
                )
            time.sleep(min(poll_interval, remaining))

    def get_activity_history_task_monitoring(
        self,
        activity_history_id: str,
        run_type: Optional[Union[TaskMonitoringRunType, str]] = None,
    ) -> TaskMonitoring:
        """Get task monitoring graph and task summaries for an activity history.

        Args:
            activity_history_id (str): The ID of the activity history.
            run_type (Optional[Union[TaskMonitoringRunType, str]]): BASE or SUB.

        Returns:
            TaskMonitoring: The task monitoring graph and task summaries.
        """
        response = self.request_gql(
            Queries.GET_ACTIVITY_HISTORY_TASK_MONITORING,
            Queries.GET_ACTIVITY_HISTORY_TASK_MONITORING["variables"](
                activity_history_id=activity_history_id,
                run_type=run_type,
            )
        )
        return TaskMonitoring.model_validate(response)

    def get_activity_history_task_detail(
        self,
        activity_history_id: str,
        task_id: str,
        run_type: Optional[Union[TaskMonitoringRunType, str]] = None,
        task_run_index: Optional[int] = None,
    ) -> TaskDetail:
        """Get detail for a task in an activity history."""
        response = self.request_gql(
            Queries.GET_ACTIVITY_HISTORY_TASK_DETAIL,
            Queries.GET_ACTIVITY_HISTORY_TASK_DETAIL["variables"](
                activity_history_id=activity_history_id,
                task_id=task_id,
                run_type=run_type,
                task_run_index=task_run_index,
            )
        )
        return TaskDetail.model_validate(response)

    def get_activity_history_task_rendered_templates(
        self,
        activity_history_id: str,
        task_id: str,
        run_type: Optional[Union[TaskMonitoringRunType, str]] = None,
        task_run_index: Optional[int] = None,
    ) -> TaskRenderedTemplates:
        """Get rendered template fields for a task in an activity history."""
        response = self.request_gql(
            Queries.GET_ACTIVITY_HISTORY_TASK_RENDERED_TEMPLATES,
            Queries.GET_ACTIVITY_HISTORY_TASK_RENDERED_TEMPLATES["variables"](
                activity_history_id=activity_history_id,
                task_id=task_id,
                run_type=run_type,
                task_run_index=task_run_index,
            )
        )
        return TaskRenderedTemplates.model_validate(response)

    def get_activity_history_task_log(
        self,
        activity_history_id: str,
        task_id: str,
        run_type: Optional[Union[TaskMonitoringRunType, str]] = None,
        task_run_index: Optional[int] = None,
        attempt: Optional[int] = None,
        cursor: Optional[str] = None,
        limit_bytes: Optional[int] = None,
    ) -> TaskLogChunk:
        """Get a cursor-based log chunk for a task in an activity history."""
        response = self.request_gql(
            Queries.GET_ACTIVITY_HISTORY_TASK_LOG,
            Queries.GET_ACTIVITY_HISTORY_TASK_LOG["variables"](
                activity_history_id=activity_history_id,
                task_id=task_id,
                run_type=run_type,
                task_run_index=task_run_index,
                attempt=attempt,
                cursor=cursor,
                limit_bytes=limit_bytes,
            )
        )
        return TaskLogChunk.model_validate(response)

    def get_activity_history_task_log_download(
        self,
        activity_history_id: str,
        task_id: str,
        run_type: Optional[Union[TaskMonitoringRunType, str]] = None,
        task_run_index: Optional[int] = None,
        attempt: Optional[int] = None,
    ) -> TaskLogDownload:
        """Get the last 1,000 log lines for a task in an activity history."""
        response = self.request_gql(
            Queries.GET_ACTIVITY_HISTORY_TASK_LOG_DOWNLOAD,
            Queries.GET_ACTIVITY_HISTORY_TASK_LOG_DOWNLOAD["variables"](
                activity_history_id=activity_history_id,
                task_id=task_id,
                run_type=run_type,
                task_run_index=task_run_index,
                attempt=attempt,
            )
        )
        return TaskLogDownload.model_validate(response)

    def update_activity(
        self,
        activity_id: str,
        activity_type: Union[
            str,
            UndefinedType
        ] = Undefined,
        name: Union[
            str,
            UndefinedType
        ] = Undefined,
        dataset_id: Union[
            UndefinedType,
            str
        ] = Undefined,
        description: Union[
            UndefinedType,
            str
        ] = Undefined,
        progress_schema: Union[
            UndefinedType,
            List[ActivitySchema]
        ] = Undefined,
        parameter_schema: Union[
            UndefinedType,
            List[ActivitySchema]
        ] = Undefined,
        settings: Union[
            UndefinedType,
            dict
        ] = Undefined,
        meta: Union[
            UndefinedType,
            dict
        ] = Undefined,
    ) -> Activity:
        """Update an activity.
        
        Args:
            activity_id (str): The ID of the activity to update.
            activity_type (Optional[str]): The type of the activity to update.
            name (Optional[str]): The name of the activity to update.
            dataset_id (Optional[str]): The ID of the dataset to update the activity for.
            description (Optional[str]): The description of the activity to update.
            progress_schema (Optional[List[ActivitySchema]]): The progress schema of the activity to update.
            parameter_schema (Optional[List[ActivitySchema]]): The parameter schema of the activity to update.
            settings (Optional[dict]): The settings of the activity to update.
            meta (Optional[dict]): The meta of the activity to update.
        
        Returns:
            Activity: The updated activity object.
        """
        response = self.request_gql(
            Queries.UPDATE_ACTIVITY,
            Queries.UPDATE_ACTIVITY["variables"](
                activity_id=activity_id,
                activity_type=activity_type,
                name=name,
                dataset_id=dataset_id,
                description=description,
                progress_schema=progress_schema,
                parameter_schema=parameter_schema,
                settings=settings,
                meta=meta,
            )
        )
        return Activity.model_validate(response)

    def delete_activity(
        self,
        activity_id: str,
    ) -> bool:
        """Delete an activity.
        
        Args:
            activity_id (str): The ID of the activity to delete.
        
        Returns:
            bool: True if the activity was deleted, False otherwise.
        """
        response = self.request_gql(
            Queries.DELETE_ACTIVITY,
            Queries.DELETE_ACTIVITY["variables"](
                activity_id=activity_id,
            )
        )
        return response

    def start_activity(
        self,
        dataset_id: str,
        activity_id: Optional[str] = None,
        activity_type: Optional[str] = None,
        parameters: Union[
            UndefinedType,
            dict
        ] = Undefined,
        progress: Union[
            UndefinedType,
            dict
        ] = Undefined,
        meta: Union[
            UndefinedType,
            dict
        ] = Undefined,
    ) -> ActivityHistory:
        """Start an activity.
        
        Args:
            dataset_id (str): The ID of the dataset to start the activity for.
            activity_id (Optional[str]): The ID of the activity to start.
            activity_type (Optional[str]): The type of the activity to start.
            parameters (Optional[dict]): The parameters for the activity.
            progress (Optional[dict]): The progress for the activity.
            meta (Optional[dict]): The meta for the activity.
        
        Returns:
            ActivityHistory: The activity history object.
        """
        response = self.request_gql(
            Queries.START_ACTIVITY,
            Queries.START_ACTIVITY["variables"](
                dataset_id=dataset_id,
                activity_id=activity_id,
                activity_type=activity_type,
                parameters=parameters,
                progress=progress,
                meta=meta,
            )
        )
        return ActivityHistory.model_validate(response)

    def update_activity_history_status(
        self,
        activity_history_id: str,
        status: ActivityStatus,
        meta: Union[
            UndefinedType,
            dict
        ] = Undefined,
    ) -> ActivityHistory:
        """Update the status of an activity history.
        
        Args:
            activity_history_id (str): The ID of the activity history to update.
            status (ActivityStatus): The new status for the activity history.
            meta (Optional[dict]): The meta for the activity history.
        
        Returns:
            ActivityHistory: The updated activity history object.
        """
        response = self.request_gql(
            Queries.UPDATE_ACTIVITY_HISTORY,
            Queries.UPDATE_ACTIVITY_HISTORY["variables"](
                activity_history_id=activity_history_id,
                status=status,
                meta=meta,
            )
        )
        return ActivityHistory.model_validate(response)

    def update_activity_history_progress(
        self,
        activity_history_id: str,
        progress: Union[
            UndefinedType,
            dict
        ] = Undefined,
        meta: Union[
            UndefinedType,
            dict
        ] = Undefined,
    ) -> ActivityHistory:
        """Update the progress of an activity history.
        
        Args:
            activity_history_id (str): The ID of the activity history to update.
            progress (Optional[dict]): The new progress for the activity history.
            meta (Optional[dict]): The meta for the activity history.
        
        Returns:
            ActivityHistory: The updated activity history object.
        """
        response = self.request_gql(
            Queries.UPDATE_ACTIVITY_HISTORY,
            Queries.UPDATE_ACTIVITY_HISTORY["variables"](
                activity_history_id=activity_history_id,
                progress=progress,
                meta=meta,
            )
        )
        return ActivityHistory.model_validate(response)
