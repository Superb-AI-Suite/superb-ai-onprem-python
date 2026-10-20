"""VLMSettingsService and VLMSettings (FDE-103): build like a filter, edit with helpers, round-trip."""
import copy
import re
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
    VLMSettings,
    VLMSettingsChangeError,
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
from spb_onprem.vlm_settings import collect_vlm_settings_violations
from spb_onprem.vlm_settings.queries import Queries

ULID = re.compile(r"^[0-7][0-9A-HJKMNP-TV-Z]{25}$")
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")

Q1 = "01J0000000000000000000000A"
Q2 = "01J0000000000000000000000B"
OPT1 = "01J0000000000000000000000C"
OPT2 = "01J0000000000000000000000D"
EV1 = "01J0000000000000000000000E"
EV2 = "01J0000000000000000000000F"
T0 = "2026-10-20T00:00:00.000Z"

STORED = {
    "reasoningGuide": "Look at the whole clip first.",
    "questions": [
        {
            "id": Q1,
            "text": "Is the robot holding an object?",
            "answerType": "SINGLE_CHOICE",
            "options": [{"id": OPT1, "label": "Yes"}, {"id": OPT2, "label": "No"}],
            "reasoningGuide": "Check the gripper.",
            "evidenceClasses": [{"id": EV1, "name": "gripper", "shape": "BOX", "color": "#FF0000", "addedAt": T0}],
            "deletedEvidenceClasses": [{"id": EV2, "name": "hand", "shape": "POINT", "deletedAt": T0}],
            "addedAt": T0,
        },
        # Stored without addedAt: reading must not fill it in.
        {"id": Q2, "text": "How many boxes?", "answerType": "NUMBER", "numberRange": {"min": 0, "max": 10}},
    ],
    "deletedQuestions": [],
}

RECORD = {
    "datasetId": "dataset-1",
    "settings": STORED,
    "createdAt": T0,
    "createdBy": "user@example.test",
    "updatedAt": None,
    "updatedBy": None,
}


def _same(payload):
    """Settings with empty evidence lists dropped (the platform reads missing and [] the same)."""
    payload = copy.deepcopy(payload)
    for key in ("questions", "deletedQuestions"):
        for question in payload.get(key) or []:
            for field in ("evidenceClasses", "deletedEvidenceClasses"):
                if question.get(field) == []:
                    question.pop(field)
    return payload


def _service(response=None):
    service = VLMSettingsService()
    service.request_gql = Mock(return_value=response)
    return service


def _sent(service):
    service.request_gql.assert_called_once()
    return service.request_gql.call_args[0]


def _read(record=RECORD):
    return _service(copy.deepcopy(record)).get_dataset_vlm_settings("dataset-1")


# --- Building like a filter ---------------------------------------------------


class TestBuilding:
    def test_ids_and_added_at_are_filled_in(self):
        settings = VLMSettings(questions=[VLMQuestion(
            text="Does this object have a visible defect?",
            answer_type=VLMAnswerType.BOOLEAN,
            evidence_classes=[VLMEvidenceClass(name="defect", shape=VLMEvidenceShape.BOX)],
        )])

        payload = settings.to_payload()
        question = payload["questions"][0]
        evidence = question["evidenceClasses"][0]
        assert ULID.match(question["id"]) and ULID.match(evidence["id"])
        assert question["id"] != evidence["id"]
        assert ISO.match(question["addedAt"]) and ISO.match(evidence["addedAt"])
        assert question["answerType"] == "BOOLEAN" and evidence["shape"] == "BOX"
        # No nulls are sent (a null color would be refused).
        assert "color" not in evidence and "deletedAt" not in question and "reasoningGuide" not in payload
        assert collect_vlm_settings_violations(payload) == []

    def test_options_from_labels(self):
        question = VLMQuestion(text="Which color?", answer_type=VLMAnswerType.SINGLE_CHOICE, options=["Red", "Blue"])
        assert [option.label for option in question.options] == ["Red", "Blue"]
        assert all(ULID.match(option.id) for option in question.options)
        assert "addedAt" not in question.model_dump(by_alias=True)["options"][0]

    def test_explicit_values_are_kept(self):
        question = VLMQuestion(id=Q1, text="?", answer_type="TEXT", added_at=T0)
        assert question.id == Q1 and question.added_at == T0

    def test_every_answer_type(self):
        settings = VLMSettings()
        for answer_type in VLMAnswerType:
            options = ["a", "b"] if answer_type in (VLMAnswerType.SINGLE_CHOICE, VLMAnswerType.MULTI_CHOICE) else None
            settings.add_question(text=f"{answer_type.value}?", answer_type=answer_type, options=options)
        assert collect_vlm_settings_violations(settings.to_payload()) == []
        assert len(settings.questions) == 6


