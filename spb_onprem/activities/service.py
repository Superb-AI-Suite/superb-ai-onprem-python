import time
from typing import Optional, Union, List, Tuple

from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import BadParameterError, BadResponseError
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

        Activity definitions are platform-wide: most have no dataset, and
        ``startJob(datasetId)`` decides where a run happens. The platform's
        ``jobs`` query has no dataset argument, so ``dataset_id`` does not
        filter (kept for compatibility). To list only the definitions made for
        one dataset, pass ``ActivitiesFilter(must_filter=
        ActivitiesFilterOptions(dataset_id_in=[...]))``; that leaves out the
        platform-wide ones.

        Args:
            dataset_id (str): Not used to filter (see above).
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

    def get_activity_histories(
        self,
        dataset_id: str,
        *,
        activity_id: Optional[Union[str, List[str]]] = None,
        status: Optional[Union[ActivityStatus, str, List[Union[ActivityStatus, str]]]] = None,
        requester: Optional[Union[str, List[str]]] = None,
        slice_id: Optional[Union[str, List[str]]] = None,
        cursor: Optional[str] = None,
        length: int = 10,
        oldest_first: bool = False,
    ) -> Tuple[List[ActivityHistory], Optional[str], int]:
        """One page of the runs (activity histories) of a dataset.

        Newest first by ``createdAt`` (``oldest_first=True`` for the other
        way). Every filter is optional; a filter takes one value or a list of
        values (any of them matches), and the filters are combined with AND.
        The platform has no time-range filter.

        A user who is not an admin of the dataset (Owner, WorkspaceAdmin,
        DATASET-ADMIN) sees only their own runs; the platform replaces
        ``requester`` with that user.

        Every run returned must belong to ``dataset_id``. If the platform
        returns a run of another dataset, nothing is returned and
        ``BadResponseError`` is raised.

        The cursor is an offset. A run started while you page newest first
        pushes the others down, so a run can show up on two pages; use
        ``oldest_first=True`` to page through everything. When the number of
        runs is a multiple of ``length``, the last page is empty.

        Args:
            dataset_id (str): The dataset whose runs to list. Required.
            activity_id (Optional[Union[str, List[str]]]): Runs of these
                activities (``Activity.id``, i.e. ``ActivityHistory.activity_id``).
            status (Optional[Union[ActivityStatus, str, List]]): Runs in these
                statuses, e.g. ``ActivityStatus.FAILED`` or ``"RUNNING"``.
            requester (Optional[Union[str, List[str]]]): Runs started by these
                users (email, as in ``ActivityHistory.created_by``).
            slice_id (Optional[Union[str, List[str]]]): Runs started on these
                slices (``start_activity(slice_id=...)``). A slice given only
                inside ``parameters`` does not count.
            cursor (Optional[str]): ``next_cursor`` of the previous page.
            length (int): Runs per page, 1 to 50. Defaults to 10.
            oldest_first (bool): Oldest first instead of newest first.

        Raises:
            BadParameterError: A missing ``dataset_id``, ``length`` out of
                range, an empty filter list, or an unknown status.
            BadResponseError: The platform returned a run of another dataset.

        Returns:
            Tuple[List[ActivityHistory], Optional[str], int]: The runs of this
            page, the cursor of the next page (None on the last page), and the
            number of runs that match the filters.
        """
        response = self.request_gql(
            Queries.GET_ACTIVITY_HISTORIES,
            Queries.GET_ACTIVITY_HISTORIES["variables"](
                dataset_id=dataset_id,
                activity_id=activity_id,
                status=status,
                requester=requester,
                slice_id=slice_id,
                cursor=cursor,
                length=length,
                oldest_first=oldest_first,
            )
        )
        response = response if isinstance(response, dict) else {}
        histories = [
            ActivityHistory.model_validate(item)
            for item in response.get("jobHistories") or []
        ]
        foreign = [history for history in histories if history.dataset_id != dataset_id]
        if foreign:
            # The IDs are left out of the message: they are runs this call was not asked for.
            raise BadResponseError(
                f"jobHistories returned {len(foreign)} run(s) of another dataset "
                f"for dataset {dataset_id}; nothing is returned."
            )
        return (
            histories,
            response.get("next"),
            response.get("totalCount") or 0,
        )

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
        slice_id: Optional[str] = None,
    ) -> ActivityHistory:
        """Start an activity.
        
        Args:
            dataset_id (str): The ID of the dataset to start the activity for.
            activity_id (Optional[str]): The ID of the activity to start.
            activity_type (Optional[str]): The type of the activity to start.
            parameters (Optional[dict]): The parameters for the activity.
            progress (Optional[dict]): The progress for the activity.
            meta (Optional[dict]): The meta for the activity.
            slice_id (Optional[str]): The slice of a slice-scoped activity.
        
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
                slice_id=slice_id,
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
