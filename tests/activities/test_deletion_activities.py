"""Delete functions start deletion activities (2.0.0) and the helpers around them."""
from unittest.mock import Mock, patch

import pytest

from spb_onprem import (
    ActivityService,
    ContentService,
    DeletionActivityType,
    DiagnosisService,
    ModelService,
    ReportService,
    SliceService,
)
from spb_onprem.activities.entities import (
    TERMINAL_ACTIVITY_STATUSES,
    ActivityHistory,
    ActivityStatus,
)
from spb_onprem.activities.queries import Queries as ActivityQueries
from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import BadParameterError, NotFoundError, UnknownError


def _history(status="PENDING", history_id="history-1"):
    return {"id": history_id, "jobId": "job-1", "datasetId": "dataset-1", "status": status}


def _service(cls):
    service = cls()
    service.request_gql = Mock(return_value=_history())
    return service


ENTITY_CASES = [
    (ModelService, "delete_model", "model_id", "DELETE_MODEL"),
    (DiagnosisService, "delete_diagnosis", "diagnosis_id", "DELETE_DIAGNOSIS"),
    (ReportService, "delete_analytics_report", "report_id", "DELETE_ANALYTICS_REPORT"),
]


class TestEntityDeletion:
    @pytest.mark.parametrize("cls,method,id_key,job_type", ENTITY_CASES)
    def test_starts_activity_with_id_only(self, cls, method, id_key, job_type):
        service = _service(cls)

        result = getattr(service, method)(dataset_id="dataset-1", **{id_key: "entity-1"})

        assert isinstance(result, ActivityHistory)
        assert result.id == "history-1"
        assert result
        service.request_gql.assert_called_once_with(
            ActivityQueries.START_ACTIVITY,
            {
                "datasetId": "dataset-1",
                "jobType": job_type,
                # The job definition only allows the entity id; dataset_id comes from datasetId.
                "parameters": {id_key: "entity-1"},
            },
        )

    @pytest.mark.parametrize("cls,method,id_key,job_type", ENTITY_CASES)
    def test_positional_call_still_works(self, cls, method, id_key, job_type):
        service = _service(cls)

        getattr(service, method)("dataset-1", "entity-1")

        assert service.request_gql.call_args[0][1]["parameters"] == {id_key: "entity-1"}

    @pytest.mark.parametrize("cls,method,id_key,job_type", ENTITY_CASES)
    @pytest.mark.parametrize("missing", ["dataset_id", "entity"])
    @pytest.mark.parametrize("value", [None, ""])
    def test_missing_ids_are_refused(self, cls, method, id_key, job_type, missing, value):
        service = _service(cls)
        kwargs = {"dataset_id": "dataset-1", id_key: "entity-1"}
        kwargs["dataset_id" if missing == "dataset_id" else id_key] = value

        with pytest.raises(BadParameterError, match="is required"):
            getattr(service, method)(**kwargs)
        service.request_gql.assert_not_called()

    @pytest.mark.parametrize("cls,method,id_key,job_type", ENTITY_CASES)
    def test_awaiting_approval_is_returned(self, cls, method, id_key, job_type):
        service = _service(cls)
        service.request_gql.return_value = _history("AWAITING_APPROVAL")

        result = getattr(service, method)(dataset_id="dataset-1", **{id_key: "entity-1"})

        assert result.status == ActivityStatus.AWAITING_APPROVAL

    def test_server_refusal_is_raised(self):
        service = _service(ModelService)
        service.request_gql.side_effect = UnknownError("GraphQL errors: [CONFLICT] has a deployment")

        with pytest.raises(UnknownError, match="CONFLICT"):
            service.delete_model(dataset_id="dataset-1", model_id="model-1")


class TestSliceDeletion:
    def test_delete_slice_starts_activity(self):
        service = _service(SliceService)

        result = service.delete_slice(dataset_id="dataset-1", slice_id="slice-1")

        assert isinstance(result, ActivityHistory)
        service.request_gql.assert_called_once_with(
            ActivityQueries.START_ACTIVITY,
            {
                "datasetId": "dataset-1",
                "jobType": "DELETE_SLICE",
                "parameters": {
                    "dataset_id": "dataset-1",
                    "slice_filter": {"must": {"idIn": ["slice-1"]}},
                },
            },
        )

    def test_no_sub_dag_id_is_sent(self):
        service = _service(SliceService)

        service.delete_slice("dataset-1", "slice-1")

        assert "sub_dag_id" not in service.request_gql.call_args[0][1]["parameters"]

    @pytest.mark.parametrize("kwargs", [
        {"dataset_id": None, "slice_id": "slice-1"},
        {"dataset_id": "dataset-1", "slice_id": None},
        {"dataset_id": "dataset-1", "slice_id": ""},
    ])
    def test_missing_ids_are_refused(self, kwargs):
        service = _service(SliceService)

        with pytest.raises(BadParameterError, match="is required"):
            service.delete_slice(**kwargs)
        service.request_gql.assert_not_called()


class TestDeleteContent:
    def test_delete_content_stays_direct(self):
        """A content is not an entity: delete_content still calls deleteContent."""
        service = ContentService()
        service.request_gql = Mock(return_value=True)

        assert service.delete_content("content-1") is True
        query = service.request_gql.call_args.kwargs["query"]
        assert query["name"] == "deleteContent"

    def test_delete_content_failure_raises(self):
        service = ContentService()
        service.request_gql = Mock(side_effect=UnknownError("GraphQL errors: [STORAGE_TRANSIENT] busy"))

        with pytest.raises(UnknownError, match="STORAGE_TRANSIENT"):
            service.delete_content("content-1")