# --- Service --------------------------------------------------------------------


class TestService:
    def test_get_reads_without_filling_in(self):
        service = _service(copy.deepcopy(RECORD))

        record = service.get_dataset_vlm_settings("dataset-1")

        query, variables = _sent(service)
        assert query is Queries.GET_DATASET_VLM_SETTINGS
        assert variables == {"datasetId": "dataset-1"}
        assert isinstance(record, DatasetVLMSettings) and isinstance(record.settings, VLMSettings)
        assert record.settings.questions[0].answer_type is VLMAnswerType.SINGLE_CHOICE
        assert record.settings.questions[1].added_at is None
        assert record.version == T0

    def test_get_none(self):
        assert _service(None).get_dataset_vlm_settings("dataset-1") is None
        assert _service(None).get_slice_vlm_settings("dataset-1", "slice-1") is None

    def test_create_sends_the_payload(self):
        settings = VLMSettings(questions=[VLMQuestion(text="What happens?", answer_type=VLMAnswerType.TEXT)])
        service = _service(copy.deepcopy(RECORD))

        service.create_dataset_vlm_settings("dataset-1", settings)

        query, variables = _sent(service)
        assert query is Queries.CREATE_DATASET_VLM_SETTINGS
        assert variables == {"datasetId": "dataset-1", "settings": settings.to_payload()}

    def test_dict_is_refused_like_filters(self):
        service = _service(copy.deepcopy(RECORD))
        with pytest.raises(VLMSettingsValidationError, match="VLMSettings.model_validate"):
            service.create_dataset_vlm_settings("dataset-1", STORED)
        service.request_gql.assert_not_called()

        service.create_dataset_vlm_settings("dataset-1", VLMSettings.model_validate(STORED))
        assert _sent(service)[1]["settings"]["questions"][0]["id"] == Q1

    def test_unchanged_round_trip(self):
        record = _read()
        service = _service(copy.deepcopy(RECORD))

        service.update_dataset_vlm_settings("dataset-1", record.settings, expected_updated_at=record.version)

        query, variables = _sent(service)
        assert query is Queries.UPDATE_DATASET_VLM_SETTINGS
        assert variables["expectedUpdatedAt"] == T0
        assert _same(variables["settings"]) == _same(STORED)

    def test_update_returns_a_record_ready_for_the_next_edit(self):
        record = _read()
        record.settings.delete_question(Q2)
        updated_record = {**RECORD, "settings": record.settings.to_payload(), "updatedAt": "2026-10-21T00:00:00.000Z"}
        service = _service(updated_record)

        updated = service.update_dataset_vlm_settings("dataset-1", record.settings, expected_updated_at=record.version)

        assert updated.version == "2026-10-21T00:00:00.000Z"
        assert [q.id for q in updated.settings.deleted_questions] == [Q2]
        updated.settings.restore_question(Q2)  # the next edit works on the returned record
        assert [q.id for q in updated.settings.questions] == [Q1, Q2]

    def test_delete(self):
        service = _service(True)
        assert service.delete_dataset_vlm_settings("dataset-1", expected_updated_at=T0) is True
        query, variables = _sent(service)
        assert query is Queries.DELETE_DATASET_VLM_SETTINGS
        assert variables == {"datasetId": "dataset-1", "expectedUpdatedAt": T0}

    def test_slice_functions(self):
        slice_record = {**RECORD, "sliceId": "slice-1"}
        dataset_settings = _read().settings

        service = _service(copy.deepcopy(slice_record))
        service.create_slice_vlm_settings("dataset-1", "slice-1", dataset_settings)
        query, variables = _sent(service)
        assert query is Queries.CREATE_SLICE_VLM_SETTINGS
        assert variables["sliceId"] == "slice-1"
        assert _same(variables["settings"]) == _same(STORED)

        service = _service(copy.deepcopy(slice_record))
        record = service.get_slice_vlm_settings("dataset-1", "slice-1")
        assert isinstance(record, SliceVLMSettings) and record.slice_id == "slice-1"

        record.settings.questions[0].add_evidence_class(name="box", shape=VLMEvidenceShape.BOX)
        service = _service(copy.deepcopy(slice_record))
        service.update_slice_vlm_settings("dataset-1", "slice-1", record.settings, expected_updated_at=record.version)
        query, variables = _sent(service)
        assert query is Queries.UPDATE_SLICE_VLM_SETTINGS
        assert variables["expectedUpdatedAt"] == T0
        assert [c["name"] for c in variables["settings"]["questions"][0]["evidenceClasses"]] == ["gripper", "box"]

        service = _service(True)
        assert service.delete_slice_vlm_settings("dataset-1", "slice-1") is True
        assert _sent(service)[1] == {"datasetId": "dataset-1", "sliceId": "slice-1"}

    @pytest.mark.parametrize("call", [
        lambda s: s.get_slice_vlm_settings("dataset-1", None),
        lambda s: s.create_slice_vlm_settings("dataset-1", "", VLMSettings()),
        lambda s: s.get_dataset_vlm_settings(None),
        lambda s: s.update_dataset_vlm_settings("dataset-1", VLMSettings(), expected_updated_at=""),
    ])
    def test_missing_ids_are_refused(self, call):
        service = _service(None)
        with pytest.raises(BadParameterError):
            call(service)
        service.request_gql.assert_not_called()


