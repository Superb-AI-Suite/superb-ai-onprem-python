import os
import uuid

import pytest
from unittest.mock import Mock

from spb_onprem.base_types import Undefined
from spb_onprem.contents.service import ContentService
from spb_onprem.models.enums import ModelTaskType
from spb_onprem.models.service import ModelService
from spb_onprem.trainingreports.service import TrainingReportService
from spb_onprem.trainingreports.queries import Queries
from spb_onprem.models.entities import Model
from spb_onprem.exceptions import BadParameterError


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


class TestTrainingReportService:
    def setup_method(self):
        self.service = TrainingReportService()
        self.service.request_gql = Mock()

    def test_create_training_report_missing_dataset_id(self):
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.service.create_training_report(
                dataset_id=None,
                model_id="m1",
                name="report",
                content_id="c1",
            )

    def test_create_training_report_missing_model_id(self):
        with pytest.raises(BadParameterError, match="model_id is required"):
            self.service.create_training_report(
                dataset_id="d1",
                model_id=None,
                name="report",
                content_id="c1",
            )

    def test_create_training_report_missing_name(self):
        with pytest.raises(BadParameterError, match="name is required"):
            self.service.create_training_report(
                dataset_id="d1",
                model_id="m1",
                name=None,
                content_id="c1",
            )

    def test_create_training_report_missing_content_id(self):
        with pytest.raises(BadParameterError, match="content_id is required"):
            self.service.create_training_report(
                dataset_id="d1",
                model_id="m1",
                name="report",
                content_id=None,
            )

    def test_delete_training_report_missing_dataset_id(self):
        with pytest.raises(BadParameterError, match="dataset_id is required"):
            self.service.delete_training_report(dataset_id=None, model_id="m1", training_report_id="tr1")

    def test_delete_training_report_missing_model_id(self):
        with pytest.raises(BadParameterError, match="model_id is required"):
            self.service.delete_training_report(dataset_id="d1", model_id=None, training_report_id="tr1")

    def test_delete_training_report_missing_training_report_id(self):
        with pytest.raises(BadParameterError, match="training_report_id is required"):
            self.service.delete_training_report(dataset_id="d1", model_id="m1", training_report_id=None)

    def test_create_training_report_success(self):
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

        result = self.service.create_training_report(
            dataset_id=dataset_id,
            model_id=model_id,
            name="report",
            content_id="c1",
            description=None,
        )

        assert isinstance(result, Model)
        assert result.id == model_id
        assert result.training_report is not None
        assert result.training_report.id == "tr1"

        self.service.request_gql.assert_called_once_with(
            Queries.CREATE,
            Queries.CREATE["variables"](
                dataset_id=dataset_id,
                model_id=model_id,
                name="report",
                content_id="c1",
                description=None,
            ),
        )

    def test_update_training_report_success(self):
        dataset_id = "d1"
        model_id = "m1"
        training_report_id = "tr1"

        self.service.request_gql.return_value = {
            "id": model_id,
            "datasetId": dataset_id,
            "name": "model-name",
            "trainingReport": {
                "id": training_report_id,
                "name": "report",
                "modelId": model_id,
                "contentId": "c1",
                "description": "updated",
            },
        }

        result = self.service.update_training_report(
            dataset_id=dataset_id,
            model_id=model_id,
            training_report_id=training_report_id,
            description="updated",
            name=Undefined,
            content_id=Undefined,
        )

        assert isinstance(result, Model)
        assert result.id == model_id
        assert result.training_report is not None
        assert result.training_report.id == training_report_id
        assert result.training_report.description == "updated"

        self.service.request_gql.assert_called_once_with(
            Queries.UPDATE,
            Queries.UPDATE["variables"](
                dataset_id=dataset_id,
                model_id=model_id,
                training_report_id=training_report_id,
                name=Undefined,
                content_id=Undefined,
                description="updated",
            ),
        )

    def test_delete_training_report_success(self):
        dataset_id = "d1"
        model_id = "m1"
        training_report_id = "tr1"

        self.service.request_gql.return_value = {
            "id": model_id,
            "datasetId": dataset_id,
            "name": "model-name",
            "trainingReport": None,
        }

        result = self.service.delete_training_report(
            dataset_id=dataset_id,
            model_id=model_id,
            training_report_id=training_report_id,
        )

        assert isinstance(result, Model)
        assert result.id == model_id

        self.service.request_gql.assert_called_once_with(
            Queries.DELETE,
            Queries.DELETE["variables"](
                dataset_id=dataset_id,
                model_id=model_id,
                training_report_id=training_report_id,
            ),
        )


