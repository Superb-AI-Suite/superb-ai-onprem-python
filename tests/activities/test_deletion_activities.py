"""Delete functions start deletion activities (2.0.0) and the helpers around them."""
import re
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
from spb_onprem.data.params import DataFilterOptions, DataListFilter
from spb_onprem.diagnoses.params import DiagnosisFilter, DiagnosisFilterOptions
from spb_onprem.exceptions import BadDeletionTargetError, BadParameterError, NotFoundError, UnknownError
from spb_onprem.models.params import ModelFilter, ModelFilterOptions
from spb_onprem.reports.params.analytics_reports import AnalyticsReportsFilter, AnalyticsReportsFilterOptions
from spb_onprem.slices.params import SlicesFilter, SlicesFilterOptions


def _history(status="PENDING", history_id="history-1"):
    return {"id": history_id, "jobId": "job-1", "datasetId": "dataset-1", "status": status}


def _service(cls):
    service = cls()
    service.request_gql = Mock(return_value=_history())
    return service


# (service, plural, singular, ids arg, filter arg, singular id arg, parameter key, job type, filter model)
ENTITY_CASES = [
    (ModelService, "delete_models", "delete_model", "model_ids", "model_filter", "model_id",
     "model_filter", "DELETE_MODEL", ModelFilter(must_filter=ModelFilterOptions(name_contains="old"))),
    (DiagnosisService, "delete_diagnoses", "delete_diagnosis", "diagnosis_ids", "diagnosis_filter",
     "diagnosis_id", "diagnosis_filter", "DELETE_DIAGNOSIS",
     DiagnosisFilter(must=DiagnosisFilterOptions(name_contains="old"))),
    (ReportService, "delete_analytics_reports", "delete_analytics_report", "report_ids", "report_filter",
     "report_id", "analytics_report_filter", "DELETE_ANALYTICS_REPORT",
     AnalyticsReportsFilter(must_filter=AnalyticsReportsFilterOptions(title_contains="old"))),
    (SliceService, "delete_slices", "delete_slice", "slice_ids", "slice_filter", "slice_id",
     "slice_filter", "DELETE_SLICE", SlicesFilter(must_filter=SlicesFilterOptions(name_contains="old"))),
]
IDS = ["01ARZ3NDEKTSV4RRFFQ69G5FAV", "01ARZ3NDEKTSV4RRFFQ69G5FAW"]


def _sent(service):
    service.request_gql.assert_called_once()
    query, variables = service.request_gql.call_args[0]
    assert query is ActivityQueries.START_ACTIVITY
    return variables


