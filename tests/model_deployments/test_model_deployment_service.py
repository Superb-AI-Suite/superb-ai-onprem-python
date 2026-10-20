"""ModelDeploymentService and ModelDeployDefinitionService against a fake platform (FDE-133)."""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from spb_onprem import (
    ActivityHistory,
    ModelDeployDefinitionInput,
    ModelDeployDefinitionService,
    ModelDeployment,
    ModelDeploymentFilter,
    ModelDeploymentFilterOptions,
    ModelDeploymentService,
    ModelDeploymentStatus,
)
from spb_onprem.activities.entities import ActivityStatus
from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import (
    BadDeletionTargetError,
    BadParameterError,
    ConflictError,
    ForbiddenError,
    InvalidInputError,
    NotFoundError,
)
from spb_onprem.model_deployments import ModelDeploymentOrderBy, ModelDeploymentOrderField
from spb_onprem.model_deployments.queries import Queries
from spb_onprem.models.enums import OrderDirection
from spb_onprem.models.params import ModelFilterOptions

from .fake_platform import FakePlatform

DATASET = "dataset-1"


@pytest.fixture
def platform():
    platform = FakePlatform(DATASET)
    with patch.object(BaseService, "requests_retry_session", return_value=platform):
        yield platform


@pytest.fixture
def deployments(platform):
    return ModelDeploymentService()


@pytest.fixture
def templates(platform):
    return ModelDeployDefinitionService()


def _variables(platform, index=-1):
    return platform.requests[index]["payload"]["variables"]


def _template(templates, template_id="my-server", dataset_only=True):
    return templates.create_model_deploy_definition(
        DATASET,
        ModelDeployDefinitionInput(
            id=template_id, name="My server", server_image_name="team/my-server",
            server_image_tag="v1", dataset_only=dataset_only,
        ),
    )


class TestTemplates:
    def test_create_sends_the_input_and_reads_the_template(self, platform, templates):
        created = _template(templates)

        assert _variables(platform) == {
            "datasetId": DATASET,
            "input": {"id": "my-server", "name": "My server", "serverImageName": "team/my-server",
                      "serverImageTag": "v1", "description": None, "startScript": None, "datasetOnly": True},
        }
        assert created.id == "my-server"
        assert created.dataset_id == DATASET
        assert created.is_system is False

    def test_create_takes_a_dict_with_field_or_graphql_names(self, platform, templates):
        templates.create_model_deploy_definition(
            DATASET, {"id": "shared-server", "name": "Shared", "serverImageName": "team/s", "dataset_only": False}
        )
        assert _variables(platform)["input"]["datasetOnly"] is False
        assert platform.definitions["shared-server"]["datasetId"] is None

    def test_create_refuses_an_incomplete_dict_before_sending(self, platform, templates):
        with pytest.raises(BadParameterError, match="definition is invalid"):
            templates.create_model_deploy_definition(DATASET, {"id": "x-server"})
        assert platform.requests == []

    def test_create_taken_id_is_a_conflict(self, templates):
        _template(templates)
        with pytest.raises(ConflictError):
            _template(templates)

    def test_invalid_id_is_invalid_input(self, templates):
        with pytest.raises(InvalidInputError):
            _template(templates, template_id="Bad_ID")

    def test_only_owner_or_workspace_admin_creates(self, platform, templates):
        platform.admin = False
        with pytest.raises(ForbiddenError):
            _template(templates)

    def test_list_and_get(self, templates):
        _template(templates)

        listed = templates.get_model_deploy_definitions(DATASET)

        assert {item.id for item in listed} == {"cosmos3-reasoner", "my-server"}
        assert templates.get_model_deploy_definition(DATASET, "cosmos3-reasoner").is_system is True
        assert templates.get_model_deploy_definition(DATASET, "missing") is None

    def test_not_a_vlm_dataset(self, platform, templates):
        platform.dataset_type = "IMAGE"
        with pytest.raises(InvalidInputError, match="vision-language"):
            templates.get_model_deploy_definitions(DATASET)

    def test_delete_detaches_deployments_and_unlinks_models(self, platform, templates, deployments):
        _template(templates)
        deployment = deployments.create_model_deployment(
            DATASET, "my-server", "d1", model_id="model-1", bind_model_to_definition=True
        )
        assert platform.models["model-1"]["definitionId"] == "my-server"

        usage = templates.get_model_deploy_definition_usage(DATASET, "my-server")
        result = templates.delete_model_deploy_definition(DATASET, "my-server")

        assert (usage.deployment_count, usage.model_count) == (1, 1)
        assert (result.id, result.detached_deployment_count, result.unlinked_model_count) == ("my-server", 1, 1)
        detached = deployments.get_model_deployment(DATASET, deployment.id)
        assert detached.definition_id is None
        assert detached.status == ModelDeploymentStatus.PENDING  # kept, not deleted

    def test_system_template_cannot_be_deleted(self, templates):
        with pytest.raises(InvalidInputError, match="System templates"):
            templates.delete_model_deploy_definition(DATASET, "cosmos3-reasoner")

    def test_delete_missing_template(self, templates):
        with pytest.raises(NotFoundError):
            templates.delete_model_deploy_definition(DATASET, "missing")

    def test_pin(self, platform, templates):
        pinned = templates.set_model_deploy_definition_pinned(DATASET, "cosmos3-reasoner", True)
        assert pinned.is_pinned is True
        assert _variables(platform) == {"datasetId": DATASET, "definitionId": "cosmos3-reasoner", "isPinned": True}

    def test_unbind_model(self, platform, templates):
        platform.models["model-1"]["definitionId"] = "cosmos3-reasoner"

        model = templates.unbind_model_deploy_definition(DATASET, "model-1")

        assert model.id == "model-1"
        assert model.definition_id is None
        assert "definitionId" in platform.requests[-1]["payload"]["query"]

    def test_model_filter_options_for_template_links(self):
        options = ModelFilterOptions(definition_id_is_null=True, definition_id_in=["cosmos3-reasoner"])
        assert options.model_dump(by_alias=True, exclude_unset=True) == {
            "definitionIdIsNull": True, "definitionIdIn": ["cosmos3-reasoner"],
        }


