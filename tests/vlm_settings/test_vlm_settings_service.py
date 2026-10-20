"""VLMSettingsService (FDE-103): dataset and slice question sets."""
import copy
from unittest.mock import Mock, patch

import pytest

from spb_onprem import (
    DatasetVLMSettings,
    SliceVLMSettings,
    VLMAnswerOption,
    VLMAnswerType,
    VLMEvidenceClass,
    VLMEvidenceShape,
    VLMNumberRange,
    VLMQuestion,
    VLMQuestionSet,
    VLMSettingsService,
    VLMSettingsValidationError,
)
from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import (
    BadParameterError,
    ConflictError,
    ForbiddenError,
    InvalidInputError,
    NotFoundError,
    UnknownError,
)
from spb_onprem.vlm_settings.queries import Queries

Q1 = "01J0000000000000000000000A"
Q2 = "01J0000000000000000000000B"
OPT1 = "01J0000000000000000000000C"
OPT2 = "01J0000000000000000000000D"
EV1 = "01J0000000000000000000000E"

SETTINGS = {
    "reasoningGuide": "Look at the whole clip first.",
    "questions": [
        {
            "id": Q1,
            "text": "Is the robot holding an object?",
            "answerType": "SINGLE_CHOICE",
            "options": [{"id": OPT1, "label": "Yes"}, {"id": OPT2, "label": "No"}],
            "reasoningGuide": "Check the gripper.",
            "evidenceClasses": [{"id": EV1, "name": "gripper", "shape": "BOX", "color": "#FF0000"}],
            "deletedEvidenceClasses": [],
            "addedAt": "2026-10-20T00:00:00.000Z",
        },
        {"id": Q2, "text": "How many boxes?", "answerType": "NUMBER", "numberRange": {"min": 0, "max": 10}},
    ],
    "deletedQuestions": [],
}

RECORD = {
    "datasetId": "dataset-1",
    "settings": SETTINGS,
    "createdAt": "2026-10-20T00:00:00.000Z",
    "createdBy": "user@example.test",
    "updatedAt": None,
    "updatedBy": None,
}


def _service(response=None):
    service = VLMSettingsService()
    service.request_gql = Mock(return_value=response)
    return service


def _sent(service):
    service.request_gql.assert_called_once()
    return service.request_gql.call_args[0]


