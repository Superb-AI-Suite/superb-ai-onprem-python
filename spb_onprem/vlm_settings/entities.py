"""VLM settings (question set) of a VLM dataset or slice.

Build them like the SDK filters: assemble the classes and pass them to the
service. New questions, options and evidence classes get their ``id`` (ULID)
and ``added_at`` from the SDK; you only write the content::

    VLMSettings(questions=[VLMQuestion(
        text="Does this object have a visible defect?",
        answer_type=VLMAnswerType.BOOLEAN,
        evidence_classes=[VLMEvidenceClass(name="defect", shape=VLMEvidenceShape.BOX)],
    )])

Rules the platform enforces (zenith ``vlmSettings``):

- Questions and evidence classes are only added, deleted or restored, never
  changed. Use the helpers (``add_question``, ``delete_question``,
  ``restore_question``, ``VLMQuestion.add_evidence_class`` ...): deleting moves
  an item to the deleted list with ``deleted_at``; restoring moves it back.
- Once saved, a question's ``id``, ``text``, ``answer_type``, ``options`` and
  ``number_range``, and an evidence class's ``id``, ``name`` and ``shape``,
  cannot change. Assigning them raises ``VLMSettingsChangeError``. Items not
  sent yet (just built or added) can still be changed.
- Set fields by their Python names (``answer_type``), not the camelCase
  aliases (``answerType``).
- What can change: the common and per-question ``reasoning_guide``, an
  evidence class's ``color`` and the order in a list.
"""
import os
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, ClassVar, Dict, FrozenSet, List, Optional, Union

from pydantic import ConfigDict, PrivateAttr, ValidationInfo, field_validator, model_validator

from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.exceptions import BadParameterError

_ULID_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

#: model_validate context key: the data comes from the platform, so nothing is filled in.
FROM_PLATFORM = "vlm_settings_from_platform"


def new_ulid() -> str:
    """A new ULID: 48-bit milliseconds + 80 random bits, Crockford base32.

    An identifier format, not a secret.
    """
    millis = int(time.time() * 1000)
    timestamp = ""
    for _ in range(10):
        timestamp = _ULID_ALPHABET[millis % 32] + timestamp
        millis //= 32
    randomness = "".join(_ULID_ALPHABET[byte % 32] for byte in os.urandom(16))
    return timestamp + randomness


def utc_now() -> str:
    """Now as the platform writes it: ISO 8601 UTC with milliseconds (2026-10-20T00:00:00.000Z)."""
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


class VLMSettingsValidationError(BadParameterError):
    """The question set breaks a platform rule; nothing was sent.

    Attributes:
        violations (List[str]): One message per problem.
    """

    def __init__(self, violations: List[str]):
        super().__init__("Invalid VLM settings: " + " ".join(violations))
        self.violations = violations


class VLMSettingsChangeError(VLMSettingsValidationError):
    """A change the platform does not allow (an unchangeable field, an unknown or already deleted id)."""


class VLMAnswerType(str, Enum):
    """Answer format of a question."""

    TEXT = "TEXT"
    SINGLE_CHOICE = "SINGLE_CHOICE"
    MULTI_CHOICE = "MULTI_CHOICE"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    STRUCTURED_CAPTION = "STRUCTURED_CAPTION"


class VLMEvidenceShape(str, Enum):
    """Spatial shape of an evidence. Time (range or point) is added for video."""

    BOX = "BOX"
    POINT = "POINT"
    NONE = "NONE"


