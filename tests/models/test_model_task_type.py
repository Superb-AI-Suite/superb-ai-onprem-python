from spb_onprem import ModelTaskType as TopLevelModelTaskType
from spb_onprem.models.entities import Model
from spb_onprem.models.enums import ModelTaskType
from spb_onprem.models.params.create_model import create_model_params


def test_model_task_type_values():
    assert [t.value for t in ModelTaskType] == [
        "OBJECT_DETECTION",
        "INSTANCE_SEGMENTATION",
        "OCR",
        "VLM",
    ]
    assert TopLevelModelTaskType is ModelTaskType


def test_vlm_task_type_value():
    assert ModelTaskType.VLM.value == "VLM"
    assert ModelTaskType("VLM") is ModelTaskType.VLM


def test_create_model_params_with_vlm_task_type():
    params = create_model_params(dataset_id="dataset-1", name="vlm-model", task_type=ModelTaskType.VLM)
    assert params["task_type"] == "VLM"


def test_model_entity_parses_vlm_task_type():
    model = Model.model_validate({"id": "model-1", "taskType": "VLM"})
    assert model.task_type is ModelTaskType.VLM