class TestActivityStatus:
    @pytest.mark.parametrize("value", [
        "AWAITING_APPROVAL", "PENDING", "RUNNING", "SUCCESS", "FAILED", "CANCELED", "REJECTED",
    ])
    def test_every_server_status_validates(self, value):
        history = ActivityHistory.model_validate(_history(value))
        assert history.status.value == value

    def test_cancelled_is_an_alias_of_canceled(self):
        assert ActivityStatus.CANCELLED is ActivityStatus.CANCELED
        assert ActivityStatus("CANCELLED") is ActivityStatus.CANCELED
        assert ActivityHistory.model_validate(_history("CANCELLED")).status is ActivityStatus.CANCELED
        assert ActivityStatus.CANCELLED.value == "CANCELED"

    def test_terminal_statuses(self):
        assert TERMINAL_ACTIVITY_STATUSES == {
            ActivityStatus.SUCCESS, ActivityStatus.FAILED, ActivityStatus.CANCELED, ActivityStatus.REJECTED,
        }
        assert not ActivityStatus.AWAITING_APPROVAL.is_terminal
        assert not ActivityStatus.PENDING.is_terminal
        assert ActivityStatus.REJECTED.is_terminal

    def test_deletion_activity_types(self):
        assert {item.value for item in DeletionActivityType} == {
            "DELETE_MODEL", "DELETE_DIAGNOSIS", "DELETE_ANALYTICS_REPORT", "DELETE_DATASET",
            "DELETE_DATA", "DELETE_SLICE", "REMOVE_DATA_FROM_SLICE",
        }


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


class TestWaitForActivity:
    def _service(self, statuses):
        service = ActivityService()
        service.request_gql = Mock(side_effect=[_history(status) for status in statuses])
        return service

    @pytest.mark.parametrize("end", ["SUCCESS", "FAILED", "CANCELED", "REJECTED"])
    def test_returns_at_an_end_status(self, end):
        service = self._service(["PENDING", "RUNNING", end])
        clock = FakeClock()

        with patch("spb_onprem.activities.service.time", clock):
            history = service.wait_for_activity("history-1", timeout=60, poll_interval=2)

        assert history.status.value == end
        assert service.request_gql.call_count == 3
        assert clock.sleeps == [2, 2]
        query, variables = service.request_gql.call_args[0]
        assert query is ActivityQueries.GET_ACTIVITY_HISTORY
        assert variables == {"dataset_id": None, "job_history_id": "history-1"}

    def test_passes_dataset_id(self):
        service = self._service(["SUCCESS"])

        service.wait_for_activity("history-1", dataset_id="dataset-1")

        assert service.request_gql.call_args[0][1] == {"dataset_id": "dataset-1", "job_history_id": "history-1"}

    def test_awaiting_approval_is_not_an_end(self):
        service = self._service(["AWAITING_APPROVAL"] * 10)
        clock = FakeClock()

        with patch("spb_onprem.activities.service.time", clock):
            with pytest.raises(TimeoutError, match="AWAITING_APPROVAL"):
                service.wait_for_activity("history-1", timeout=10, poll_interval=4)

        # Polls at 0, 4, 8 and once more at the deadline (10).
        assert service.request_gql.call_count == 4
        assert clock.sleeps == [4, 4, 2]

    def test_timeout_message_has_last_status(self):
        service = self._service(["PENDING", "RUNNING", "RUNNING"])
        clock = FakeClock()

        with patch("spb_onprem.activities.service.time", clock):
            with pytest.raises(TimeoutError, match=r"history-1.*last status: RUNNING"):
                service.wait_for_activity("history-1", timeout=2, poll_interval=1)

    @pytest.mark.parametrize("kwargs,error", [
        ({"activity_history_id": None}, BadParameterError),
        ({"activity_history_id": ""}, BadParameterError),
        ({"activity_history_id": "h", "timeout": 0}, ValueError),
        ({"activity_history_id": "h", "poll_interval": 0}, ValueError),
    ])
    def test_bad_arguments(self, kwargs, error):
        service = self._service([])

        with pytest.raises(error):
            service.wait_for_activity(**kwargs)
        service.request_gql.assert_not_called()


class _FakeResponse:
    status_code = 200
    elapsed = None

    def __init__(self, body):
        self._body = body

    def raise_for_status(self):
        return None

    def json(self):
        return self._body


class TestGraphqlErrorCode:
    def _request(self, errors):
        service = BaseService()
        session = Mock()
        session.post.return_value = _FakeResponse({"errors": errors, "data": None})
        with patch.object(BaseService, "requests_retry_session", return_value=session):
            return service.request_gql({"name": "deleteContent", "query": "mutation { x }"}, {})

    def test_top_level_not_found(self):
        with pytest.raises(NotFoundError, match="gone"):
            self._request([{"message": "gone", "code": "NOT_FOUND"}])

    def test_extensions_not_found(self):
        with pytest.raises(NotFoundError, match="gone"):
            self._request([{"message": "gone", "extensions": {"code": "NOT_FOUND"}}])

    def test_top_level_code_wins(self):
        with pytest.raises(UnknownError, match=r"\[STORAGE_PERMANENT\] denied"):
            self._request([{"message": "denied", "code": "STORAGE_PERMANENT",
                            "extensions": {"code": "NOT_FOUND"}}])

    def test_extensions_code_in_message(self):
        with pytest.raises(UnknownError, match=r"\[STORAGE_TRANSIENT\] busy"):
            self._request([{"message": "busy", "extensions": {"code": "STORAGE_TRANSIENT"}}])

    def test_error_without_code(self):
        """An error with no code used to fail with KeyError('code')."""
        with pytest.raises(UnknownError, match="GraphQL errors: bad input"):
            self._request([{"message": "bad input"}])