class _SettingsModel(CustomBaseModel):
    # Keep keys the SDK does not know when reading, so a newer platform does not
    # break reading. Writing checks the keys.
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    #: Fields that cannot change once saved on the platform (platform rule).
    _FIXED: ClassVar[FrozenSet[str]] = frozenset()
    _WHAT: ClassVar[str] = "item"

    #: True once the item is saved (read from or sent to the platform).
    _locked: bool = PrivateAttr(False)

    @classmethod
    def _field_of_alias(cls, name: str) -> Optional[str]:
        for field_name, info in cls.model_fields.items():
            if info.alias and info.alias == name and info.alias != field_name:
                return field_name
        return None

    def __setattr__(self, name: str, value: Any) -> None:
        aliased = self._field_of_alias(name)
        field = aliased or name
        if field in self._FIXED and self._locked:
            raise VLMSettingsChangeError([
                f"{self._WHAT} {field} cannot change once saved (platform rule); "
                f"delete the {self._WHAT} and add a new one instead."
            ])
        if aliased:
            # With extra keys allowed, `q.answerType = ...` would add a second key instead of setting answer_type.
            raise VLMSettingsChangeError([f"set {aliased}, not the alias {name}."])
        super().__setattr__(name, value)

    def _lock(self) -> None:
        """Mark this item (and what it holds) as saved: its fixed fields cannot change any more."""
        self._locked = True
        for field_name in type(self).model_fields:
            value = getattr(self, field_name, None)
            items = value if isinstance(value, list) else [value]
            for item in items:
                if isinstance(item, _SettingsModel):
                    item._lock()

    def _set(self, name: str, value: Any) -> None:
        """Set a field from SDK code (helpers), skipping the guard."""
        super().__setattr__(name, value)

    @model_validator(mode="after")
    def _fill_added_at(self, info: ValidationInfo):
        """New items get ``added_at``; items read from the platform are left as they are."""
        if (
            "added_at" in type(self).model_fields
            and "added_at" not in self.model_fields_set
            and not (info.context or {}).get(FROM_PLATFORM)
        ):
            self._set("added_at", utc_now())
        return self


class VLMAnswerOption(_SettingsModel):
    """A choice of a SINGLE_CHOICE or MULTI_CHOICE question."""

    _FIXED: ClassVar[FrozenSet[str]] = frozenset({"id", "label"})
    _WHAT: ClassVar[str] = "option"

    id: str = Field(default_factory=new_ulid, description="ULID, filled in by the SDK")
    label: str


class VLMNumberRange(_SettingsModel):
    """Allowed range of a NUMBER question. A missing bound means no bound."""

    _FIXED: ClassVar[FrozenSet[str]] = frozenset({"min", "max"})
    _WHAT: ClassVar[str] = "numberRange"

    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None


class VLMEvidenceClass(_SettingsModel):
    """An evidence class labelers mark for a question."""

    _FIXED: ClassVar[FrozenSet[str]] = frozenset({"id", "name", "shape"})
    _WHAT: ClassVar[str] = "evidence class"

    id: str = Field(default_factory=new_ulid, description="ULID, filled in by the SDK")
    name: str
    # An unknown value from a newer platform stays a str instead of failing.
    shape: Union[VLMEvidenceShape, str] = Field(..., union_mode="left_to_right")
    color: Optional[str] = Field(None, description="#RRGGBB, for the labeling screen; can change")
    added_at: Optional[str] = Field(None, alias="addedAt", description="ISO 8601 UTC, filled in by the SDK")
    deleted_at: Optional[str] = Field(None, alias="deletedAt", description="Set by delete_evidence_class")


def _find(items: Optional[list], item_id: str):
    for index, item in enumerate(items or []):
        if item.id == item_id:
            return index, item
    return None, None