class TestDataset:
    def test_get(self):
        service = _service(RECORD)

        record = service.get_dataset_vlm_settings("dataset-1")

        query, variables = _sent(service)
        assert query is Queries.GET_DATASET_VLM_SETTINGS
        assert variables == {"datasetId": "dataset-1"}
        assert isinstance(record, DatasetVLMSettings)
        assert record.settings.questions[0].answer_type == VLMAnswerType.SINGLE_CHOICE
        assert record.settings.questions[1].number_range.max == 10
        assert record.version == "2026-10-20T00:00:00.000Z"  # createdAt while never updated

    def test_get_none(self):
        assert _service(None).get_dataset_vlm_settings("dataset-1") is None

    def test_create_with_dict(self):
        service = _service(RECORD)

        service.create_dataset_vlm_settings("dataset-1", SETTINGS)

        query, variables = _sent(service)
        assert query is Queries.CREATE_DATASET_VLM_SETTINGS
        assert variables == {"datasetId": "dataset-1", "settings": SETTINGS}
        assert variables["settings"] is not SETTINGS

    def test_create_with_models_sends_camel_case(self):
        service = _service(RECORD)
        question_set = VLMQuestionSet(
            reasoning_guide="Look at the whole clip first.",
            questions=[
                VLMQuestion(
                    id=Q1,
                    text="Is the robot holding an object?",
                    answer_type=VLMAnswerType.SINGLE_CHOICE,
                    options=[VLMAnswerOption(id=OPT1, label="Yes"), VLMAnswerOption(id=OPT2, label="No")],
                    reasoning_guide="Check the gripper.",
                    evidence_classes=[
                        VLMEvidenceClass(id=EV1, name="gripper", shape=VLMEvidenceShape.BOX, color="#FF0000")
                    ],
                    deleted_evidence_classes=[],
                    added_at="2026-10-20T00:00:00.000Z",
                ),
                VLMQuestion(
                    id=Q2, text="How many boxes?", answer_type=VLMAnswerType.NUMBER,
                    number_range=VLMNumberRange(min=0, max=10),
                ),
            ],
            deleted_questions=[],
        )

        service.create_dataset_vlm_settings("dataset-1", question_set)

        sent = _sent(service)[1]["settings"]
        assert sent == SETTINGS
        assert sent["questions"][1]["numberRange"] == {"min": 0, "max": 10}
        assert isinstance(sent["questions"][1]["numberRange"]["max"], int)

    def test_read_record_round_trips(self):
        """A record read from the platform can be sent back unchanged."""
        record = DatasetVLMSettings.model_validate(RECORD)
        service = _service(RECORD)

        service.update_dataset_vlm_settings("dataset-1", record.settings, expected_updated_at=record.version)

        query, variables = _sent(service)
        assert query is Queries.UPDATE_DATASET_VLM_SETTINGS
        assert variables == {
            "datasetId": "dataset-1",
            "settings": SETTINGS,
            "expectedUpdatedAt": "2026-10-20T00:00:00.000Z",
        }

    def test_update_without_version_skips_the_check(self):
        service = _service(RECORD)

        service.update_dataset_vlm_settings("dataset-1", SETTINGS)

        assert "expectedUpdatedAt" not in _sent(service)[1]

    def test_version_prefers_updated_at(self):
        record = DatasetVLMSettings.model_validate({**RECORD, "updatedAt": "2026-10-21T01:02:03.456Z"})
        assert record.version == "2026-10-21T01:02:03.456Z"

    def test_delete(self):
        service = _service(True)

        assert service.delete_dataset_vlm_settings("dataset-1", expected_updated_at="2026-10-20T00:00:00.000Z") is True

        query, variables = _sent(service)
        assert query is Queries.DELETE_DATASET_VLM_SETTINGS
        assert variables == {"datasetId": "dataset-1", "expectedUpdatedAt": "2026-10-20T00:00:00.000Z"}

    def test_reading_keeps_unknown_enum_values(self):
        """A newer platform may add an answer type or shape; reading must not fail."""
        settings = copy.deepcopy(SETTINGS)
        settings["questions"][1]["answerType"] = "FUTURE_TYPE"
        settings["questions"][0]["evidenceClasses"][0]["shape"] = "POLYGON"
        record = DatasetVLMSettings.model_validate({**RECORD, "settings": settings})
        assert record.settings.questions[1].answer_type == "FUTURE_TYPE"
        assert record.settings.questions[0].evidence_classes[0].shape == "POLYGON"
        assert record.settings.questions[0].answer_type is VLMAnswerType.SINGLE_CHOICE

    def test_reading_keeps_unknown_keys(self):
        """A newer platform may add keys; reading must not break."""
        settings = copy.deepcopy(SETTINGS)
        settings["questions"][1]["futureKey"] = 1
        record = DatasetVLMSettings.model_validate({**RECORD, "settings": settings})
        assert record.settings.questions[1].model_extra == {"futureKey": 1}