@pytest.mark.parametrize(
    "cls,plural,singular,ids_arg,filter_arg,id_arg,param_key,job_type,model_filter", ENTITY_CASES
)
class TestEntityDeletion:
    def test_ids_start_one_activity(self, cls, plural, singular, ids_arg, filter_arg, id_arg,
                                    param_key, job_type, model_filter):
        service = _service(cls)

        result = getattr(service, plural)(dataset_id="dataset-1", **{ids_arg: IDS})

        assert isinstance(result, ActivityHistory)
        assert result.id == "history-1"
        assert _sent(service) == {
            "datasetId": "dataset-1",
            "jobType": job_type,
            "parameters": {"dataset_id": "dataset-1", param_key: {"must": {"idIn": IDS}}},
        }

    def test_positional_ids(self, cls, plural, singular, ids_arg, filter_arg, id_arg,
                            param_key, job_type, model_filter):
        service = _service(cls)

        getattr(service, plural)("dataset-1", IDS)

        assert _sent(service)["parameters"][param_key] == {"must": {"idIn": IDS}}

    def test_filter_model_is_sent_in_camel_case(self, cls, plural, singular, ids_arg, filter_arg, id_arg,
                                                param_key, job_type, model_filter):
        service = _service(cls)

        getattr(service, plural)(dataset_id="dataset-1", **{filter_arg: model_filter})

        sent = _sent(service)["parameters"][param_key]
        assert list(sent) == ["must"]
        assert len(sent["must"]) == 1
        assert list(sent["must"].values()) == ["old"]
        assert next(iter(sent["must"])).endswith("Contains")  # nameContains / titleContains

    def test_dict_filter_is_sent_as_is(self, cls, plural, singular, ids_arg, filter_arg, id_arg,
                                       param_key, job_type, model_filter):
        service = _service(cls)
        raw = {"must": {"idIn": IDS}, "not": {"nameContains": "keep"}}

        getattr(service, plural)(dataset_id="dataset-1", **{filter_arg: raw})

        sent = _sent(service)["parameters"][param_key]
        assert sent == raw and sent is not raw

    @pytest.mark.parametrize("targets", [
        {},
        {"ids": IDS, "filter": {"must": {"idIn": IDS}}},
        {"ids": []},
        {"ids": ["a", ""]},
        {"ids": "01ARZ3NDEKTSV4RRFFQ69G5FAV"},
        {"filter": {}},
        {"filter": {"must": None}},
        {"filter": {"must": {"idIn": []}}},
        {"filter": {"must": {"idIn": []}, "not": {"nameContains": "x"}}},
        {"filter": {"must": {}}},
        {"filter": "must"},
        {"filter": {"must": "idIn"}},
        # A blank text search reads as "no condition" on the platform (selects everything).
        {"filter": {"must": {"nameContains": "   "}}},
        {"filter": {"must": {"nameContains": ""}}},
        {"filter": {"must": {"titleContains": " \t"}, "not": {"idIn": ["x"]}}},
        {"filter": {"must": {"keyContains": "  ", "idIn": ["x"]}}},
        {"filter": {"must": {"nameContains": "  "}, "not": {"nameContains": "keep"}}},
    ])
    def test_bad_targets_are_refused(self, cls, plural, singular, ids_arg, filter_arg, id_arg,
                                     param_key, job_type, model_filter, targets):
        service = _service(cls)
        kwargs = {}
        if "ids" in targets:
            kwargs[ids_arg] = targets["ids"]
        if "filter" in targets:
            kwargs[filter_arg] = targets["filter"]

        with pytest.raises(BadDeletionTargetError):
            getattr(service, plural)(dataset_id="dataset-1", **kwargs)
        with pytest.raises(ValueError):
            getattr(service, plural)(dataset_id="dataset-1", **kwargs)
        service.request_gql.assert_not_called()

    def test_blank_search_in_a_filter_model_is_refused(self, cls, plural, singular, ids_arg, filter_arg,
                                                      id_arg, param_key, job_type, model_filter):
        service = _service(cls)
        options = type(model_filter.must_filter if hasattr(model_filter, "must_filter") else model_filter.must)
        text_field = "title_contains" if "title_contains" in options.model_fields else "name_contains"
        blank = type(model_filter).model_validate({"must": {text_field: "   "}})

        with pytest.raises(BadDeletionTargetError, match="must not be blank"):
            getattr(service, plural)(dataset_id="dataset-1", **{filter_arg: blank})
        service.request_gql.assert_not_called()

    def test_not_only_filter_selects_the_rest(self, cls, plural, singular, ids_arg, filter_arg, id_arg,
                                              param_key, job_type, model_filter):
        """{"not": {"idIn": [x]}} means "all but x"; zenith and the DAGs take it too."""
        service = _service(cls)

        getattr(service, plural)(dataset_id="dataset-1", **{filter_arg: {"not": {"idIn": IDS}}})

        assert _sent(service)["parameters"][param_key] == {"not": {"idIn": IDS}}

    def test_wrong_filter_model_is_refused(self, cls, plural, singular, ids_arg, filter_arg, id_arg,
                                           param_key, job_type, model_filter):
        service = _service(cls)
        wrong = DataListFilter(must_filter=DataFilterOptions(key_contains="x"))

        with pytest.raises(BadDeletionTargetError, match=filter_arg):
            getattr(service, plural)(dataset_id="dataset-1", **{filter_arg: wrong})
        service.request_gql.assert_not_called()

    @pytest.mark.parametrize("value", [None, ""])
    def test_missing_dataset_id(self, cls, plural, singular, ids_arg, filter_arg, id_arg,
                                param_key, job_type, model_filter, value):
        service = _service(cls)

        with pytest.raises(BadParameterError, match="dataset_id is required"):
            getattr(service, plural)(dataset_id=value, **{ids_arg: IDS})
        service.request_gql.assert_not_called()

    def test_awaiting_approval_is_returned(self, cls, plural, singular, ids_arg, filter_arg, id_arg,
                                           param_key, job_type, model_filter):
        service = _service(cls)
        service.request_gql.return_value = _history("AWAITING_APPROVAL")

        result = getattr(service, plural)(dataset_id="dataset-1", **{ids_arg: IDS})

        assert result.status == ActivityStatus.AWAITING_APPROVAL

    # Deprecated singular functions --------------------------------------------
    def test_singular_starts_one_filter_activity(self, cls, plural, singular, ids_arg, filter_arg, id_arg,
                                                 param_key, job_type, model_filter):
        """The singular function calls startJob once, with an idIn filter of that one id."""
        service = _service(cls)

        with pytest.warns(DeprecationWarning) as caught:
            result = getattr(service, singular)(dataset_id="dataset-1", **{id_arg: "one-id"})

        assert isinstance(result, ActivityHistory)
        assert _sent(service) == {
            "datasetId": "dataset-1",
            "jobType": job_type,
            "parameters": {"dataset_id": "dataset-1", param_key: {"must": {"idIn": ["one-id"]}}},
        }
        message = str(caught[0].message)
        assert f"{singular} is deprecated" in message
        assert "next major version" in message
        assert "in a loop" in message
        assert f"{plural}({ids_arg}=[...])" in message
        assert filter_arg in message
        # The warning points at the caller, not at the SDK.
        assert caught[0].filename == __file__

    def test_singular_positional(self, cls, plural, singular, ids_arg, filter_arg, id_arg,
                                 param_key, job_type, model_filter):
        service = _service(cls)

        with pytest.warns(DeprecationWarning):
            getattr(service, singular)("dataset-1", "one-id")

        assert _sent(service)["parameters"][param_key] == {"must": {"idIn": ["one-id"]}}

    @pytest.mark.parametrize("missing", ["dataset_id", "entity"])
    @pytest.mark.parametrize("value", [None, ""])
    def test_singular_missing_ids(self, cls, plural, singular, ids_arg, filter_arg, id_arg,
                                  param_key, job_type, model_filter, missing, value):
        service = _service(cls)
        kwargs = {"dataset_id": "dataset-1", id_arg: "one-id"}
        kwargs["dataset_id" if missing == "dataset_id" else id_arg] = value

        with pytest.warns(DeprecationWarning):
            with pytest.raises(BadParameterError, match="is required"):
                getattr(service, singular)(**kwargs)
        service.request_gql.assert_not_called()


