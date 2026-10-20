"""Variables and client-side checks for the VLM settings queries."""
import copy
import math
import re
from typing import Any, Dict, List, Mapping, Optional, Union

from pydantic import BaseModel

from spb_onprem.exceptions import BadParameterError

from .entities import VLMAnswerType, VLMEvidenceShape, VLMQuestionSet

ULID_PATTERN = re.compile(r"^[0-7][0-9A-HJKMNP-TV-Z]{25}$")
ISO_UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,3})?Z$")
HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")

#: Keys the platform accepts; any other key is refused (zenith vlmSettings).
SETTINGS_KEYS = frozenset({"reasoningGuide", "questions", "deletedQuestions"})
QUESTION_KEYS = frozenset({
    "id", "text", "answerType", "options", "numberRange", "reasoningGuide",
    "evidenceClasses", "deletedEvidenceClasses", "addedAt", "deletedAt",
})
OPTION_KEYS = frozenset({"id", "label"})
EVIDENCE_CLASS_KEYS = frozenset({"id", "name", "shape", "color", "addedAt", "deletedAt"})
NUMBER_RANGE_KEYS = frozenset({"min", "max"})
CHOICE_ANSWER_TYPES = frozenset({VLMAnswerType.SINGLE_CHOICE.value, VLMAnswerType.MULTI_CHOICE.value})
ANSWER_TYPES = frozenset(item.value for item in VLMAnswerType)
EVIDENCE_SHAPES = frozenset(item.value for item in VLMEvidenceShape)


class VLMSettingsValidationError(BadParameterError):
    """The question set breaks a platform rule; nothing was sent.

    Attributes:
        violations (List[str]): One message per problem.
    """

    def __init__(self, violations: List[str]):
        super().__init__("Invalid VLM settings: " + " ".join(violations))
        self.violations = violations