class TestLifecycle:
    def test_create_sends_every_argument(self, platform, deployments):
        expires = datetime(2030, 1, 2, 3, 4, 5, tzinfo=timezone.utc)

        created = deployments.create_model_deployment(
            DATASET, "cosmos3-reasoner", "reasoner r4", model_id="model-1", description="first",
            expires_at=expires, gpu_types=["NVIDIA-A100-SXM4-80GB"], gpu_count=2, invoke_timeout_seconds=900,
        )

        assert _variables(platform) == {
            "datasetId": DATASET, "definitionId": "cosmos3-reasoner", "modelId": "model-1", "name": "reasoner r4",
            "description": "first", "expiresAt": "2030-01-02T03:04:05Z", "gpuTypes": ["NVIDIA-A100-SXM4-80GB"],
            "gpuCount": 2, "invokeTimeoutSeconds": 900, "bindModelToDefinition": False,
        }
        assert isinstance(created, ModelDeployment)
        assert created.status == ModelDeploymentStatus.PENDING
        assert created.runtime.generation == 1
        assert created.runtime.deploy_activity_history_id
        assert created.is_base_model is False
        assert platform.models["model-1"]["definitionId"] is None  # deployed once, not linked

    def test_base_model_deployment_and_relative_expiry(self, platform, deployments):
        before = datetime.now(timezone.utc)

        created = deployments.create_model_deployment(
            DATASET, "cosmos3-reasoner", "base", expires_at=timedelta(hours=2)
        )

        sent = _variables(platform)
        assert sent["modelId"] is None
        assert created.is_base_model is True
        expires = datetime.fromisoformat(sent["expiresAt"].replace("Z", "+00:00"))
        assert timedelta(hours=2) <= expires - before < timedelta(hours=2, minutes=1)

    @pytest.mark.parametrize("bad", [
        timedelta(0), timedelta(seconds=-1), 5, "",
        "2026-12-31T09:00:00",          # no offset: refused
        "next tuesday",
    ])
    def test_bad_expiry_is_refused_before_sending(self, platform, deployments, bad):
        with pytest.raises(BadParameterError):
            deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "x", expires_at=bad)
        assert platform.requests == []

    @pytest.mark.parametrize("value", ["2026-12-31T09:00:00Z", "2026-12-31T18:00:00+09:00", "2026-12-31T09:00:00.000Z"])
    def test_expiry_string_with_offset_is_sent_as_is(self, platform, deployments, value):
        deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "x", expires_at=value)
        assert _variables(platform)["expiresAt"] == value

    def test_naive_datetime_is_local_time(self, platform, deployments):
        local = datetime(2026, 12, 31, 9, 0, 0)
        deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "x", expires_at=local)
        sent = datetime.fromisoformat(_variables(platform)["expiresAt"].replace("Z", "+00:00"))
        assert sent == local.astimezone(timezone.utc)

    def test_model_of_another_template_is_refused(self, platform, deployments):
        platform.models["model-1"]["definitionId"] = "other-template"
        with pytest.raises(InvalidInputError, match="not registered"):
            deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "x", model_id="model-1")

    def test_missing_template_is_not_found(self, deployments):
        with pytest.raises(NotFoundError):
            deployments.create_model_deployment(DATASET, "missing", "x")

    def test_stop_then_start_a_new_generation(self, platform, deployments):
        created = deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "d1")
        platform.runtime_reports(created.id, "READY")

        stopping = deployments.stop_model_deployment(DATASET, created.id)
        assert stopping.status == ModelDeploymentStatus.STOPPING
        assert stopping.runtime.cleanup_activity_history_id

        platform.runtime_reports(created.id, "STOPPED")
        started = deployments.start_model_deployment(DATASET, created.id, expires_at="2031-01-01T00:00:00Z")

        assert started.status == ModelDeploymentStatus.PENDING
        assert started.runtime.generation == 2
        assert _variables(platform)["expiresAt"] == "2031-01-01T00:00:00Z"
        runtimes = deployments.get_model_deployment_runtimes(DATASET, created.id)
        assert [runtime.generation for runtime in runtimes] == [2, 1]

    def test_stop_a_stopped_deployment_is_a_conflict(self, platform, deployments):
        created = deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "d1")
        platform.runtime_reports(created.id, "STOPPED")
        with pytest.raises(ConflictError):
            deployments.stop_model_deployment(DATASET, created.id)

    def test_start_a_running_deployment_is_a_conflict(self, platform, deployments):
        created = deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "d1")
        platform.runtime_reports(created.id, "READY")
        with pytest.raises(ConflictError):
            deployments.start_model_deployment(DATASET, created.id)

    def test_deployment_without_template_cannot_start(self, platform, deployments, templates):
        _template(templates)
        created = deployments.create_model_deployment(DATASET, "my-server", "d1")
        templates.delete_model_deploy_definition(DATASET, "my-server")
        platform.runtime_reports(created.id, "STOPPED")
        with pytest.raises(InvalidInputError, match="template"):
            deployments.start_model_deployment(DATASET, created.id)

    def test_update_sends_only_the_given_fields(self, platform, deployments):
        created = deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "d1", description="old")

        updated = deployments.update_model_deployment(DATASET, created.id, description=None,
                                                      invoke_timeout_seconds=1200)

        assert _variables(platform) == {"datasetId": DATASET, "deploymentId": created.id,
                                        "description": None, "invokeTimeoutSeconds": 1200}
        assert updated.description is None
        assert updated.invoke_timeout_seconds == 1200

    @pytest.mark.parametrize("kwargs", [{"name": ""}, {"name": None}, {"invoke_timeout_seconds": None}])
    def test_update_refuses_values_the_platform_cannot_clear(self, platform, deployments, kwargs):
        with pytest.raises(BadParameterError):
            deployments.update_model_deployment(DATASET, "d", **kwargs)
        assert platform.requests == []

    def test_pin(self, platform, deployments):
        created = deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "d1")
        assert deployments.set_model_deployment_pinned(DATASET, created.id, True).is_pinned is True
        with pytest.raises(BadParameterError):
            deployments.set_model_deployment_pinned(DATASET, created.id, "yes")

    def test_list_with_filter_and_order(self, platform, deployments):
        first = deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "alpha")
        deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "beta")
        platform.runtime_reports(first.id, "READY")

        items, cursor, total = deployments.get_model_deployments(
            DATASET,
            filter=ModelDeploymentFilter(must_filter=ModelDeploymentFilterOptions(
                status_in=[ModelDeploymentStatus.READY])),
            order_by=ModelDeploymentOrderBy(field=ModelDeploymentOrderField.NAME, direction=OrderDirection.ASC),
            length=50,
        )

        assert [item.id for item in items] == [first.id]
        assert (cursor, total) == (None, 1)
        assert items[0].runtime is None  # lists do not load runtime
        assert _variables(platform) == {
            "datasetId": DATASET, "filter": {"must": {"statusIn": ["READY"]}},
            "orderBy": {"field": "NAME", "direction": "ASC"}, "cursor": None, "length": 50,
        }
        assert "runtime" not in platform.requests[-1]["payload"]["query"]

    @pytest.mark.parametrize("length", [0, 101, True])
    def test_list_length(self, deployments, length):
        with pytest.raises(BadParameterError):
            deployments.get_model_deployments(DATASET, length=length)

    def test_get_missing_is_none(self, deployments):
        assert deployments.get_model_deployment(DATASET, "missing") is None

    def test_unknown_status_from_a_newer_platform_stays_a_string(self):
        record = ModelDeployment.model_validate({"id": "d", "status": "HIBERNATING", "runtime": {"endStatus": "X"}})
        assert record.status == "HIBERNATING"
        assert record.runtime.end_status == "X"
        assert ModelDeployment.model_validate({"status": "READY"}).status is ModelDeploymentStatus.READY

    @pytest.mark.parametrize("missing", ["dataset_id", "deployment_id"])
    def test_ids_are_required(self, platform, deployments, missing):
        kwargs = {"dataset_id": DATASET, "deployment_id": "d"}
        kwargs[missing] = ""
        with pytest.raises(BadParameterError):
            deployments.stop_model_deployment(**kwargs)
        assert platform.requests == []


