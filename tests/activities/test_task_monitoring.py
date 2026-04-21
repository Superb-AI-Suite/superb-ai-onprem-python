from unittest.mock import MagicMock

import pytest

from spb_onprem.activities.entities import (
    RenderedTemplateValueType,
    TaskDataAvailability,
    TaskDetail,
    TaskKind,
    TaskLogChunk,
    TaskLogDownload,
    TaskMonitoring,
    TaskMonitoringRunState,
    TaskMonitoringRunType,
    TaskRenderedTemplates,
    TaskState,
)
from spb_onprem.activities.params import (
    get_activity_history_task_log_params,
    get_activity_history_task_monitoring_params,
)
from spb_onprem.activities.service import ActivityService


@pytest.fixture
def activity_service():
    return ActivityService()


class TestActivityHistoryTaskMonitoring:
    def test_get_activity_history_task_monitoring(self, activity_service):
        mock_response = {
            "runType": "BASE",
            "runId": "job_test",
            "available": True,
            "runState": "SUCCESS",
            "rawRunState": "success",
            "linkedRun": {
                "runType": "SUB",
                "runId": "sub_job_test",
            },
            "nodes": [
                {
                    "id": "prepare_data",
                    "taskId": "prepare_data",
                    "label": "prepare_data",
                    "kind": "TASK",
                    "state": "SUCCESS",
                    "instanceCount": 1,
                    "instances": [
                        {
                            "id": "prepare_data",
                            "taskId": "prepare_data",
                            "label": "prepare_data",
                            "kind": "TASK",
                            "state": "SUCCESS",
                            "rawState": "success",
                            "durationSeconds": 1.25,
                            "startedAt": "2026-04-14T03:29:59.284079Z",
                            "endedAt": "2026-04-14T03:30:00.534079Z",
                            "attempt": 1,
                            "taskRunIndex": None,
                        }
                    ],
                },
                {
                    "id": "trigger_and_wait_sub_dag",
                    "taskId": "trigger_and_wait_sub_dag",
                    "label": "trigger_and_wait_sub_dag",
                    "kind": "DAG_RUN",
                    "state": "FAILED",
                    "instanceCount": 1,
                    "instances": [
                        {
                            "id": "trigger_and_wait_sub_dag",
                            "taskId": "trigger_and_wait_sub_dag",
                            "label": "trigger_and_wait_sub_dag",
                            "kind": "DAG_RUN",
                            "state": "FAILED",
                            "rawState": "failed",
                        }
                    ],
                },
            ],
            "edges": [
                {
                    "id": "prepare_data->trigger_and_wait_sub_dag",
                    "source": "prepare_data",
                    "target": "trigger_and_wait_sub_dag",
                }
            ],
        }
        activity_service.request_gql = MagicMock(return_value=mock_response)

        monitoring = activity_service.get_activity_history_task_monitoring(
            activity_history_id="history_id",
            run_type=TaskMonitoringRunType.BASE,
        )

        assert isinstance(monitoring, TaskMonitoring)
        assert monitoring.run_type == TaskMonitoringRunType.BASE
        assert monitoring.run_id == "job_test"
        assert monitoring.available is True
        assert monitoring.run_state == TaskMonitoringRunState.SUCCESS
        assert monitoring.raw_run_state == "success"
        assert monitoring.linked_run.run_type == TaskMonitoringRunType.SUB
        assert monitoring.linked_run.run_id == "sub_job_test"
        assert len(monitoring.nodes) == 2
        assert monitoring.nodes[0].instance_count == 1
        assert monitoring.nodes[0].instances[0].task_id == "prepare_data"
        assert monitoring.nodes[0].instances[0].kind == TaskKind.TASK
        assert monitoring.nodes[0].instances[0].state == TaskState.SUCCESS
        assert monitoring.nodes[0].instances[0].duration_seconds == 1.25
        assert monitoring.nodes[1].instances[0].kind == TaskKind.DAG_RUN
        assert monitoring.nodes[1].instances[0].state == TaskState.FAILED
        assert len(monitoring.edges) == 1
        assert monitoring.edges[0].source == "prepare_data"

        _, variables = activity_service.request_gql.call_args.args
        assert variables == {
            "input": {
                "jobHistoryId": "history_id",
                "runType": "BASE",
            }
        }

    def test_get_activity_history_task_monitoring_params_omit_run_type(self):
        variables = get_activity_history_task_monitoring_params(
            activity_history_id="history_id",
        )

        assert variables == {
            "input": {
                "jobHistoryId": "history_id",
            }
        }

    def test_get_activity_history_task_detail(self, activity_service):
        mock_response = {
            "availability": "AVAILABLE",
            "taskId": "prepare_data",
            "taskRunIndex": None,
            "label": "prepare_data",
            "state": "SUCCESS",
            "rawState": "success",
            "operator": "KubernetesPodOperator",
            "triggerRule": "none_failed_min_one_success",
            "startedAt": "2026-04-14T03:29:59.284079Z",
            "endedAt": "2026-04-14T03:30:29.873192Z",
            "durationSeconds": 30.589113,
            "attempt": 1,
            "maxAttempts": 1,
            "runtime": {
                "queue": "default",
                "pool": "default_pool",
                "poolSlots": 1,
                "hostname": "airflow-worker",
                "unixname": "airflow",
                "pid": 505,
                "priorityWeight": 8,
                "queuedAt": "2026-04-14T03:29:59.175627Z",
                "scheduledAt": "2026-04-14T03:29:59.156145Z",
                "kubernetes": {
                    "podName": "prepare-data-abc",
                    "namespace": "airflow",
                    "image": "registry/prepare:latest",
                    "containerName": "base",
                    "nodeName": "node-1",
                    "podPhase": "Succeeded",
                },
            },
        }
        activity_service.request_gql = MagicMock(return_value=mock_response)

        detail = activity_service.get_activity_history_task_detail(
            activity_history_id="history_id",
            run_type=TaskMonitoringRunType.BASE,
            task_id="prepare_data",
        )

        assert isinstance(detail, TaskDetail)
        assert detail.availability == TaskDataAvailability.AVAILABLE
        assert detail.task_id == "prepare_data"
        assert detail.state == TaskState.SUCCESS
        assert detail.operator == "KubernetesPodOperator"
        assert detail.runtime.queue == "default"
        assert detail.runtime.kubernetes.pod_name == "prepare-data-abc"

        _, variables = activity_service.request_gql.call_args.args
        assert variables == {
            "input": {
                "jobHistoryId": "history_id",
                "taskId": "prepare_data",
                "runType": "BASE",
            }
        }

    def test_get_activity_history_task_rendered_templates(self, activity_service):
        mock_response = {
            "availability": "AVAILABLE",
            "taskId": "prepare_data",
            "taskRunIndex": None,
            "sections": [
                {
                    "key": "image",
                    "value": "registry/prepare:latest",
                    "valueType": "TEXT",
                },
                {
                    "key": "arguments",
                    "value": ["--dataset-id", "dataset_1"],
                    "valueType": "LIST",
                },
            ],
        }
        activity_service.request_gql = MagicMock(return_value=mock_response)

        rendered_templates = (
            activity_service.get_activity_history_task_rendered_templates(
                activity_history_id="history_id",
                task_id="prepare_data",
            )
        )

        assert isinstance(rendered_templates, TaskRenderedTemplates)
        assert rendered_templates.availability == TaskDataAvailability.AVAILABLE
        assert len(rendered_templates.sections) == 2
        assert rendered_templates.sections[0].value_type == RenderedTemplateValueType.TEXT
        assert rendered_templates.sections[1].value == ["--dataset-id", "dataset_1"]

    def test_get_activity_history_task_log(self, activity_service):
        mock_response = {
            "availability": "AVAILABLE",
            "taskId": "prepare_data",
            "taskRunIndex": 2,
            "attempt": 1,
            "content": "line 1\nline 2\n",
            "nextCursor": "cursor-2",
            "hasMore": True,
            "isComplete": False,
            "metadata": {
                "lineCount": 2,
                "sizeBytes": 14,
                "startedAt": "2026-04-14T03:29:59.284079Z",
            },
        }
        activity_service.request_gql = MagicMock(return_value=mock_response)

        log_chunk = activity_service.get_activity_history_task_log(
            activity_history_id="history_id",
            run_type="SUB",
            task_id="prepare_data",
            task_run_index=2,
            attempt=1,
            cursor="cursor-1",
            limit_bytes=65536,
        )

        assert isinstance(log_chunk, TaskLogChunk)
        assert log_chunk.availability == TaskDataAvailability.AVAILABLE
        assert log_chunk.task_run_index == 2
        assert log_chunk.next_cursor == "cursor-2"
        assert log_chunk.has_more is True
        assert log_chunk.is_complete is False
        assert log_chunk.metadata.line_count == 2

        _, variables = activity_service.request_gql.call_args.args
        assert variables == {
            "input": {
                "jobHistoryId": "history_id",
                "taskId": "prepare_data",
                "runType": "SUB",
                "taskRunIndex": 2,
                "attempt": 1,
                "cursor": "cursor-1",
                "limitBytes": 65536,
            }
        }

    def test_get_activity_history_task_log_download(self, activity_service):
        mock_response = {
            "availability": "AVAILABLE",
            "taskId": "prepare_data",
            "taskRunIndex": None,
            "attempt": 1,
            "content": "last line\n",
            "downloadFilename": "prepare_data_attempt_1_last_1000_lines.log",
            "lineCount": 1,
            "isTail": True,
        }
        activity_service.request_gql = MagicMock(return_value=mock_response)

        download = activity_service.get_activity_history_task_log_download(
            activity_history_id="history_id",
            task_id="prepare_data",
            attempt=1,
        )

        assert isinstance(download, TaskLogDownload)
        assert download.availability == TaskDataAvailability.AVAILABLE
        assert download.download_filename == (
            "prepare_data_attempt_1_last_1000_lines.log"
        )
        assert download.line_count == 1
        assert download.is_tail is True

    def test_get_activity_history_task_log_params_omit_optionals(self):
        variables = get_activity_history_task_log_params(
            activity_history_id="history_id",
            task_id="prepare_data",
        )

        assert variables == {
            "input": {
                "jobHistoryId": "history_id",
                "taskId": "prepare_data",
            }
        }