class TestSlice:
    SLICE_RECORD = {**RECORD, "sliceId": "slice-1"}

    def test_get(self):
        service = _service(self.SLICE_RECORD)

        record = service.get_slice_vlm_settings("dataset-1", "slice-1")

        query, variables = _sent(service)
        assert query is Queries.GET_SLICE_VLM_SETTINGS
        assert variables == {"datasetId": "dataset-1", "sliceId": "slice-1"}
        assert isinstance(record, SliceVLMSettings)
        assert record.slice_id == "slice-1"

    def test_get_none(self):
        assert _service(None).get_slice_vlm_settings("dataset-1", "slice-1") is None

    def test_create_from_the_dataset_settings(self):
        """A slice's set is created from settings read from the dataset (never copied by the platform)."""
        dataset_record = DatasetVLMSettings.model_validate(RECORD)
        service = _service(self.SLICE_RECORD)

        service.create_slice_vlm_settings("dataset-1", "slice-1", dataset_record.settings)

        query, variables = _sent(service)
        assert query is Queries.CREATE_SLICE_VLM_SETTINGS
        assert variables == {"datasetId": "dataset-1", "sliceId": "slice-1", "settings": SETTINGS}

    def test_update_and_delete(self):
        service = _service(self.SLICE_RECORD)
        service.update_slice_vlm_settings("dataset-1", "slice-1", SETTINGS, expected_updated_at="v1")
        query, variables = _sent(service)
        assert query is Queries.UPDATE_SLICE_VLM_SETTINGS
        assert variables["expectedUpdatedAt"] == "v1"
        assert variables["sliceId"] == "slice-1"

        service = _service(True)
        assert service.delete_slice_vlm_settings("dataset-1", "slice-1") is True
        query, variables = _sent(service)
        assert query is Queries.DELETE_SLICE_VLM_SETTINGS
        assert variables == {"datasetId": "dataset-1", "sliceId": "slice-1"}

    @pytest.mark.parametrize("call", [
        lambda s: s.get_slice_vlm_settings("dataset-1", None),
        lambda s: s.create_slice_vlm_settings("dataset-1", "", SETTINGS),
        lambda s: s.get_dataset_vlm_settings(None),
        lambda s: s.update_dataset_vlm_settings("dataset-1", SETTINGS, expected_updated_at=""),
    ])
    def test_missing_ids_are_refused(self, call):
        service = _service(None)
        with pytest.raises(BadParameterError):
            call(service)
        service.request_gql.assert_not_called()


def _mutate(path, value):
    settings = copy.deepcopy(SETTINGS)
    target = settings
    for key in path[:-1]:
        target = target[key]
    if value is KeyError:
        del target[path[-1]]
    else:
        target[path[-1]] = value
    return settings


class TestClientChecks:
    """The platform refuses these; the SDK refuses them before sending."""

    @pytest.mark.parametrize("settings,message", [
        (_mutate(["unknownTop"], 1), 'unknown key "unknownTop"'),
        (_mutate(["questions", 0, "answer"], "x"), 'unknown key "answer"'),
        (_mutate(["questions", 0, "options", 0, "value"], "x"), 'unknown key "value"'),
        (_mutate(["questions", 0, "evidenceClasses", 0, "label"], "x"), 'unknown key "label"'),
        (_mutate(["questions", 1, "numberRange", "step"], 1), 'unknown key "step"'),
        (_mutate(["questions", 0, "id"], "not-a-ulid"), "id must be a ulid"),
        (_mutate(["questions", 1, "id"], Q1), "is used more than once"),
        (_mutate(["questions", 0, "text"], "  "), "text must be a non-empty string"),
        (_mutate(["questions", 0, "answerType"], "ESSAY"), 'unknown answerType "ESSAY"'),
        (_mutate(["questions", 0, "options"], []), "choice questions need at least one option"),
        (_mutate(["questions", 1, "options"], [{"id": OPT1, "label": "x"}]), "only allowed on choice questions"),
        (_mutate(["questions", 0, "options", 1, "label"], "yes"), 'label "yes" is duplicated'),
        (_mutate(["questions", 0, "numberRange"], {"min": 1}), "only allowed on NUMBER questions"),
        (_mutate(["questions", 1, "numberRange"], {"min": 5, "max": 1}), "min must not be greater than max"),
        (_mutate(["questions", 1, "numberRange"], {"min": float("inf")}), "must be a finite number"),
        (_mutate(["questions", 0, "evidenceClasses", 0, "shape"], "POLYGON"), 'unknown shape "POLYGON"'),
        (_mutate(["questions", 0, "evidenceClasses", 0, "color"], "red"), "#RRGGBB"),
        (_mutate(["questions", 0, "addedAt"], "2026-10-20"), "ISO 8601 UTC timestamp"),
        (_mutate(["questions"], "q"), "settings.questions must be an array"),
        # Unhashable or huge values give a validation error, not TypeError / OverflowError.
        (_mutate(["questions", 0, "answerType"], ["TEXT"]), "unknown answerType"),
        (_mutate(["questions", 0, "answerType"], {"a": 1}), "unknown answerType"),
        (_mutate(["questions", 0, "evidenceClasses", 0, "shape"], ["BOX"]), "unknown shape"),
        (_mutate(["questions", 1, "numberRange"], {"max": 10 ** 400}), "must be a finite number"),
        ([], "settings must be an object"),
    ])
    def test_refused_before_sending(self, settings, message):
        service = _service(RECORD)
        with pytest.raises(VLMSettingsValidationError) as raised:
            service.create_dataset_vlm_settings("dataset-1", settings)
        assert any(message in item for item in raised.value.violations), raised.value.violations
        assert isinstance(raised.value, BadParameterError)
        service.request_gql.assert_not_called()

    def test_unknown_key_on_a_model_is_refused(self):
        question_set = VLMQuestionSet(questions=[VLMQuestion(
            id=Q1, text="?", answer_type=VLMAnswerType.TEXT, answer_hint="x",
        )])
        with pytest.raises(VLMSettingsValidationError, match='unknown key "answer_hint"'):
            _service(RECORD).create_dataset_vlm_settings("dataset-1", question_set)

    def test_every_answer_type_is_accepted(self):
        questions = []
        for index, answer_type in enumerate(VLMAnswerType):
            question = {"id": f"01J00000000000000000000{index:03d}", "text": "?", "answerType": answer_type.value}
            if answer_type in (VLMAnswerType.SINGLE_CHOICE, VLMAnswerType.MULTI_CHOICE):
                question["options"] = [{"id": f"01J00000000000000000001{index:03d}", "label": "a"}]
            questions.append(question)
        service = _service(RECORD)
        service.create_dataset_vlm_settings("dataset-1", {"questions": questions})
        assert len(_sent(service)[1]["settings"]["questions"]) == 6