# --- Helpers: delete and restore -------------------------------------------------


class TestQuestionHelpers:
    def test_delete_then_restore_round_trip(self):
        settings = _read().settings

        deleted = settings.delete_question(Q2)
        payload = settings.to_payload()
        assert [q["id"] for q in payload["questions"]] == [Q1]
        assert [q["id"] for q in payload["deletedQuestions"]] == [Q2]
        assert ISO.match(deleted.deleted_at) and payload["deletedQuestions"][0]["deletedAt"] == deleted.deleted_at

        settings.restore_question(Q2)
        payload = settings.to_payload()
        assert [q["id"] for q in payload["questions"]] == [Q1, Q2]
        assert payload["deletedQuestions"] == []
        assert "deletedAt" not in payload["questions"][1]
        assert _same(payload) == _same(STORED)  # back to what was stored

    def test_redelete_keeps_the_first_time(self):
        settings = VLMSettings.model_validate({
            "questions": [], "deletedQuestions": [{"id": Q1, "text": "?", "answerType": "TEXT", "deletedAt": T0}],
        })
        settings.restore_question(Q1)
        assert settings.delete_question(Q1).deleted_at == T0

    def test_added_question_gets_id_and_time(self):
        settings = _read().settings
        question = settings.add_question(text="Is it raining?", answer_type=VLMAnswerType.BOOLEAN)
        assert ULID.match(question.id) and ISO.match(question.added_at)
        assert settings.questions[-1] is question
        assert settings.add_question(VLMQuestion(text="?", answer_type="TEXT")).answer_type is VLMAnswerType.TEXT

    @pytest.mark.parametrize("call,message", [
        (lambda s: s.delete_question("01J000000000000000000000ZZ"), "there is no question"),
        (lambda s: s.restore_question("01J000000000000000000000ZZ"), "there is no question"),
        (lambda s: s.restore_question(Q1), "is not deleted"),
        (lambda s: s.get_question("01J000000000000000000000ZZ"), "there is no question"),
        (lambda s: s.add_question(VLMQuestion(id=Q1, text="?", answer_type="TEXT")), "already used"),
        (lambda s: s.add_question(VLMQuestion(text="?", answer_type="TEXT"), text="x"), "not both"),
    ])
    def test_wrong_ids(self, call, message):
        with pytest.raises(VLMSettingsChangeError, match=message):
            call(_read().settings)

    def test_deleting_twice(self):
        settings = _read().settings
        settings.delete_question(Q1)
        with pytest.raises(VLMSettingsChangeError, match="already deleted"):
            settings.delete_question(Q1)


