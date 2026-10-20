# VLM Settings (question set)

`VLMSettingsService` reads and writes the question set of a **VLM dataset** and of its slices:
the questions labelers answer, the answer format, the evidence classes they mark and the
reasoning guides. These are the same calls the web app makes.

```python
from spb_onprem import (
    VLMSettingsService, VLMQuestionSet, VLMQuestion, VLMAnswerOption, VLMEvidenceClass,
    VLMAnswerType, VLMEvidenceShape,
)
from spb_onprem.exceptions import ConflictError

service = VLMSettingsService()

question_set = VLMQuestionSet(
    reasoning_guide="Look at the whole clip before answering.",
    questions=[
        VLMQuestion(
            id="01JABCDEFGHJKMNPQRSTVWXYZ0",          # ULID, never reused
            text="Is the robot holding an object?",
            answer_type=VLMAnswerType.SINGLE_CHOICE,
            options=[
                VLMAnswerOption(id="01JABCDEFGHJKMNPQRSTVWXYZ1", label="Yes"),
                VLMAnswerOption(id="01JABCDEFGHJKMNPQRSTVWXYZ2", label="No"),
            ],
            reasoning_guide="Check the gripper.",
            evidence_classes=[
                VLMEvidenceClass(id="01JABCDEFGHJKMNPQRSTVWXYZ3", name="gripper",
                                 shape=VLMEvidenceShape.BOX, color="#FF0000"),
            ],
        ),
    ],
    deleted_questions=[],
)

# Dataset question set (only on a VLM dataset; fails with ConflictError if one exists)
record = service.create_dataset_vlm_settings("dataset_123", question_set)

# A slice gets its own set; the platform never copies it. Create it from what you read.
current = service.get_dataset_vlm_settings("dataset_123")      # None when there is none
service.create_slice_vlm_settings("dataset_123", "slice_456", current.settings)

# Update: send the whole set and the version you read (optimistic lock)
settings = current.settings.model_dump(by_alias=True, exclude_unset=True)
settings["reasoningGuide"] = "Answer in one sentence."
try:
    service.update_dataset_vlm_settings("dataset_123", settings, expected_updated_at=current.version)
except ConflictError as error:
    print("Changed since read:", error.details)               # read again and retry

# Delete the whole set (a new one can be created afterwards)
service.delete_slice_vlm_settings("dataset_123", "slice_456")
```

## Functions

| Function | Returns |
| --- | --- |
| `get_dataset_vlm_settings(dataset_id)` | `DatasetVLMSettings` or `None` |
| `create_dataset_vlm_settings(dataset_id, settings)` | `DatasetVLMSettings` |
| `update_dataset_vlm_settings(dataset_id, settings, expected_updated_at=None)` | `DatasetVLMSettings` |
| `delete_dataset_vlm_settings(dataset_id, expected_updated_at=None)` | `bool` |
| `get_slice_vlm_settings(dataset_id, slice_id)` | `SliceVLMSettings` or `None` |
| `create_slice_vlm_settings(dataset_id, slice_id, settings)` | `SliceVLMSettings` |
| `update_slice_vlm_settings(dataset_id, slice_id, settings, expected_updated_at=None)` | `SliceVLMSettings` |
| `delete_slice_vlm_settings(dataset_id, slice_id, expected_updated_at=None)` | `bool` |

`settings` is a `VLMQuestionSet` or a dict with the camelCase keys
(`reasoningGuide`, `questions`, `deletedQuestions`). A record's `version` is `updatedAt`, or
`createdAt` when never updated; pass it as `expected_updated_at`. Leaving it out skips the check.

## Rules

- Answer types: `TEXT`, `SINGLE_CHOICE`, `MULTI_CHOICE` (need `options`), `NUMBER`
  (optional `numberRange {min, max}`), `BOOLEAN`, `STRUCTURED_CAPTION`.
- Evidence shapes: `BOX`, `POINT`, `NONE`. `color` is `#RRGGBB`.
- Questions and evidence classes are only added, deleted (moved to `deletedQuestions` /
  `deletedEvidenceClasses`) or restored. Text, answer type, options, number range, and a class's
  name and shape never change. IDs are ULIDs and are never reused.
- Unknown keys are refused. The SDK checks the shape before sending
  (`VLMSettingsValidationError`, a `BadParameterError`, with `.violations`). Sizes and the
  add/delete/restore rule are checked by the platform.

## Errors from the platform

| Exception | When |
| --- | --- |
| `InvalidInputError` | Not a VLM dataset, invalid settings or sizes, or an update that changes an existing question or class |
| `ConflictError` | A set already exists (create), or it changed since `expected_updated_at` (update, delete). `details` has `expectedUpdatedAt` and `currentUpdatedAt` |
| `NotFoundError` | `details["resource"]` is `"dataset"`, `"slice"` or `"vlmSettings"` |
| `ForbiddenError` | The caller may not edit them |

All of them except `NotFoundError` are `UnknownError` subclasses with `.code` and `.details`.
