"""VLM settings (question set) of a VLM dataset or slice.

The question set says which questions labelers answer for each data item, in
which answer format, and which evidence they mark. The platform keeps one for
a VLM dataset and may keep one per slice.

Rules the platform enforces (zenith ``vlmSettings``):

- Questions and evidence classes are only added, deleted or restored, never
  changed. Deleting moves them to ``deletedQuestions`` /
  ``deletedEvidenceClasses``. A question's text, answer type, options and
  number range, and an evidence class's name and shape, cannot change.
- IDs are ULIDs and are never reused.
- Only the reasoning guides, ``addedAt`` / ``deletedAt``, an evidence class's
  color and the order in a list can change.
"""
from enum import Enum
from typing import List, Optional, Union

from pydantic import ConfigDict

from spb_onprem.base_model import CustomBaseModel, Field


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


class _QuestionSetModel(CustomBaseModel):
    # Keep keys the SDK does not know when reading, so a newer platform does not
    # break reading. Writing checks the keys (check_vlm_settings).
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class VLMAnswerOption(_QuestionSetModel):
    """A choice of a SINGLE_CHOICE or MULTI_CHOICE question."""

    id: str = Field(..., description="ULID")
    label: str


class VLMNumberRange(_QuestionSetModel):
    """Allowed range of a NUMBER question. A missing bound means no bound."""

    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None


class VLMEvidenceClass(_QuestionSetModel):
    """An evidence class labelers mark for a question."""

    id: str = Field(..., description="ULID")
    name: str
    # An unknown value from a newer platform stays a str instead of failing.
    shape: Union[VLMEvidenceShape, str] = Field(..., union_mode="left_to_right")
    color: Optional[str] = Field(None, description="#RRGGBB, for the labeling screen; can change")
    added_at: Optional[str] = Field(None, alias="addedAt", description="ISO 8601 UTC")
    deleted_at: Optional[str] = Field(None, alias="deletedAt", description="ISO 8601 UTC")


class VLMQuestion(_QuestionSetModel):
    """A question of the question set."""

    id: str = Field(..., description="ULID")
    text: str
    # An unknown value from a newer platform stays a str instead of failing.
    answer_type: Union[VLMAnswerType, str] = Field(..., alias="answerType", union_mode="left_to_right")
    options: Optional[List[VLMAnswerOption]] = Field(None, description="Only for choice questions")
    number_range: Optional[VLMNumberRange] = Field(None, alias="numberRange", description="Only for NUMBER")
    reasoning_guide: Optional[str] = Field(
        None, alias="reasoningGuide", description="Added to the common reasoning guide"
    )
    evidence_classes: Optional[List[VLMEvidenceClass]] = Field(None, alias="evidenceClasses")
    deleted_evidence_classes: Optional[List[VLMEvidenceClass]] = Field(None, alias="deletedEvidenceClasses")
    added_at: Optional[str] = Field(None, alias="addedAt", description="ISO 8601 UTC")
    deleted_at: Optional[str] = Field(None, alias="deletedAt", description="ISO 8601 UTC")


class VLMQuestionSet(_QuestionSetModel):
    """The whole question set (the ``settings`` JSON)."""

    reasoning_guide: Optional[str] = Field(None, alias="reasoningGuide", description="Common reasoning guide")
    questions: Optional[List[VLMQuestion]] = None
    deleted_questions: Optional[List[VLMQuestion]] = Field(None, alias="deletedQuestions")


class _VLMSettingsRecord(CustomBaseModel):
    dataset_id: str = Field(..., alias="datasetId")
    settings: VLMQuestionSet
    created_at: str = Field(..., alias="createdAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    updated_by: Optional[str] = Field(None, alias="updatedBy")

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