class VLMQuestion(_SettingsModel):
    """A question of the question set.

    ``options`` takes ``VLMAnswerOption`` objects or plain labels
    (``options=["Yes", "No"]``).
    """

    _FIXED: ClassVar[FrozenSet[str]] = frozenset({"id", "text", "answer_type", "options", "number_range"})
    _WHAT: ClassVar[str] = "question"

    id: str = Field(default_factory=new_ulid, description="ULID, filled in by the SDK")
    text: str
    # An unknown value from a newer platform stays a str instead of failing.
    answer_type: Union[VLMAnswerType, str] = Field(..., alias="answerType", union_mode="left_to_right")
    options: Optional[List[VLMAnswerOption]] = Field(None, description="Only for choice questions")
    number_range: Optional[VLMNumberRange] = Field(None, alias="numberRange", description="Only for NUMBER")
    reasoning_guide: Optional[str] = Field(
        None, alias="reasoningGuide", description="Added to the common reasoning guide; can change"
    )
    evidence_classes: List[VLMEvidenceClass] = Field(default_factory=list, alias="evidenceClasses")
    deleted_evidence_classes: List[VLMEvidenceClass] = Field(default_factory=list, alias="deletedEvidenceClasses")
    added_at: Optional[str] = Field(None, alias="addedAt", description="ISO 8601 UTC, filled in by the SDK")
    deleted_at: Optional[str] = Field(None, alias="deletedAt", description="Set by delete_question")

    _restored_deleted_at: Dict[str, str] = PrivateAttr(default_factory=dict)

    @field_validator("options", mode="before")
    @classmethod
    def _labels_to_options(cls, value):
        if isinstance(value, list):
            return [{"label": item} if isinstance(item, str) else item for item in value]
        return value

    @field_validator("evidence_classes", "deleted_evidence_classes", mode="before")
    @classmethod
    def _none_to_list(cls, value):
        return [] if value is None else value

    # Evidence classes ------------------------------------------------------
    def get_evidence_class(self, class_id: str) -> VLMEvidenceClass:
        """The evidence class with this id, current or deleted."""
        for items in (self.evidence_classes, self.deleted_evidence_classes):
            _, item = _find(items, class_id)
            if item is not None:
                return item
        raise VLMSettingsChangeError([f"question {self.id} has no evidence class {class_id}."])

    def add_evidence_class(
        self,
        evidence_class: Optional[VLMEvidenceClass] = None,
        *,
        name: Optional[str] = None,
        shape: Union[VLMEvidenceShape, str, None] = None,
        color: Optional[str] = None,
    ) -> VLMEvidenceClass:
        """Add an evidence class (an object, or ``name`` and ``shape``). Returns it."""
        if evidence_class is None:
            if name is None or shape is None:
                raise VLMSettingsChangeError(["add_evidence_class needs an evidence class, or name and shape."])
            evidence_class = VLMEvidenceClass(name=name, shape=shape, color=color)
        elif name is not None or shape is not None or color is not None:
            raise VLMSettingsChangeError(["Pass an evidence class or name/shape/color, not both."])
        taken = {item.name.strip().lower() for item in self.evidence_classes}
        if evidence_class.name.strip().lower() in taken:
            raise VLMSettingsChangeError([f'question {self.id} already has an evidence class "{evidence_class.name}".'])
        _, existing = _find(self.evidence_classes + self.deleted_evidence_classes, evidence_class.id)
        if existing is not None:
            raise VLMSettingsChangeError([f"evidence class id {evidence_class.id} is already used."])
        self.evidence_classes.append(evidence_class)
        return evidence_class

    def delete_evidence_class(self, class_id: str) -> VLMEvidenceClass:
        """Move an evidence class to ``deleted_evidence_classes`` with ``deleted_at``."""
        index, item = _find(self.evidence_classes, class_id)
        if item is None:
            if _find(self.deleted_evidence_classes, class_id)[1] is not None:
                raise VLMSettingsChangeError([f"evidence class {class_id} is already deleted."])
            raise VLMSettingsChangeError([f"question {self.id} has no evidence class {class_id}."])
        self.evidence_classes.pop(index)
        item._set("deleted_at", self._restored_deleted_at.pop(class_id, None) or utc_now())
        self.deleted_evidence_classes.append(item)
        return item

    def restore_evidence_class(self, class_id: str) -> VLMEvidenceClass:
        """Move a deleted evidence class back to ``evidence_classes``."""
        index, item = _find(self.deleted_evidence_classes, class_id)
        if item is None:
            if _find(self.evidence_classes, class_id)[1] is not None:
                raise VLMSettingsChangeError([f"evidence class {class_id} is not deleted."])
            raise VLMSettingsChangeError([f"question {self.id} has no evidence class {class_id}."])
        if item.name.strip().lower() in {other.name.strip().lower() for other in self.evidence_classes}:
            raise VLMSettingsChangeError([
                f'question {self.id} already has an evidence class "{item.name}"; delete that one first.'
            ])
        self.deleted_evidence_classes.pop(index)
        if item.deleted_at:
            # Deleting it again in this edit keeps the original time, like the web app.
            self._restored_deleted_at[class_id] = item.deleted_at
        item._set("deleted_at", None)
        self.evidence_classes.append(item)
        return item

    def set_evidence_class_color(self, class_id: str, color: Optional[str]) -> VLMEvidenceClass:
        """Change the display color (#RRGGBB) of an evidence class. The only class field that can change."""
        item = self.get_evidence_class(class_id)
        item.color = color
        return item