class TestEvidenceClassHelpers:
    def test_delete_then_restore_round_trip(self):
        settings = _read().settings
        question = settings.get_question(Q1)

        question.delete_evidence_class(EV1)
        payload = settings.to_payload()["questions"][0]
        assert payload["evidenceClasses"] == []
        assert [c["id"] for c in payload["deletedEvidenceClasses"]] == [EV2, EV1]

        question.restore_evidence_class(EV1)
        restored = settings.to_payload()["questions"][0]
        assert [c["id"] for c in restored["evidenceClasses"]] == [EV1]
        assert "deletedAt" not in restored["evidenceClasses"][0]
        assert [c["id"] for c in restored["deletedEvidenceClasses"]] == [EV2]

    def test_restore_a_class_deleted_before(self):
        question = _read().settings.get_question(Q1)
        restored = question.restore_evidence_class(EV2)
        assert restored.deleted_at is None
        assert [c.id for c in question.evidence_classes] == [EV1, EV2]
        assert question.delete_evidence_class(EV2).deleted_at == T0  # its first deletion time

    def test_add_and_color(self):
        settings = _read().settings
        question = settings.get_question(Q1)
        added = question.add_evidence_class(name="cup", shape=VLMEvidenceShape.BOX, color="#00FF00")
        assert ULID.match(added.id) and ISO.match(added.added_at)
        question.set_evidence_class_color(EV1, "#0000FF")
        question.reasoning_guide = "Look at the gripper and the table."  # can change
        settings.reasoning_guide = "New common guide."                     # can change

        service = _service(copy.deepcopy(RECORD))
        service.update_dataset_vlm_settings("dataset-1", settings)  # passes the change check
        sent = _sent(service)[1]["settings"]
        assert sent["questions"][0]["evidenceClasses"][0]["color"] == "#0000FF"
        assert sent["reasoningGuide"] == "New common guide."

    @pytest.mark.parametrize("call,message", [
        (lambda q: q.delete_evidence_class("01J000000000000000000000ZZ"), "has no evidence class"),
        (lambda q: q.delete_evidence_class(EV2), "already deleted"),
        (lambda q: q.restore_evidence_class(EV1), "is not deleted"),
        (lambda q: q.add_evidence_class(name="Gripper", shape="BOX"), 'already has an evidence class "Gripper"'),
        (lambda q: q.add_evidence_class(name="x"), "name and shape"),
        (lambda q: q.set_evidence_class_color("01J000000000000000000000ZZ", "#000000"), "has no evidence class"),
    ])
    def test_wrong_ids(self, call, message):
        with pytest.raises(VLMSettingsChangeError, match=message):
            call(_read().settings.get_question(Q1))

    def test_restore_with_a_taken_name(self):
        question = _read().settings.get_question(Q1)
        question.add_evidence_class(name="hand", shape=VLMEvidenceShape.POINT)
        with pytest.raises(VLMSettingsChangeError, match='already has an evidence class "hand"'):
            question.restore_evidence_class(EV2)


# --- What cannot change ----------------------------------------------------------


