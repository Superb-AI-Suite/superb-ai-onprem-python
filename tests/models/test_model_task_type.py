import json

import pytest

from spb_onprem import ModelTaskType as TopLevelModelTaskType
from spb_onprem.models.entities import Model
from spb_onprem.models.enums import ModelTaskType
from spb_onprem.models.params.create_model import create_model_params
from spb_onprem.models.params.get_models import get_models_params
from spb_onprem.models.params.models import ModelFilter, ModelFilterOptions
from spb_onprem.models.params.update_model import update_model_params


TASK_TYPES = ("VLM", "VISION_GENERATION")


def test_model_task_type_values():
    assert [t.value for t in ModelTaskType] == [
        "OBJECT_DETECTION",
        "INSTANCE_SEGMENTATION",
        "OCR",
        "VLM",
        "VISION_GENERATION",
    ]
    assert TopLevelModelTaskType is ModelTaskType


@pytest.mark.parametrize("task_type", TASK_TYPES)
def test_model_task_type_value(task_type):
    assert ModelTaskType[task_type].value == task_type
    assert ModelTaskType(task_type) is ModelTaskType[task_type]


@pytest.mark.parametrize("task_type", TASK_TYPES)
def test_create_model_params_with_task_type(task_type):
    params = create_model_params(
        dataset_id="dataset-1", name="test-model", task_type=ModelTaskType(task_type)
    )
    assert params["task_type"] == task_type


@pytest.mark.parametrize("task_type", TASK_TYPES)
def test_update_model_params_with_task_type(task_type):
    params = update_model_params(
        dataset_id="dataset-1", model_id="model-1", task_type=ModelTaskType(task_type)
    )
    assert params["task_type"] == task_type


@pytest.mark.parametrize("task_type", TASK_TYPES)
def test_get_models_params_serializes_task_type_filter(task_type):
    model_filter = ModelFilter(must=ModelFilterOptions(taskTypeIn=[task_type]))
    params = get_models_params(dataset_id="dataset-1", filter=model_filter)
    assert json.loads(json.dumps(params))["filter"]["must"]["taskTypeIn"] == [task_type]


@pytest.mark.parametrize("task_type", TASK_TYPES)
def test_model_entity_parses_task_type(task_type):
    model = Model.model_validate({"id": "model-1", "taskType": task_type})
    assert model.task_type is ModelTaskType(task_type)