def test_entity_deletions_are_not_slice_scoped():
    """Only REMOVE_DATA_FROM_SLICE sends startJob(sliceId); deleting slices works on the dataset."""
    for cls, plural, ids_arg in [(SliceService, "delete_slices", "slice_ids"),
                                 (ModelService, "delete_models", "model_ids")]:
        service = _service(cls)
        getattr(service, plural)("dataset-1", **{ids_arg: IDS})
        assert "sliceId" not in _sent(service)


def test_start_activity_passes_slice_id():
    service = ActivityService()
    service.request_gql = Mock(return_value=_history())

    service.start_activity(dataset_id="dataset-1", activity_type="X", parameters={}, slice_id="slice-1")

    assert service.request_gql.call_args[0][1] == {
        "datasetId": "dataset-1", "jobType": "X", "parameters": {}, "sliceId": "slice-1",
    }


def test_no_sub_dag_id_is_sent():
    service = _service(SliceService)

    service.delete_slices("dataset-1", slice_ids=IDS)

    assert "sub_dag_id" not in _sent(service)["parameters"]


def test_server_refusal_is_raised():
    service = _service(ModelService)
    service.request_gql.side_effect = UnknownError("GraphQL errors: [CONFLICT] has a deployment")

    with pytest.raises(UnknownError, match="CONFLICT"):
        service.delete_models(dataset_id="dataset-1", model_ids=IDS)


def test_analytics_report_filter_has_id_in():
    dumped = AnalyticsReportsFilter(
        must_filter=AnalyticsReportsFilterOptions(id_in=IDS)
    ).model_dump(by_alias=True, exclude_unset=True)
    assert dumped == {"must": {"idIn": IDS}}


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
            "DELETE_DATA", "DELETE_SLICE", "REMOVE_DATA_FROM_SLICE", "DELETE_MODEL_DEPLOYMENT",
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


@pytest.mark.parametrize("cls,plural,filter_arg,bad,message", [
    (ModelService, "delete_models", "model_filter", {"not": "x", "must": {"idIn": IDS}}, "not must be an object"),
    (ModelService, "delete_models", "model_filter", {"must": {"idIn": "01ARZ3NDEKTSV4RRFFQ69G5FAV"}}, "list of non-empty ID strings"),
    (ModelService, "delete_models", "model_filter", {"must": {"idIn": [IDS[0], " "]}}, "list of non-empty ID strings"),
    (ModelService, "delete_models", "model_filter", {"not": {"idIn": [1]}, "must": {"nameContains": "x"}}, "list of non-empty ID strings"),
    (ModelService, "delete_models", "model_filter", {"must": {"statusIn": ["DONE"]}}, "unknown statuses ['DONE']"),
    (ModelService, "delete_models", "model_filter", {"must": {"statusIn": "FAILED"}}, "statusIn must be a list"),
    (DiagnosisService, "delete_diagnoses", "diagnosis_filter", {"must": {"statusIn": ["TRAINING"]}}, "unknown statuses"),
    (ReportService, "delete_analytics_reports", "report_filter", {"not": {"statusIn": ["X"]}, "must": {"titleContains": "a"}}, "unknown statuses"),
])
def test_dict_filter_value_shapes_are_refused_before_sending(cls, plural, filter_arg, bad, message):
    service = _service(cls)
    with pytest.raises(BadDeletionTargetError, match=re.escape(message)):
        getattr(service, plural)(dataset_id="dataset-1", **{filter_arg: bad})
    service.request_gql.assert_not_called()


def test_known_statuses_pass():
    from spb_onprem.models.enums import ModelStatus

    service = _service(ModelService)
    service.delete_models(dataset_id="dataset-1", model_filter={"must": {"statusIn": [ModelStatus.FAILED.value]}})
    assert _sent(service)["parameters"]["model_filter"] == {"must": {"statusIn": ["FAILED"]}}
