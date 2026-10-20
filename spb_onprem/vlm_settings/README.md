# VLM Settings (question set)

`VLMSettingsService` reads and writes the question set of a **VLM dataset** and of its slices:
the questions labelers answer, the answer format, the evidence classes they mark and the
reasoning guides. These are the same calls the web app makes.

Build the settings like an SDK filter: assemble the classes and pass them to the service.
The SDK fills in the `id` (ULID) and `added_at` of new questions, options and evidence classes.

## Create

```python
from spb_onprem import (
    VLMSettingsService, VLMSettings, VLMQuestion, VLMEvidenceClass,
    VLMAnswerType, VLMEvidenceShape, VLMNumberRange,
)

service = VLMSettingsService()

settings = VLMSettings(
    reasoning_guide="Look at the whole clip before answering.",
    questions=[
        VLMQuestion(
            text="Does this object have a visible defect?",
            answer_type=VLMAnswerType.BOOLEAN,
            evidence_classes=[VLMEvidenceClass(name="defect", shape=VLMEvidenceShape.BOX)],
        ),
        VLMQuestion(
            text="Which part is damaged?",
            answer_type=VLMAnswerType.SINGLE_CHOICE,
            options=["Lid", "Body", "Label"],            # labels; ids are filled in
            reasoning_guide="Pick the part with the largest damage.",
        ),
        VLMQuestion(
            text="How many scratches?",
            answer_type=VLMAnswerType.NUMBER,
            number_range=VLMNumberRange(min=0, max=50),
        ),
    ],
)

record = service.create_dataset_vlm_settings("dataset_123", settings)   # only on a VLM dataset

# A slice gets its own set; the platform never copies it. Create it from what you read.
dataset_record = service.get_dataset_vlm_settings("dataset_123")        # None when there is none
service.create_slice_vlm_settings("dataset_123", "slice_456", dataset_record.settings)
```

## Edit: read, change with helpers, update once

The platform only lets you **add, delete or restore** questions and evidence classes. The helpers
do the moving between lists and the `deleted_at` time for you:

```python
from spb_onprem.exceptions import ConflictError

record = service.get_dataset_vlm_settings("dataset_123")
settings = record.settings

settings.add_question(text="Is the label readable?", answer_type=VLMAnswerType.BOOLEAN)
settings.delete_question(old_question_id)        # -> deleted_questions, with deleted_at
settings.restore_question(deleted_question_id)   # -> back to questions

question = settings.get_question(question_id)
question.add_evidence_class(name="scratch", shape=VLMEvidenceShape.BOX, color="#FF8800")
question.delete_evidence_class(class_id)
question.restore_evidence_class(deleted_class_id)
question.set_evidence_class_color(class_id, "#00AAFF")   # color can change

question.reasoning_guide = "Check the edges first."      # guides can change
settings.reasoning_guide = "Answer in one sentence."

try:
    record = service.update_dataset_vlm_settings(
        "dataset_123", settings, expected_updated_at=record.version,   # optimistic lock
    )
except ConflictError as error:
    print("Someone saved in between:", error.details)                # read again and redo
```

The returned record is ready for the next edit. The same works for a slice
(`get_slice_vlm_settings` → helpers → `update_slice_vlm_settings`).

### What cannot change

A question's `id`, `text`, `answer_type`, `options` and `number_range`, and an evidence
class's `id`, `name` and `shape`, are fixed once created (labels already point at them).
Assigning one raises `VLMSettingsChangeError` with the reason. Changing them in place
(for example `question.options.append(...)`), removing a question or class from its list,
or moving a class to another question is caught by `update_*` before sending, against the
settings that were read. To change a question, delete it and add a new one.

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

| Helper | On |
| --- | --- |
| `add_question(question=None, **fields)`, `delete_question(id)`, `restore_question(id)`, `get_question(id)` | `VLMSettings` |
| `add_evidence_class(evidence_class=None, *, name, shape, color)`, `delete_evidence_class(id)`, `restore_evidence_class(id)`, `set_evidence_class_color(id, color)`, `get_evidence_class(id)` | `VLMQuestion` |

`settings` is a `VLMSettings`, like the SDK filters take their filter class; for a dict use
`VLMSettings.model_validate(data)`. A record's `version` is `updatedAt`, or `createdAt` when
never updated; pass it as `expected_updated_at`. Leaving it out skips the check.

## Rules

- Answer types: `TEXT`, `SINGLE_CHOICE`, `MULTI_CHOICE` (need `options`), `NUMBER`
  (optional `number_range`), `BOOLEAN`, `STRUCTURED_CAPTION`.
- Evidence shapes: `BOX`, `POINT`, `NONE`. `color` is `#RRGGBB`.
- IDs are ULIDs and are never reused; option labels and evidence class names are unique
  in a question (case-insensitive).
- Unknown keys are refused. The SDK checks the shape before sending
  (`VLMSettingsValidationError`, a `BadParameterError`, with `.violations`); sizes are checked by
  the platform.

## Errors from the platform

| Exception | When |
| --- | --- |
| `InvalidInputError` | Not a VLM dataset, invalid settings or sizes, or an update that changes an existing question or class |
| `ConflictError` | A set already exists (create), or it changed since `expected_updated_at` (update, delete). `details` has `expectedUpdatedAt` and `currentUpdatedAt` |
| `NotFoundError` | `details["resource"]` is `"dataset"`, `"slice"` or `"vlmSettings"` |
| `ForbiddenError` | The caller may not edit them |

All of them except `NotFoundError` are `UnknownError` subclasses with `.code` and `.details`.
