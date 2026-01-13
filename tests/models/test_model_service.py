import os
import uuid

import pytest
from unittest.mock import Mock

from spb_onprem.base_types import Undefined
from spb_onprem.models.service import ModelService
from spb_onprem.models.queries import Queries
from spb_onprem.models.entities import Model
from spb_onprem.models.enums import ModelTaskType, ModelStatus
from spb_onprem.trainingreports.entities import TrainingReport
from spb_onprem.exceptions import BadParameterError, NotFoundError


def _print_step(title: str, payload=None):
    print(f"\n=== {title} ===")
    if payload is not None:
        print(payload)


def _precheck_real_test(required_env=None, optional_env=None):
    required_env = required_env or []
    optional_env = optional_env or []

    config_file_path = os.path.expanduser("~/.spb/onprem-config")
    host_from_env = os.environ.get("SUNRISE_SERVER_URL") or os.environ.get("SUPERB_SYSTEM_SDK_HOST")
    has_config_file = os.path.exists(config_file_path)

    missing = [k for k in required_env if not os.environ.get(k)]

    env_snapshot = {k: os.environ.get(k) for k in (required_env + optional_env)}
    _print_step(
        "Precheck env",
        {
            "required_env": required_env,
            "missing_env": missing,
            "env": env_snapshot,
            "host_from_env": host_from_env,
            "config_file": config_file_path,
            "config_file_exists": has_config_file,
        },
    )

    if not host_from_env and not has_config_file:
        pytest.skip(
            "Missing GraphQL host config. Set SUNRISE_SERVER_URL (or SUPERB_SYSTEM_SDK_HOST) or create ~/.spb/onprem-config"
        )

    if missing:
        pytest.skip(f"Missing required env: {', '.join(missing)}")


