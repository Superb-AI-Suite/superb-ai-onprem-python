"""ActivityService.get_activity_histories: one page of the runs of a dataset."""
from unittest.mock import MagicMock

import pytest

from spb_onprem import ActivityService
from spb_onprem.activities.entities import ActivityHistory, ActivityStatus
from spb_onprem.activities.params import (
    MAX_ACTIVITY_HISTORIES_LENGTH,
    get_activity_histories_params,
)
from spb_onprem.activities.queries import Queries
from spb_onprem.exceptions import BadParameterError, BadResponseError

DATASET_ID = "01DATASET0000000000000000A"
OTHER_DATASET_ID = "01DATASET0000000000000000B"


def _history(history_id, dataset_id=DATASET_ID, **fields):
    item = {
        "id": history_id,
        "jobId": "01JOB",
        "status": "SUCCESS",
        "datasetId": dataset_id,
        "parameters": {"slice_id": "01SLICE"},
        "progress": {"done": 1},
        "createdAt": "2026-11-25T01:00:00.000Z",
        "createdBy": "user@example.com",
        "updatedAt": "2026-11-25T01:05:00.000Z",
        "updatedBy": "user@example.com",
        "meta": None,
    }
    item.update(fields)
    return item


@pytest.fixture
def service():
    service = ActivityService()
    service.request_gql = MagicMock()
    return service


def _sent_variables(service):
    query, variables = service.request_gql.call_args.args
    assert query is Queries.GET_ACTIVITY_HISTORIES
    return variables


class TestVariables:
    def test_defaults_newest_first_and_dataset_in_both_places(self, service):
        service.request_gql.return_value = {"jobHistories": [], "next": None, "totalCount": 0}

        service.get_activity_histories(DATASET_ID)

        assert _sent_variables(service) == {
            "datasetId": DATASET_ID,
            "filter": {"must": {"datasetId": DATASET_ID}},
            "orderBy": {"field": "createdAt", "direction": "DESC"},
            "cursor": None,
            "length": 10,
        }

    def test_every_filter_goes_to_must(self, service):
        service.request_gql.return_value = {"jobHistories": [], "next": None, "totalCount": 0}

        service.get_activity_histories(
            DATASET_ID,
            activity_id="01JOB",
            status=[ActivityStatus.FAILED, "RUNNING"],
            requester=["a@example.com", "b@example.com"],
            slice_id="01SLICE",
            cursor="MTA=",
            length=50,
            oldest_first=True,
        )

        assert _sent_variables(service) == {
            "datasetId": DATASET_ID,
            "filter": {"must": {
                "datasetId": DATASET_ID,
                "jobIdIn": ["01JOB"],
                "statusIn": ["FAILED", "RUNNING"],
                "requestedByIn": ["a@example.com", "b@example.com"],
                "sliceIdIn": ["01SLICE"],
            }},
            "orderBy": {"field": "createdAt", "direction": "ASC"},
            "cursor": "MTA=",
            "length": 50,
        }

    def test_one_value_becomes_a_list(self):
        variables = get_activity_histories_params(
            DATASET_ID, activity_id="01JOB", status="SUCCESS", requester="a@example.com", slice_id="01SLICE",
        )
        must = variables["filter"]["must"]
        assert must["jobIdIn"] == ["01JOB"]
        assert must["statusIn"] == ["SUCCESS"]
        assert must["requestedByIn"] == ["a@example.com"]
        assert must["sliceIdIn"] == ["01SLICE"]

    def test_status_old_spelling_and_duplicates(self):
        variables = get_activity_histories_params(
            DATASET_ID, status=("CANCELLED", ActivityStatus.CANCELED, "FAILED"),
        )
        assert variables["filter"]["must"]["statusIn"] == ["CANCELED", "FAILED"]

    def test_filters_are_keyword_only(self, service):
        with pytest.raises(TypeError):
            service.get_activity_histories(DATASET_ID, "01JOB")
        service.request_gql.assert_not_called()