class TestDelete:
    def test_ids_start_one_activity_that_picks_targets_when_it_runs(self, platform, deployments):
        running = deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "running")
        stopped = deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "stopped")
        platform.runtime_reports(running.id, "READY")
        platform.runtime_reports(stopped.id, "STOPPED")

        history = deployments.delete_model_deployments(DATASET, deployment_ids=[running.id, stopped.id])

        assert isinstance(history, ActivityHistory)
        assert history.status == ActivityStatus.PENDING
        assert _variables(platform) == {
            "datasetId": DATASET,
            "jobType": "DELETE_MODEL_DEPLOYMENT",
            "parameters": {"dataset_id": DATASET,
                           "deployment_filter": {"must": {"idIn": [running.id, stopped.id]}}},
        }
        assert len(platform.jobs) == 1
        # C20: the request changes nothing.
        assert deployments.get_model_deployment(DATASET, running.id).status == ModelDeploymentStatus.READY
        assert deployments.get_model_deployment(DATASET, stopped.id).status == ModelDeploymentStatus.STOPPED

        platform.run_deletion_activity(history.id)

        # A stopped deployment goes at once; a running one waits for its server to be removed.
        assert deployments.get_model_deployment(DATASET, stopped.id) is None
        assert deployments.get_model_deployment(DATASET, running.id).status == ModelDeploymentStatus.DELETING

    def test_missing_targets_are_not_refused(self, platform, deployments):
        history = deployments.delete_model_deployments(DATASET, deployment_ids=["01JGONE0000000000000000000"])

        assert history.status == ActivityStatus.PENDING
        assert platform.run_deletion_activity(history.id)["status"] == "SUCCESS"

    def test_filter_model(self, platform, deployments):
        deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "old-1")
        deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "new-1")

        history = deployments.delete_model_deployments(
            DATASET,
            deployment_filter=ModelDeploymentFilter(must_filter=ModelDeploymentFilterOptions(name_contains="old")),
        )
        platform.run_deletion_activity(history.id)

        assert _variables(platform)["parameters"]["deployment_filter"] == {"must": {"nameContains": "old"}}
        assert [d["name"] for d in platform.deployments.values() if d["status"] == "DELETING"] == ["old-1"]

    def test_dict_filter_is_sent_as_it_is(self, platform, deployments):
        deployments.delete_model_deployments(DATASET, deployment_filter={"must": {"statusIn": ["FAILED"]},
                                                                         "not": {"idIn": ["x"]}})
        assert _variables(platform)["parameters"]["deployment_filter"] == {
            "must": {"statusIn": ["FAILED"]}, "not": {"idIn": ["x"]}}

    @pytest.mark.parametrize("kwargs", [
        {},
        {"deployment_ids": []},
        {"deployment_ids": "01JDEPLOY"},
        {"deployment_ids": ["a"], "deployment_filter": {"must": {"idIn": ["a"]}}},
        {"deployment_filter": {}},
        {"deployment_filter": {"must": {}}},
        {"deployment_filter": {"must": {"idIn": []}}},
        {"deployment_filter": {"must": {"nameContains": "  "}}},
        {"deployment_filter": ModelDeploymentFilter()},
        # Checked by the platform only when the activity runs (C20), so the SDK refuses them first.
        {"deployment_filter": {"must": {"id_in": ["a"]}}},
        {"deployment_filter": {"must_filter": {"idIn": ["a"]}}},
        {"deployment_filter": {"not": {"nameIn": ["a"]}}},
    ])
    def test_refused_targets(self, platform, deployments, kwargs):
        with pytest.raises(BadDeletionTargetError):
            deployments.delete_model_deployments(DATASET, **kwargs)
        assert platform.requests == []

    def test_a_member_submits_it_for_approval(self, platform, deployments):
        created = deployments.create_model_deployment(DATASET, "cosmos3-reasoner", "d1")
        platform.admin = False

        history = deployments.delete_model_deployments(DATASET, deployment_ids=[created.id])

        assert history.status == ActivityStatus.AWAITING_APPROVAL
        assert platform.deployments[created.id]["status"] == "PENDING"  # nothing changes before approval


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class TestWait:
    def _wait(self, deployments, statuses, **kwargs):
        clock = FakeClock()
        reads = iter(statuses)

        def read(dataset_id, deployment_id):
            status = next(reads)
            return None if status is None else ModelDeployment(id=deployment_id, status=status)

        with patch.object(deployments, "get_model_deployment", side_effect=read), \
                patch("spb_onprem.model_deployments.service.time", clock):
            return deployments.wait_for_model_deployment(DATASET, "d1", **kwargs), clock

    def test_until_ready(self, platform, deployments):
        result, clock = self._wait(deployments, ["PENDING", "STARTING", "READY"], poll_interval=5)
        assert result.status == ModelDeploymentStatus.READY
        assert clock.now == 10

    def test_returns_on_failure_without_raising(self, platform, deployments):
        result, _ = self._wait(deployments, ["PENDING", "FAILED"])
        assert result.status == ModelDeploymentStatus.FAILED

    def test_returns_none_when_deleted(self, platform, deployments):
        result, _ = self._wait(deployments, ["DELETING", None], until=[ModelDeploymentStatus.STOPPED])
        assert result is None

    def test_timeout(self, platform, deployments):
        with pytest.raises(TimeoutError, match="last status: STARTING"):
            self._wait(deployments, ["STARTING"] * 10, timeout=20, poll_interval=10)

    @pytest.mark.parametrize("until", ["READY", ModelDeploymentStatus.READY, ["READY"]])
    def test_until_takes_one_status_or_a_name(self, platform, deployments, until):
        result, _ = self._wait(deployments, ["STARTING", "READY"], until=until, poll_interval=1)
        assert result.status == ModelDeploymentStatus.READY

    def test_unknown_until_is_refused(self, deployments):
        with pytest.raises(BadParameterError, match="until must be"):
            deployments.wait_for_model_deployment(DATASET, "d1", until="RUNNING")

    @pytest.mark.parametrize("kwargs", [{"timeout": 0}, {"poll_interval": 0}])
    def test_bad_arguments(self, deployments, kwargs):
        with pytest.raises(ValueError):
            deployments.wait_for_model_deployment(DATASET, "d1", **kwargs)


def test_every_query_is_used_by_a_service_function():
    """No GraphQL document without a public function (and the other way round, by the tests above)."""
    import inspect

    from spb_onprem.model_deployments import service

    source = inspect.getsource(service)
    unused = [name for name, value in vars(Queries).items()
              if isinstance(value, dict) and f"Queries.{name}" not in source]
    assert unused == []