class TestModelService:
    def setup_method(self):
        self.service = ModelService()
        self.service.request_gql = Mock()

    def test_get_model_missing_dataset_id(self):
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.service.get_model(dataset_id=None, model_id="m1")

    def test_get_model_missing_model_id(self):
        with pytest.raises(BadParameterError, match="model_id is required"):
            self.service.get_model(dataset_id="d1", model_id=None)

    def test_get_model_success(self):
        dataset_id = "d1"
        model_id = "m1"

        self.service.request_gql.return_value = {
            "id": model_id,
            "datasetId": dataset_id,
            "name": "model-name",
            "trainingReport": {
                "id": "tr1",
                "name": "report",
                "modelId": model_id,
                "contentId": "c1",
                "description": None,
            },
        }

        result = self.service.get_model(dataset_id=dataset_id, model_id=model_id)

        assert isinstance(result, Model)
        assert result.id == model_id
        assert result.dataset_id == dataset_id
        assert isinstance(result.training_report, TrainingReport)
        assert result.training_report.id == "tr1"

        self.service.request_gql.assert_called_once_with(
            Queries.GET,
            Queries.GET["variables"](dataset_id=dataset_id, model_id=model_id),
        )

    def test_get_model_by_name_success(self):
        dataset_id = "d1"
        name = "model-name"

        self.service.request_gql.return_value = {
            "id": "m1",
            "datasetId": dataset_id,
            "name": name,
            "trainingReport": None,
        }

        result = self.service.get_model_by_name(dataset_id=dataset_id, name=name)

        assert isinstance(result, Model)
        assert result.dataset_id == dataset_id
        assert result.name == name

        self.service.request_gql.assert_called_once_with(
            Queries.GET,
            Queries.GET["variables"](dataset_id=dataset_id, name=name),
        )

    def test_get_models_success(self):
        dataset_id = "d1"

        self.service.request_gql.return_value = {
            "models": [
                {
                    "id": "m1",
                    "datasetId": dataset_id,
                    "name": "model-1",
                    "trainingReport": None,
                },
                {
                    "id": "m2",
                    "datasetId": dataset_id,
                    "name": "model-2",
                    "trainingReport": {
                        "id": "tr2",
                        "name": "report-2",
                        "modelId": "m2",
                        "contentId": "c2",
                    },
                },
            ],
            "next": "cursor-1",
            "totalCount": 2,
        }

        models, cursor, total_count = self.service.get_models(dataset_id=dataset_id, length=10)

        assert len(models) == 2
        assert cursor == "cursor-1"
        assert total_count == 2
        assert models[0].id == "m1"
        assert models[0].training_report is None
        assert models[1].id == "m2"
        assert models[1].training_report is not None
        assert models[1].training_report.id == "tr2"

        self.service.request_gql.assert_called_once_with(
            Queries.GET_LIST,
            Queries.GET_LIST["variables"](
                dataset_id=dataset_id,
                filter=None,
                order_by=None,
                cursor=None,
                length=10,
            ),
        )

    def test_get_models_invalid_length(self):
        with pytest.raises(BadParameterError, match="length must be between 1 and 50"):
            self.service.get_models(dataset_id="d1", length=0)

    def test_create_model_success(self):
        dataset_id = "d1"
        name = "new-model"
        task_type = ModelTaskType.OCR

        self.service.request_gql.return_value = {
            "id": "m1",
            "datasetId": dataset_id,
            "name": name,
            "taskType": task_type.value,
            "status": ModelStatus.PENDING.value,
            "trainingReport": None,
        }

        result = self.service.create_model(
            dataset_id=dataset_id,
            name=name,
            task_type=task_type,
            description=None,
        )

        assert isinstance(result, Model)
        assert result.dataset_id == dataset_id
        assert result.name == name
        assert result.task_type == task_type

        self.service.request_gql.assert_called_once_with(
            Queries.CREATE,
            Queries.CREATE["variables"](
                dataset_id=dataset_id,
                name=name,
                task_type=task_type,
                description=None,
                custom_dag_id=None,
                total_data_count=None,
                train_data_count=None,
                validation_data_count=None,
                training_parameters=None,
                train_slice_id=None,
                validation_slice_id=None,
                is_pinned=None,
                score_key=None,
                score_value=None,
                score_unit=None,
            ),
        )

    def test_update_model_success(self):
        dataset_id = "d1"
        model_id = "m1"

        self.service.request_gql.return_value = {
            "id": model_id,
            "datasetId": dataset_id,
            "name": "updated",
            "status": ModelStatus.COMPLETED.value,
            "trainingReport": None,
        }

        result = self.service.update_model(
            dataset_id=dataset_id,
            model_id=model_id,
            description="desc",
            status=ModelStatus.COMPLETED,
            name=Undefined,
        )

        assert isinstance(result, Model)
        assert result.id == model_id
        assert result.status == ModelStatus.COMPLETED

        self.service.request_gql.assert_called_once_with(
            Queries.UPDATE,
            Queries.UPDATE["variables"](
                dataset_id=dataset_id,
                model_id=model_id,
                name=Undefined,
                description="desc",
                status=ModelStatus.COMPLETED,
            ),
        )

    def test_delete_model_success(self):
        dataset_id = "d1"
        model_id = "m1"

        self.service.request_gql.return_value = True

        result = self.service.delete_model(dataset_id=dataset_id, model_id=model_id)

        assert result is True

        self.service.request_gql.assert_called_once_with(
            Queries.DELETE,
            Queries.DELETE["variables"](dataset_id=dataset_id, model_id=model_id),
        )


@pytest.mark.skipif(os.environ.get("CI") == "true", reason="Skip local real tests on CI")
def test_model_service_real_smoke():
    _precheck_real_test(
        required_env=["TEST_DATASET_ID"],
        optional_env=[
            "SUNRISE_SERVER_URL",
            "SUPERB_SYSTEM_SDK_HOST",
            "SUPERB_SYSTEM_SDK_USER_EMAIL",
            "SDK_DEBUG_GQL",
            "SDK_DEBUG_GQL_MAX_CHARS",
        ],
    )

    dataset_id = os.environ.get("TEST_DATASET_ID")
    if not dataset_id:
        pytest.skip("TEST_DATASET_ID not set")

    service = ModelService()

    _print_step(
        "ModelService real_smoke - config",
        {
            "endpoint": getattr(service, "endpoint", None),
            "dataset_id": dataset_id,
        },
    )

    _print_step("ModelService.get_models", {"dataset_id": dataset_id, "length": 1})
    models, cursor, total_count = service.get_models(dataset_id=dataset_id, length=1)

    _print_step(
        "ModelService.get_models - result",
        {
            "models_count": len(models),
            "cursor": cursor,
            "total_count": total_count,
            "first_model_id": models[0].id if models else None,
            "first_model_name": models[0].name if models else None,
        },
    )

    assert isinstance(models, list)
    assert total_count is None or isinstance(total_count, int)
    # models can be empty depending on dataset

    if models:
        _print_step("ModelService.get_model", {"dataset_id": dataset_id, "model_id": models[0].id})
        model = service.get_model(dataset_id=dataset_id, model_id=models[0].id)
        assert model is not None
        _print_step(
            "ModelService.get_model - result",
            {
                "id": model.id,
                "name": model.name,
                "status": getattr(model.status, "value", model.status),
                "task_type": getattr(model.task_type, "value", model.task_type),
                "training_report_id": getattr(getattr(model, "training_report", None), "id", None),
            },
        )
        if model.name:
            _print_step("ModelService.get_model_by_name", {"dataset_id": dataset_id, "name": model.name})
            model_by_name = service.get_model_by_name(dataset_id=dataset_id, name=model.name)
            assert model_by_name is not None
            _print_step(
                "ModelService.get_model_by_name - result",
                {
                    "id": model_by_name.id,
                    "name": model_by_name.name,
                },
            )