def _non_empty(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def collect_vlm_settings_violations(settings: Any) -> List[str]:
    """Problems the platform would refuse, found before sending.

    This covers the shape of the question set: keys, IDs, answer types,
    options, number ranges, evidence classes and timestamps. The platform also
    checks sizes and that an update only adds, deletes or restores (see
    ``VLMQuestionSet``); those come back as ``InvalidInputError``.
    """
    if not isinstance(settings, Mapping):
        return ["settings must be an object."]
    violations: List[str] = []
    seen_ids: set = set()

    def check_keys(obj: Mapping, allowed: frozenset, where: str) -> None:
        for key in obj:
            if key not in allowed:
                violations.append(f'{where}: unknown key "{key}".')

    def check_id(value: Any, where: str) -> None:
        if not isinstance(value, str) or not ULID_PATTERN.match(value):
            violations.append(f"{where}: id must be a ulid.")
            return
        if value in seen_ids:
            violations.append(f"{where}: id {value} is used more than once.")
        seen_ids.add(value)

    def check_timestamp(value: Any, field: str, where: str) -> None:
        if value is None:
            return
        if not isinstance(value, str) or not ISO_UTC_PATTERN.match(value):
            violations.append(f"{where}: {field} must be an ISO 8601 UTC timestamp (e.g. 2026-10-15T00:00:00.000Z).")

    def check_optional_string(value: Any, field: str, where: str) -> None:
        if value is not None and not isinstance(value, str):
            violations.append(f"{where}: {field} must be a string.")

    def check_classes(items: Any, field: str, where: str, unique_names: bool) -> None:
        if items is None:
            return
        if not isinstance(items, list):
            violations.append(f"{where}: {field} must be an array.")
            return
        names = set()
        for index, item in enumerate(items):
            at = f"{where}.{field}[{index}]"
            if not isinstance(item, Mapping):
                violations.append(f"{at}: must be an object.")
                continue
            check_keys(item, EVIDENCE_CLASS_KEYS, at)
            check_id(item.get("id"), at)
            name = item.get("name")
            if not _non_empty(name):
                violations.append(f"{at}: name must be a non-empty string.")
            elif unique_names:
                key = name.strip().lower()
                if key in names:
                    violations.append(f'{at}: name "{name}" is duplicated.')
                names.add(key)
            if item.get("shape") not in EVIDENCE_SHAPES:
                violations.append(f'{at}: unknown shape "{item.get("shape")}".')
            color = item.get("color")
            if "color" in item and not (isinstance(color, str) and HEX_COLOR_PATTERN.match(color)):
                violations.append(f"{at}: color must be a #RRGGBB hex string.")
            check_timestamp(item.get("addedAt"), "addedAt", at)
            check_timestamp(item.get("deletedAt"), "deletedAt", at)

    def check_question(question: Any, where: str) -> None:
        if not isinstance(question, Mapping):
            violations.append(f"{where}: must be an object.")
            return
        label = f"{where} ({question['id']})" if isinstance(question.get("id"), str) else where
        check_keys(question, QUESTION_KEYS, label)
        check_id(question.get("id"), label)
        if not _non_empty(question.get("text")):
            violations.append(f"{label}: text must be a non-empty string.")
        answer_type = question.get("answerType")
        if answer_type not in ANSWER_TYPES:
            violations.append(f'{label}: unknown answerType "{answer_type}".')
        options = question.get("options")
        if answer_type in CHOICE_ANSWER_TYPES:
            if not isinstance(options, list) or not options:
                violations.append(f"{label}: choice questions need at least one option.")
        elif isinstance(options, list) and options:
            violations.append(f"{label}: options are only allowed on choice questions.")
        if options is not None and not isinstance(options, list):
            violations.append(f"{label}: options must be an array.")
        if isinstance(options, list):
            labels = set()
            for index, option in enumerate(options):
                at = f"{label}.options[{index}]"
                if not isinstance(option, Mapping):
                    violations.append(f"{at}: must be an object.")
                    continue
                check_keys(option, OPTION_KEYS, at)
                check_id(option.get("id"), at)
                text = option.get("label")
                if not _non_empty(text):
                    violations.append(f"{at}: label must be a non-empty string.")
                    continue
                key = text.strip().lower()
                if key in labels:
                    violations.append(f'{at}: label "{text}" is duplicated.')
                labels.add(key)
        number_range = question.get("numberRange")
        if number_range is not None:
            if answer_type != VLMAnswerType.NUMBER.value:
                violations.append(f"{label}: numberRange is only allowed on NUMBER questions.")
            if not isinstance(number_range, Mapping):
                violations.append(f"{label}: numberRange must be an object.")
            else:
                check_keys(number_range, NUMBER_RANGE_KEYS, f"{label}.numberRange")
                bounds = {}
                for bound in ("min", "max"):
                    value = number_range.get(bound)
                    if value is None:
                        continue
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                        violations.append(f"{label}: numberRange.{bound} must be a finite number.")
                    else:
                        bounds[bound] = value
                if "min" in bounds and "max" in bounds and bounds["min"] > bounds["max"]:
                    violations.append(f"{label}: numberRange.min must not be greater than max.")
        check_optional_string(question.get("reasoningGuide"), "reasoningGuide", label)
        check_classes(question.get("evidenceClasses"), "evidenceClasses", label, True)
        check_classes(question.get("deletedEvidenceClasses"), "deletedEvidenceClasses", label, False)
        check_timestamp(question.get("addedAt"), "addedAt", label)
        check_timestamp(question.get("deletedAt"), "deletedAt", label)

    check_keys(settings, SETTINGS_KEYS, "settings")
    check_optional_string(settings.get("reasoningGuide"), "reasoningGuide", "settings")
    for field in ("questions", "deletedQuestions"):
        items = settings.get(field)
        if items is None:
            continue
        if not isinstance(items, list):
            violations.append(f"settings.{field} must be an array.")
            continue
        for index, question in enumerate(items):
            check_question(question, f"{field}[{index}]")
    return violations


def vlm_settings_payload(settings: Union[VLMQuestionSet, Mapping[str, Any]]) -> Dict[str, Any]:
    """The ``settings`` JSON to send, checked.

    A ``VLMQuestionSet`` is sent with its camelCase keys and only the fields
    that were set. A dict is sent as it is (it must use the camelCase keys).

    Raises:
        VLMSettingsValidationError: If the question set breaks a platform rule.
    """
    if isinstance(settings, BaseModel):
        payload = settings.model_dump(mode="json", by_alias=True, exclude_unset=True)
    elif isinstance(settings, Mapping):
        payload = copy.deepcopy(dict(settings))
    else:
        raise VLMSettingsValidationError(["settings must be an object (a VLMQuestionSet or a dict)."])
    violations = collect_vlm_settings_violations(payload)
    if violations:
        raise VLMSettingsValidationError(violations)
    return payload


def _require(value: Optional[str], name: str) -> str:
    if value is None or (isinstance(value, str) and not value.strip()):
        raise BadParameterError(f"{name} is required.")
    return value


def dataset_vlm_settings_params(dataset_id: str) -> dict:
    return {"datasetId": _require(dataset_id, "dataset_id")}


def slice_vlm_settings_params(dataset_id: str, slice_id: str) -> dict:
    return {"datasetId": _require(dataset_id, "dataset_id"), "sliceId": _require(slice_id, "slice_id")}


def create_dataset_vlm_settings_params(dataset_id: str, settings: Any) -> dict:
    return {**dataset_vlm_settings_params(dataset_id), "settings": vlm_settings_payload(settings)}


def create_slice_vlm_settings_params(dataset_id: str, slice_id: str, settings: Any) -> dict:
    return {**slice_vlm_settings_params(dataset_id, slice_id), "settings": vlm_settings_payload(settings)}


def _with_version(params: dict, expected_updated_at: Optional[str]) -> dict:
    if expected_updated_at is not None:
        if not isinstance(expected_updated_at, str) or not expected_updated_at.strip():
            raise BadParameterError("expected_updated_at must be the version string the platform sent.")
        params["expectedUpdatedAt"] = expected_updated_at
    return params


def update_dataset_vlm_settings_params(
    dataset_id: str, settings: Any, expected_updated_at: Optional[str] = None
) -> dict:
    return _with_version(create_dataset_vlm_settings_params(dataset_id, settings), expected_updated_at)


def update_slice_vlm_settings_params(
    dataset_id: str, slice_id: str, settings: Any, expected_updated_at: Optional[str] = None
) -> dict:
    return _with_version(create_slice_vlm_settings_params(dataset_id, slice_id, settings), expected_updated_at)


def delete_dataset_vlm_settings_params(dataset_id: str, expected_updated_at: Optional[str] = None) -> dict:
    return _with_version(dataset_vlm_settings_params(dataset_id), expected_updated_at)


def delete_slice_vlm_settings_params(
    dataset_id: str, slice_id: str, expected_updated_at: Optional[str] = None
) -> dict:
    return _with_version(slice_vlm_settings_params(dataset_id, slice_id), expected_updated_at)