@pytest.mark.skipif(os.environ.get("CI") == "true", reason="Skip local real tests on CI")
def test_training_report_service_real_smoke():
    _precheck_real_test(
        required_env=["TEST_DATASET_ID"],
        optional_env=[
            "TEST_MODEL_ID",
            "TEST_CONTENT_ID",
            "RUN_TRAINING_REPORT_MUTATION_TESTS",
            "RUN_MUTATION_TESTS",
            "SUNRISE_SERVER_URL",
            "SUPERB_SYSTEM_SDK_HOST",
            "SUPERB_SYSTEM_SDK_USER_EMAIL",
            "SDK_DEBUG_GQL",
            "SDK_DEBUG_GQL_MAX_CHARS",
        ],
    )

    dataset_id = os.environ.get("TEST_DATASET_ID")
    model_id = os.environ.get("TEST_MODEL_ID")
    content_id = os.environ.get("TEST_CONTENT_ID")

    if not dataset_id:
        pytest.skip("TEST_DATASET_ID not set")

    run_mutation_tests = os.environ.get("RUN_TRAINING_REPORT_MUTATION_TESTS") or os.environ.get("RUN_MUTATION_TESTS")
    if run_mutation_tests != "1":
        pytest.skip("RUN_TRAINING_REPORT_MUTATION_TESTS!=1 (or RUN_MUTATION_TESTS!=1) (avoid accidental mutations)")

    service = TrainingReportService()

    created_model_here = False
    created_content_here = False

    if not model_id:
        model_service = ModelService()
        _print_step(
            "Resolve TEST_MODEL_ID - try existing models",
            {"dataset_id": dataset_id, "length": 1},
        )
        models, _, _ = model_service.get_models(dataset_id=dataset_id, length=1)
        if models:
            model_id = models[0].id
            _print_step("Resolve TEST_MODEL_ID - found", {"model_id": model_id, "name": models[0].name})
        else:
            name = f"sdk-smoke-tr-model-{uuid.uuid4().hex[:8]}"
            _print_step(
                "Resolve TEST_MODEL_ID - create_model",
                {"dataset_id": dataset_id, "name": name, "task_type": ModelTaskType.OCR.value},
            )
            created_model = model_service.create_model(
                dataset_id=dataset_id,
                name=name,
                task_type=ModelTaskType.OCR,
                description="sdk smoke training report model",
            )
            model_id = created_model.id
            created_model_here = True
            _print_step("Resolve TEST_MODEL_ID - created", {"model_id": model_id, "name": created_model.name})

    if not model_id:
        pytest.skip("Failed to resolve model_id")

    if not content_id:
        content_service = ContentService()
        key = f"sdk-smoke-training-report-{uuid.uuid4().hex}.json"
        _print_step(
            "Resolve TEST_CONTENT_ID - create_content",
            {"key": key, "content_type": "application/json"},
        )
        content, _upload_url = content_service.create_content(key=key, content_type="application/json")
        content_id = content.id
        created_content_here = True
        _print_step("Resolve TEST_CONTENT_ID - created", {"content_id": content_id, "key": content.key})

    if not content_id:
        pytest.skip("Failed to resolve content_id")

    _print_step(
        "TrainingReportService real_smoke - config",
        {
            "endpoint": getattr(service, "endpoint", None),
            "dataset_id": dataset_id,
            "model_id": model_id,
            "content_id": content_id,
            "note": "This test will create/update/delete a training report.",
        },
    )

    created = None
    created_training_report_id = None
    model_service_for_cleanup = ModelService()
    content_service_for_cleanup = ContentService()

    try:
        _print_step(
            "TrainingReportService.create_training_report",
            {
                "dataset_id": dataset_id,
                "model_id": model_id,
                "name": "sdk-smoke-training-report",
                "content_id": content_id,
                "description": "sdk smoke",
            },
        )
        created = service.create_training_report(
            dataset_id=dataset_id,
            model_id=model_id,
            name="sdk-smoke-training-report",
            content_id=content_id,
            description="sdk smoke",
        )

        created_training_report_id = getattr(getattr(created, "training_report", None), "id", None)

        _print_step(
            "TrainingReportService.create_training_report - result",
            {
                "model_id": created.id,
                "training_report_id": created_training_report_id,
                "training_report_name": getattr(getattr(created, "training_report", None), "name", None),
                "training_report_content_id": getattr(getattr(created, "training_report", None), "content_id", None),
            },
        )

        assert created.id == model_id
        assert created.training_report is not None
        assert created_training_report_id is not None

        _print_step(
            "TrainingReportService.update_training_report",
            {
                "dataset_id": dataset_id,
                "model_id": model_id,
                "training_report_id": created_training_report_id,
                "description": "sdk smoke updated",
            },
        )
        updated = service.update_training_report(
            dataset_id=dataset_id,
            model_id=model_id,
            training_report_id=created_training_report_id,
            description="sdk smoke updated",
        )

        _print_step(
            "TrainingReportService.update_training_report - result",
            {
                "training_report_id": getattr(getattr(updated, "training_report", None), "id", None),
                "training_report_description": getattr(getattr(updated, "training_report", None), "description", None),
            },
        )

        assert updated.training_report is not None

        _print_step(
            "TrainingReportService.delete_training_report",
            {
                "dataset_id": dataset_id,
                "model_id": model_id,
                "training_report_id": created_training_report_id,
            },
        )
        deleted = service.delete_training_report(
            dataset_id=dataset_id,
            model_id=model_id,
            training_report_id=created_training_report_id,
        )

        _print_step(
            "TrainingReportService.delete_training_report - result",
            {
                "model_id": deleted.id,
                "training_report": getattr(deleted, "training_report", None),
            },
        )

        assert deleted.id == model_id
    finally:
        if created_content_here and content_id:
            try:
                _print_step("Cleanup content", {"content_id": content_id})
                content_service_for_cleanup.delete_content(content_id=content_id)
            except Exception as e:
                _print_step("Cleanup content failed", str(e))

        if created_model_here and model_id:
            try:
                _print_step("Cleanup model", {"dataset_id": dataset_id, "model_id": model_id})
                model_service_for_cleanup.delete_model(dataset_id=dataset_id, model_id=model_id)
            except Exception as e:
                _print_step("Cleanup model failed", str(e))