@pytest.mark.skipif(os.environ.get("CI") == "true", reason="Skip local real tests on CI")
def test_model_service_real_mutations():
    _precheck_real_test(
        required_env=["TEST_DATASET_ID", "RUN_MODEL_MUTATION_TESTS"],
        optional_env=[
            "SUNRISE_SERVER_URL",
            "SUPERB_SYSTEM_SDK_HOST",
            "SUPERB_SYSTEM_SDK_USER_EMAIL",
            "SDK_DEBUG_GQL",
            "SDK_DEBUG_GQL_MAX_CHARS",
        ],
    )

    dataset_id = os.environ.get("TEST_DATASET_ID")
    if not dataset_id:
        pytest.skip("TEST_DATASET_ID not set")

    if os.environ.get("RUN_MODEL_MUTATION_TESTS") != "1":
        pytest.skip("RUN_MODEL_MUTATION_TESTS!=1 (avoid accidental mutations)")

    service = ModelService()

    _print_step(
        "ModelService real_mutations - config",
        {
            "endpoint": getattr(service, "endpoint", None),
            "dataset_id": dataset_id,
            "note": "This test will create/update/delete a model.",
        },
    )

    model_name = f"sdk-smoke-model-{uuid.uuid4().hex[:8]}"

    _print_step(
        "ModelService.create_model",
        {
            "dataset_id": dataset_id,
            "name": model_name,
            "task_type": ModelTaskType.OCR.value,
            "description": "sdk smoke",
        },
    )

    created = service.create_model(
        dataset_id=dataset_id,
        name=model_name,
        task_type=ModelTaskType.OCR,
        description="sdk smoke",
    )

    _print_step(
        "ModelService.create_model - result",
        {
            "id": created.id,
            "name": created.name,
            "status": getattr(created.status, "value", created.status),
            "task_type": getattr(created.task_type, "value", created.task_type),
        },
    )

    assert created is not None
    assert created.id is not None
    assert created.name == model_name

    _print_step(
        "ModelService.update_model",
        {
            "dataset_id": dataset_id,
            "model_id": created.id,
            "description": "sdk smoke updated",
        },
    )
    updated = service.update_model(
        dataset_id=dataset_id,
        model_id=created.id,
        description="sdk smoke updated",
    )

    _print_step(
        "ModelService.update_model - result",
        {
            "id": updated.id,
            "description": updated.description,
        },
    )

    assert updated is not None
    assert updated.id == created.id
    assert updated.description == "sdk smoke updated"

    _print_step(
        "ModelService.delete_model",
        {
            "dataset_id": dataset_id,
            "model_id": created.id,
        },
    )
    deleted = service.delete_model(
        dataset_id=dataset_id,
        model_id=created.id,
    )

    _print_step("ModelService.delete_model - result", {"deleted": deleted})

    assert deleted is True

    try:
        _print_step("ModelService.get_model (verify deletion)", {"dataset_id": dataset_id, "model_id": created.id})
        after = service.get_model(dataset_id=dataset_id, model_id=created.id)
        _print_step("ModelService.get_model (verify deletion) - result", {"model": after})
        assert after is None
    except NotFoundError:
        _print_step("ModelService.get_model (verify deletion)", "NotFoundError -> deleted")
        assert True