class TestUnchangeableFields:
    @pytest.mark.parametrize("target,field,value", [
        ("question", "text", "Another text"),
        ("question", "answer_type", VLMAnswerType.TEXT),
        ("question", "options", []),
        ("question", "id", Q2),
        ("question2", "number_range", VLMNumberRange(min=1)),
        ("range", "max", 99),
        ("option", "label", "Maybe"),
        ("class", "name", "hand2"),
        ("class", "shape", VLMEvidenceShape.POINT),
    ])
    def test_assignment_is_refused_with_a_reason(self, target, field, value):
        settings = _read().settings
        objects = {
            "question": settings.get_question(Q1),
            "question2": settings.get_question(Q2),
            "range": settings.get_question(Q2).number_range,
            "option": settings.get_question(Q1).options[0],
            "class": settings.get_question(Q1).get_evidence_class(EV1),
        }
        with pytest.raises(VLMSettingsChangeError, match="cannot change once saved") as raised:
            setattr(objects[target], field, value)
        assert "delete the" in str(raised.value)

    def test_unsent_items_can_still_change(self):
        """Items built or added but not sent yet are not stored: their content can still change."""
        settings = VLMSettings(questions=[VLMQuestion(text="Draft?", answer_type=VLMAnswerType.TEXT)])
        draft = settings.questions[0]
        draft.text = "Final text?"
        draft.answer_type = VLMAnswerType.SINGLE_CHOICE
        draft.options = [VLMAnswerOption(label="a")]
        added = _read().settings.add_question(text="New?", answer_type=VLMAnswerType.BOOLEAN)
        added.text = "New question?"
        evidence = _read().settings.get_question(Q1).add_evidence_class(name="cup", shape="BOX")
        evidence.name = "mug"
        assert draft.text == "Final text?" and added.text == "New question?" and evidence.name == "mug"

    def test_items_lock_after_they_are_sent(self):
        settings = VLMSettings(questions=[VLMQuestion(text="Draft?", answer_type=VLMAnswerType.TEXT)])
        question = settings.questions[0]
        service = _service({**RECORD, "settings": settings.to_payload()})

        service.create_dataset_vlm_settings("dataset-1", settings)

        with pytest.raises(VLMSettingsChangeError, match="cannot change once saved"):
            question.text = "Changed after saving"
        # The sent object now checks later changes against what was stored.
        settings.questions.pop()
        with pytest.raises(VLMSettingsChangeError, match="was removed"):
            _service(RECORD).update_dataset_vlm_settings("dataset-1", settings)

    @pytest.mark.parametrize("target,alias,field,value", [
        ("question", "answerType", "answer_type", "TEXT"),
        ("question2", "numberRange", "number_range", {"min": 1}),
        ("question", "reasoningGuide", "reasoning_guide", "x"),
        ("settings", "deletedQuestions", "deleted_questions", []),
        ("class", "addedAt", "added_at", T0),
    ])
    def test_alias_assignment_is_refused(self, target, alias, field, value):
        settings = _read().settings
        objects = {
            "settings": settings,
            "question": settings.get_question(Q1),
            "question2": settings.get_question(Q2),
            "class": settings.get_question(Q1).get_evidence_class(EV1),
        }
        with pytest.raises(VLMSettingsChangeError, match=f"{field}"):
            setattr(objects[target], alias, value)
        # Also on items not sent yet.
        fresh = VLMQuestion(text="?", answer_type=VLMAnswerType.NUMBER)
        with pytest.raises(VLMSettingsChangeError, match="not the alias numberRange"):
            fresh.numberRange = {"min": 1}

    def _update(self, settings):
        service = _service(copy.deepcopy(RECORD))
        service.update_dataset_vlm_settings("dataset-1", settings, expected_updated_at=T0)
        return service

    def test_changing_a_list_in_place_is_caught_before_sending(self):
        settings = _read().settings
        settings.get_question(Q1).options.append(VLMAnswerOption(label="Maybe"))
        service = _service(copy.deepcopy(RECORD))
        with pytest.raises(VLMSettingsChangeError, match="options cannot change"):
            service.update_dataset_vlm_settings("dataset-1", settings, expected_updated_at=T0)
        service.request_gql.assert_not_called()

    def test_removing_a_question_from_the_list_is_caught(self):
        settings = _read().settings
        settings.questions.pop()
        with pytest.raises(VLMSettingsChangeError, match=f"question {Q2} was removed; delete it with delete_question"):
            self._update(settings)

    def test_moving_a_class_to_another_question_is_caught(self):
        settings = _read().settings
        moved = settings.get_question(Q1).evidence_classes.pop()
        settings.get_question(Q2).evidence_classes.append(moved)
        with pytest.raises(VLMSettingsChangeError, match=f"evidence class {EV1} of question {Q1} was removed"):
            self._update(settings)

    def test_a_new_set_is_not_compared(self):
        """Creating (or creating a slice set from a dataset set) has nothing stored to compare with."""
        settings = _read().settings
        settings.questions.pop()
        service = _service({**RECORD, "sliceId": "slice-1"})
        service.create_slice_vlm_settings("dataset-1", "slice-1", settings)
        assert len(_sent(service)[1]["settings"]["questions"]) == 1


# --- Shape checks (the platform's rules, before sending) ------------------------


def _mutate(path, value):
    settings = copy.deepcopy(STORED)
    target = settings
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return settings