class _Response:
    status_code = 200
    elapsed = None

    def __init__(self, body):
        self._body = body

    def raise_for_status(self):
        return None

    def json(self):
        return self._body


def _platform_error(code, details=None, message="refused"):
    error = {"message": message, "code": code}
    if details is not None:
        error["details"] = details
    session = Mock()
    session.post.return_value = _Response({"errors": [error], "data": None})
    return patch.object(BaseService, "requests_retry_session", return_value=session)


class TestPlatformErrors:
    def test_conflict_on_a_stale_version(self):
        details = {"expectedUpdatedAt": "2026-10-20T00:00:00.000Z", "currentUpdatedAt": "2026-10-21T00:00:00.000Z"}
        with _platform_error("CONFLICT", details, "VLM settings changed since they were loaded."):
            with pytest.raises(ConflictError) as raised:
                VLMSettingsService().update_dataset_vlm_settings(
                    "dataset-1", SETTINGS, expected_updated_at="2026-10-20T00:00:00.000Z"
                )
        assert raised.value.code == "CONFLICT"
        assert raised.value.details["currentUpdatedAt"] == "2026-10-21T00:00:00.000Z"
        assert isinstance(raised.value, UnknownError)  # old except clauses keep working

    def test_bad_request(self):
        with _platform_error("BAD_REQUEST", message="VLM settings can only be set on a VLM dataset."):
            with pytest.raises(InvalidInputError, match="only be set on a VLM dataset"):
                VLMSettingsService().create_dataset_vlm_settings("dataset-1", SETTINGS)

    def test_forbidden(self):
        with _platform_error("FORBIDDEN"):
            with pytest.raises(ForbiddenError):
                VLMSettingsService().delete_slice_vlm_settings("dataset-1", "slice-1")

    @pytest.mark.parametrize("resource", ["dataset", "slice", "vlmSettings"])
    def test_not_found_tells_what_is_missing(self, resource):
        with _platform_error("NOT_FOUND", {"resource": resource, "datasetId": "dataset-1"}):
            with pytest.raises(NotFoundError) as raised:
                VLMSettingsService().update_slice_vlm_settings("dataset-1", "slice-1", SETTINGS)
        assert raised.value.details["resource"] == resource