class VLMSettings(_SettingsModel):
    """The whole question set (the ``settings`` of a dataset or slice).

    Read it with ``get_*_vlm_settings``, change it with the helpers, and pass
    it to ``update_*_vlm_settings``; the SDK checks the change before sending.
    """

    reasoning_guide: Optional[str] = Field(None, alias="reasoningGuide", description="Common reasoning guide")
    questions: List[VLMQuestion] = Field(default_factory=list)
    deleted_questions: List[VLMQuestion] = Field(default_factory=list, alias="deletedQuestions")

    #: The settings as the platform stored them (set when read), to check a change before sending.
    _saved: Optional[Dict[str, Any]] = PrivateAttr(None)
    _restored_deleted_at: Dict[str, str] = PrivateAttr(default_factory=dict)

    @field_validator("questions", "deleted_questions", mode="before")
    @classmethod
    def _none_to_list(cls, value):
        return [] if value is None else value

    def to_payload(self) -> Dict[str, Any]:
        """The ``settings`` JSON to send (camelCase keys, no null values)."""
        return self.model_dump(mode="json", by_alias=True, exclude_none=True)

    def _mark_saved(self) -> None:
        """Remember these settings as stored on the platform and lock their items."""
        self._saved = self.to_payload()
        self._lock()

    # Questions -------------------------------------------------------------
    def get_question(self, question_id: str) -> VLMQuestion:
        """The question with this id, current or deleted."""
        for items in (self.questions, self.deleted_questions):
            _, item = _find(items, question_id)
            if item is not None:
                return item
        raise VLMSettingsChangeError([f"there is no question {question_id}."])

    def add_question(
        self,
        question: Optional[VLMQuestion] = None,
        **fields: Any,
    ) -> VLMQuestion:
        """Add a question (an object, or its fields: ``text``, ``answer_type``, ...). Returns it."""
        if question is None:
            question = VLMQuestion(**fields)
        elif fields:
            raise VLMSettingsChangeError(["Pass a question or its fields, not both."])
        if _find(self.questions + self.deleted_questions, question.id)[1] is not None:
            raise VLMSettingsChangeError([f"question id {question.id} is already used."])
        self.questions.append(question)
        return question

    def delete_question(self, question_id: str) -> VLMQuestion:
        """Move a question to ``deleted_questions`` with ``deleted_at``."""
        index, item = _find(self.questions, question_id)
        if item is None:
            if _find(self.deleted_questions, question_id)[1] is not None:
                raise VLMSettingsChangeError([f"question {question_id} is already deleted."])
            raise VLMSettingsChangeError([f"there is no question {question_id}."])
        self.questions.pop(index)
        item._set("deleted_at", self._restored_deleted_at.pop(question_id, None) or utc_now())
        self.deleted_questions.append(item)
        return item

    def restore_question(self, question_id: str) -> VLMQuestion:
        """Move a deleted question back to ``questions``."""
        index, item = _find(self.deleted_questions, question_id)
        if item is None:
            if _find(self.questions, question_id)[1] is not None:
                raise VLMSettingsChangeError([f"question {question_id} is not deleted."])
            raise VLMSettingsChangeError([f"there is no question {question_id}."])
        self.deleted_questions.pop(index)
        if item.deleted_at:
            # Deleting it again in this edit keeps the original time, like the web app.
            self._restored_deleted_at[question_id] = item.deleted_at
        item._set("deleted_at", None)
        self.questions.append(item)
        return item


class _VLMSettingsRecord(CustomBaseModel):
    dataset_id: str = Field(..., alias="datasetId")
    settings: VLMSettings
    created_at: str = Field(..., alias="createdAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    updated_by: Optional[str] = Field(None, alias="updatedBy")

    @classmethod
    def from_platform(cls, data: Dict[str, Any]):
        """Read a record the platform sent: nothing is filled in, and the stored
        settings are kept to check a later update."""
        record = cls.model_validate(data, context={FROM_PLATFORM: True})
        record.settings._mark_saved()
        return record

    @property
    def version(self) -> str:
        """The version to send as ``expected_updated_at`` when updating or deleting.

        It is ``updatedAt``, or ``createdAt`` when the settings were never
        updated, exactly as the platform sent it.
        """
        return self.updated_at or self.created_at


class DatasetVLMSettings(_VLMSettingsRecord):
    """The question set of a VLM dataset."""


class SliceVLMSettings(_VLMSettingsRecord):
    """The question set of a slice of a VLM dataset."""

    slice_id: str = Field(..., alias="sliceId")