class TestShapeChecks:
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
        (_mutate(["questions", 1, "numberRange"], {"max": 10 ** 400}), "must be a finite number"),
        (_mutate(["questions", 0, "evidenceClasses", 0, "shape"], "POLYGON"), 'unknown shape "POLYGON"'),
        (_mutate(["questions", 0, "evidenceClasses", 0, "color"], "red"), "#RRGGBB"),
        (_mutate(["questions", 0, "addedAt"], "2026-10-20"), "ISO 8601 UTC timestamp"),
    ])
    def test_refused_before_sending(self, settings, message):
        service = _service(copy.deepcopy(RECORD))
        with pytest.raises(VLMSettingsValidationError) as raised:
            service.create_dataset_vlm_settings("dataset-1", VLMSettings.model_validate(settings))
        assert any(message in item for item in raised.value.violations), raised.value.violations
        assert isinstance(raised.value, BadParameterError)
        service.request_gql.assert_not_called()

    @pytest.mark.parametrize("settings,message", [
        (_mutate(["questions", 0, "answerType"], ["TEXT"]), "unknown answerType"),
        (_mutate(["questions", 0, "answerType"], {"a": 1}), "unknown answerType"),
        (_mutate(["questions", 0, "evidenceClasses", 0, "shape"], ["BOX"]), "unknown shape"),
        (_mutate(["questions"], "q"), "settings.questions must be an array"),
        ([], "settings must be an object"),
    ])
    def test_odd_values_give_violations_not_exceptions(self, settings, message):
        violations = collect_vlm_settings_violations(settings)
        assert any(message in item for item in violations), violations

    def test_unknown_key_on_a_model_is_refused(self):
        settings = VLMSettings(questions=[VLMQuestion(text="?", answer_type=VLMAnswerType.TEXT, answer_hint="x")])
        with pytest.raises(VLMSettingsValidationError, match='unknown key "answer_hint"'):
            _service(RECORD).create_dataset_vlm_settings("dataset-1", settings)


class TestReading:
    def test_keeps_unknown_keys_and_enum_values(self):
        stored = copy.deepcopy(STORED)
        stored["questions"][1]["answerType"] = "FUTURE_TYPE"
        stored["questions"][1].pop("numberRange")
        stored["questions"][0]["evidenceClasses"][0]["shape"] = "POLYGON"
        stored["questions"][0]["futureKey"] = 1
        record = DatasetVLMSettings.from_platform({**RECORD, "settings": stored})
        assert record.settings.questions[1].answer_type == "FUTURE_TYPE"
        assert record.settings.questions[0].evidence_classes[0].shape == "POLYGON"
        assert record.settings.questions[0].model_extra == {"futureKey": 1}
        assert _same(record.settings.to_payload()) == _same(stored)

    def test_version_prefers_updated_at(self):
        record = DatasetVLMSettings.from_platform({**RECORD, "updatedAt": "2026-10-21T01:02:03.456Z"})
        assert record.version == "2026-10-21T01:02:03.456Z"


# --- Platform errors --------------------------------------------------------------


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
        details = {"expectedUpdatedAt": T0, "currentUpdatedAt": "2026-10-21T00:00:00.000Z"}
        record = _read()
        with _platform_error("CONFLICT", details, "VLM settings changed since they were loaded."):
            with pytest.raises(ConflictError) as raised:
                VLMSettingsService().update_dataset_vlm_settings("dataset-1", record.settings, expected_updated_at=T0)
        assert raised.value.code == "CONFLICT"
        assert raised.value.details["currentUpdatedAt"] == "2026-10-21T00:00:00.000Z"
        assert isinstance(raised.value, UnknownError)

    def test_bad_request(self):
        with _platform_error("BAD_REQUEST", message="VLM settings can only be set on a VLM dataset."):
            with pytest.raises(InvalidInputError, match="only be set on a VLM dataset"):
                VLMSettingsService().create_dataset_vlm_settings("dataset-1", VLMSettings())

    def test_forbidden(self):
        with _platform_error("FORBIDDEN"):
            with pytest.raises(ForbiddenError):
                VLMSettingsService().delete_slice_vlm_settings("dataset-1", "slice-1")

    @pytest.mark.parametrize("resource", ["dataset", "slice", "vlmSettings"])
    def test_not_found_tells_what_is_missing(self, resource):
        with _platform_error("NOT_FOUND", {"resource": resource, "datasetId": "dataset-1"}):
            with pytest.raises(NotFoundError) as raised:
                VLMSettingsService().update_slice_vlm_settings("dataset-1", "slice-1", VLMSettings())
        assert raised.value.details["resource"] == resource