class TestRefusedBeforeSending:
    @pytest.mark.parametrize("dataset_id", [None, "", "   ", 123])
    def test_dataset_id_is_required(self, service, dataset_id):
        with pytest.raises(BadParameterError, match="dataset_id"):
            service.get_activity_histories(dataset_id)
        service.request_gql.assert_not_called()

    @pytest.mark.parametrize("length", [0, -1, MAX_ACTIVITY_HISTORIES_LENGTH + 1, True, 1.5, "10"])
    def test_length_out_of_range(self, service, length):
        with pytest.raises(BadParameterError, match="length"):
            service.get_activity_histories(DATASET_ID, length=length)
        service.request_gql.assert_not_called()

    @pytest.mark.parametrize("name", ["activity_id", "requester", "slice_id", "status"])
    def test_empty_list_is_refused(self, service, name):
        # The platform reads an empty list as "no condition"; it would list every run.
        with pytest.raises(BadParameterError, match=name):
            service.get_activity_histories(DATASET_ID, **{name: []})
        service.request_gql.assert_not_called()

    @pytest.mark.parametrize("name", ["activity_id", "requester", "slice_id"])
    @pytest.mark.parametrize("value", [[""], ["  "], [None], 12, {"a": 1}])
    def test_bad_values_are_refused(self, service, name, value):
        with pytest.raises(BadParameterError, match=name):
            service.get_activity_histories(DATASET_ID, **{name: value})
        service.request_gql.assert_not_called()

    @pytest.mark.parametrize("status", ["DONE", ["SUCCESS", "nope"], 3])
    def test_unknown_status(self, service, status):
        with pytest.raises(BadParameterError, match="status"):
            service.get_activity_histories(DATASET_ID, status=status)
        service.request_gql.assert_not_called()

    def test_cursor_must_be_a_string(self, service):
        with pytest.raises(BadParameterError, match="cursor"):
            service.get_activity_histories(DATASET_ID, cursor=10)
        service.request_gql.assert_not_called()

    def test_oldest_first_must_be_bool(self, service):
        with pytest.raises(BadParameterError, match="oldest_first"):
            service.get_activity_histories(DATASET_ID, oldest_first="yes")
        service.request_gql.assert_not_called()


class TestResponse:
    def test_page_is_items_next_cursor_and_total(self, service):
        service.request_gql.return_value = {
            "jobHistories": [_history("01RUN2"), _history("01RUN1", status="FAILED", meta={"error": "x"})],
            "next": "Mg==",
            "totalCount": 7,
        }

        items, next_cursor, total = service.get_activity_histories(DATASET_ID, length=2)

        assert [item.id for item in items] == ["01RUN2", "01RUN1"]
        assert all(isinstance(item, ActivityHistory) for item in items)
        assert items[0].activity_id == "01JOB"
        assert items[0].dataset_id == DATASET_ID
        assert items[0].created_by == "user@example.com"
        assert items[1].status == ActivityStatus.FAILED
        assert items[1].meta == {"error": "x"}
        assert next_cursor == "Mg=="
        assert total == 7

    def test_last_page_has_no_cursor(self, service):
        service.request_gql.return_value = {"jobHistories": [_history("01RUN1")], "next": None, "totalCount": 1}

        assert service.get_activity_histories(DATASET_ID)[1:] == (None, 1)

    @pytest.mark.parametrize("response", [
        {"jobHistories": None, "next": None, "totalCount": None},
        {},
        None,
    ])
    def test_empty_page(self, service, response):
        service.request_gql.return_value = response

        assert service.get_activity_histories(DATASET_ID) == ([], None, 0)

    def test_paging_passes_the_cursor_back(self, service):
        service.request_gql.side_effect = [
            {"jobHistories": [_history("01RUN3"), _history("01RUN2")], "next": "Mg==", "totalCount": 3},
            {"jobHistories": [_history("01RUN1")], "next": None, "totalCount": 3},
        ]

        seen, cursor = [], None
        while True:
            items, cursor, _ = service.get_activity_histories(DATASET_ID, cursor=cursor, length=2)
            seen.extend(item.id for item in items)
            if cursor is None:
                break

        assert seen == ["01RUN3", "01RUN2", "01RUN1"]
        cursors = [call.args[1]["cursor"] for call in service.request_gql.call_args_list]
        assert cursors == [None, "Mg=="]


class TestOtherDatasetIsNeverReturned:
    @pytest.mark.parametrize("foreign", [
        _history("01RUNX", dataset_id=OTHER_DATASET_ID),
        _history("01RUNX", dataset_id=None),
        {k: v for k, v in _history("01RUNX").items() if k != "datasetId"},
    ])
    def test_a_run_of_another_dataset_raises(self, service, foreign):
        service.request_gql.return_value = {
            "jobHistories": [_history("01RUN1"), foreign],
            "next": None,
            "totalCount": 2,
        }

        with pytest.raises(BadResponseError, match="another dataset") as raised:
            service.get_activity_histories(DATASET_ID)
        # The foreign run is not named in the error.
        assert "01RUNX" not in str(raised.value)
        assert OTHER_DATASET_ID not in str(raised.value)
