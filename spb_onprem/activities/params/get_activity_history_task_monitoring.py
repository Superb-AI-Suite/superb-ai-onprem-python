from typing import Dict, Optional, Union

from spb_onprem.activities.entities.task_monitoring import TaskMonitoringRunType


def _run_type_value(
    run_type: Optional[Union[TaskMonitoringRunType, str]],
) -> Optional[str]:
    if run_type is None:
        return None
    if isinstance(run_type, TaskMonitoringRunType):
        return run_type.value
    return run_type


def _task_input_params(
    activity_history_id: str,
    task_id: str,
    run_type: Optional[Union[TaskMonitoringRunType, str]] = None,
    task_run_index: Optional[int] = None,
) -> Dict[str, dict]:
    input_params = {
        "jobHistoryId": activity_history_id,
        "taskId": task_id,
    }

    run_type_value = _run_type_value(run_type)
    if run_type_value is not None:
        input_params["runType"] = run_type_value
    if task_run_index is not None:
        input_params["taskRunIndex"] = task_run_index

    return {
        "input": input_params,
    }


def get_activity_history_task_monitoring_params(
    activity_history_id: str,
    run_type: Optional[Union[TaskMonitoringRunType, str]] = None,
) -> Dict[str, dict]:
    """Get parameters for activity history task monitoring.

    Args:
        activity_history_id (str): The activity history ID.
        run_type (Optional[Union[TaskMonitoringRunType, str]]): BASE or SUB.

    Returns:
        Dict[str, dict]: The GraphQL variables for the query.
    """
    input_params = {
        "jobHistoryId": activity_history_id,
    }

    run_type_value = _run_type_value(run_type)
    if run_type_value is not None:
        input_params["runType"] = run_type_value

    return {
        "input": input_params,
    }


def get_activity_history_task_detail_params(
    activity_history_id: str,
    task_id: str,
    run_type: Optional[Union[TaskMonitoringRunType, str]] = None,
    task_run_index: Optional[int] = None,
) -> Dict[str, dict]:
    """Get parameters for activity history task detail."""
    return _task_input_params(
        activity_history_id=activity_history_id,
        task_id=task_id,
        run_type=run_type,
        task_run_index=task_run_index,
    )


def get_activity_history_task_rendered_templates_params(
    activity_history_id: str,
    task_id: str,
    run_type: Optional[Union[TaskMonitoringRunType, str]] = None,
    task_run_index: Optional[int] = None,
) -> Dict[str, dict]:
    """Get parameters for activity history task rendered templates."""
    return _task_input_params(
        activity_history_id=activity_history_id,
        task_id=task_id,
        run_type=run_type,
        task_run_index=task_run_index,
    )


def get_activity_history_task_log_params(
    activity_history_id: str,
    task_id: str,
    run_type: Optional[Union[TaskMonitoringRunType, str]] = None,
    task_run_index: Optional[int] = None,
    attempt: Optional[int] = None,
    cursor: Optional[str] = None,
    limit_bytes: Optional[int] = None,
) -> Dict[str, dict]:
    """Get parameters for an activity history task log chunk."""
    variables = _task_input_params(
        activity_history_id=activity_history_id,
        task_id=task_id,
        run_type=run_type,
        task_run_index=task_run_index,
    )
    input_params = variables["input"]

    if attempt is not None:
        input_params["attempt"] = attempt
    if cursor is not None:
        input_params["cursor"] = cursor
    if limit_bytes is not None:
        input_params["limitBytes"] = limit_bytes

    return variables


def get_activity_history_task_log_download_params(
    activity_history_id: str,
    task_id: str,
    run_type: Optional[Union[TaskMonitoringRunType, str]] = None,
    task_run_index: Optional[int] = None,
    attempt: Optional[int] = None,
) -> Dict[str, dict]:
    """Get parameters for activity history task log download."""
    variables = _task_input_params(
        activity_history_id=activity_history_id,
        task_id=task_id,
        run_type=run_type,
        task_run_index=task_run_index,
    )
    if attempt is not None:
        variables["input"]["attempt"] = attempt

    return variables
