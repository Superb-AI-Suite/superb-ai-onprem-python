# Model Deployments and Templates

A **model deployment** runs a model server on GPUs and answers calls. It is made from a
**template** (`ModelDeployDefinition`, the server image to run) and a trained model of the
dataset, or the template's base model. Deployments belong to **VLM datasets**.

- `ModelDeploymentService`: create, list, wait, call (`invoke`), stop, start again, delete.
- `ModelDeployDefinitionService`: list, create, delete and pin templates; unlink a model from its template.

## Deploy, wait, call

```python
from datetime import timedelta

from spb_onprem import (
    DeploymentInvokeFile,
    DeploymentInvokeRequest,
    ModelDeploymentService,
    ModelDeploymentStatus,
)

service = ModelDeploymentService()

deployment = service.create_model_deployment(
    dataset_id="dataset_123",
    definition_id="cosmos3-reasoner",        # a template visible in the dataset
    name="reasoner r4",
    model_id="model_456",                    # None deploys the template's base model
    expires_at=timedelta(hours=8),           # or a datetime / ISO 8601 string; None never expires
    gpu_types=["NVIDIA-A100-SXM4-80GB"],     # None: any GPU
    gpu_count=1,
    invoke_timeout_seconds=600,              # wait for the server's response headers (10-3600)
)
print(deployment.status)                     # PENDING; a DEPLOY_MODEL activity launches the server

deployment = service.wait_for_model_deployment("dataset_123", deployment.id, timeout=1800)
if deployment is None or deployment.status != ModelDeploymentStatus.READY:
    raise RuntimeError(f"not ready: {deployment and deployment.status}")

result = service.invoke_model_deployment(
    "dataset_123",
    deployment.id,
    DeploymentInvokeRequest(
        text="Is the robot holding an object?",
        json={"max_new_tokens": 512},          # model options; one JSON document per part
        video=DeploymentInvokeFile.from_path("clip.mp4"),
    ),
)
print(result.texts)          # text parts
print(result.json_values)    # json parts, parsed (for example {"answer": ..., "model": "base"})
for video in result.videos:  # image / video / file parts keep their file name and type
    video.save("outputs/")   # a directory uses the part's file name
```

- Parts are named `text`, `json`, `image`, `video` and `file`, and each may repeat. Which parts
  a model reads is up to its server; see the template's documentation.
- Files: `DeploymentInvokeFile.from_path(path)` or `DeploymentInvokeFile.from_bytes(data, "input.png")`.
  The file name matters: servers read the type from the extension.
- The call goes through the platform (`POST {host}/graphql/model-deployments/{dataset}/{deployment}/invoke`)
  with your access key. The system SDK (no config file) cannot call it.
- It is never retried: a server handles one request at a time, and a retry can run the model twice.
  A request is at most 1 GiB; the request and the response are held in memory.
- Time: the platform waits up to the deployment's `invoke_timeout_seconds` for the response headers
  (`504 TIMEOUT`), and cuts a response that sends nothing for 60 seconds.

### Errors of `invoke_model_deployment`

All are `DeploymentInvokeError` (`status_code`, `code`, `message`, `retry_after`); those with a
general meaning are also the general SDK error:

| HTTP | `code` | Also |
| --- | --- | --- |
| 400, 413, 415, 422 | `INVALID_INPUT`, `PAYLOAD_TOO_LARGE`, `UNSUPPORTED_MEDIA_TYPE`, `UNPROCESSABLE` | `InvalidInputError` |
| 403 | `FORBIDDEN` (Collaborator, or not in the dataset) | `ForbiddenError` |
| 404 | `NOT_FOUND` | `NotFoundError` |
| 409 / 503 | `NOT_READY` (not READY) / `BUSY`, `NOT_READY` (server loading or busy, see `retry_after`) | `ConflictError` |
| 401, 500, 502, 503, 504 | `UNAUTHENTICATED`, `INTERNAL_ERROR`, `UPSTREAM_UNAVAILABLE`, `ENDPOINT_TOKEN_UNAVAILABLE`, `TIMEOUT` | — |

## Stop, start again, delete

```python
from spb_onprem import ActivityService, ModelDeploymentFilter, ModelDeploymentFilterOptions

stopping = service.stop_model_deployment("dataset_123", deployment.id)   # STOPPING, then STOPPED
service.wait_for_model_deployment("dataset_123", deployment.id, until=[ModelDeploymentStatus.STOPPED])

restarted = service.start_model_deployment("dataset_123", deployment.id)  # new generation, PENDING
print(restarted.runtime.generation)

# Delete: one DELETE_MODEL_DEPLOYMENT activity for all targets (ids or a filter, not both)
history = service.delete_model_deployments("dataset_123", deployment_ids=[deployment.id])
history = service.delete_model_deployments(
    "dataset_123",
    deployment_filter=ModelDeploymentFilter(
        must_filter=ModelDeploymentFilterOptions(status_in=[ModelDeploymentStatus.FAILED]),
    ),
)
ActivityService().wait_for_activity(history.id, dataset_id="dataset_123")
```

- Stop: PENDING, STARTING, READY or UNRESPONSIVE. Start: STOPPED, FAILED or EXPIRED. Otherwise
  `ConflictError`.
- Delete does not need a stop first. The request changes nothing: when the activity runs, it picks
  the deployments that match then. A deployment whose server is gone is deleted at once; the others
  become DELETING until the activity removes their server.
- Nothing matching (or already deleted) is a success. What the activity cannot handle (a filter the
  platform refuses, a server that cannot be removed) shows as a FAILED activity, not as an error of
  `delete_model_deployments`; check `wait_for_activity(...).status`.
- A filter without a condition, or a dict filter with keys other than `must`/`not` and `idIn`,
  `nameContains`, `statusIn`, `definitionIdIn`, is refused before sending (`BadDeletionTargetError`).
  A non-admin's delete is submitted as `AWAITING_APPROVAL`.
- Status and history: `get_model_deployment(...)` (with `runtime`, the current generation),
  `get_model_deployments(dataset_id, filter=..., order_by=..., cursor=..., length=...)` (pages of up
  to 100, without `runtime`), `get_model_deployment_runtimes(...)` (every generation: image,
  GPUs, activity IDs, end status, failure reason).
- `update_model_deployment(..., name=..., description=..., invoke_timeout_seconds=...)` and
  `set_model_deployment_pinned(...)`.

## Templates

```python
from spb_onprem import ModelDeployDefinitionInput, ModelDeployDefinitionService

templates = ModelDeployDefinitionService()

for template in templates.get_model_deploy_definitions("dataset_123"):  # system, shared and this dataset's
    print(template.id, template.is_system, template.dataset_id, template.server_image_name)

template = templates.create_model_deploy_definition(
    "dataset_123",
    ModelDeployDefinitionInput(
        id="my-vlm-server",                      # lowercase letters, numbers, hyphens; cannot change
        name="My VLM server",
        server_image_name="team/my-vlm-server",  # without a registry: the platform registry
        server_image_tag="1.0.0",                # None: latest
        dataset_only=True,                       # False shares it with all datasets
    ),
)

usage = templates.get_model_deploy_definition_usage("dataset_123", template.id)
deleted = templates.delete_model_deploy_definition("dataset_123", template.id)
print(deleted.detached_deployment_count, deleted.unlinked_model_count)

model = templates.unbind_model_deploy_definition("dataset_123", "model_456")  # model.definition_id is None
```

- Creating, deleting and pinning templates and reading their usage need Owner or WorkspaceAdmin.
  Templates cannot be edited; delete and create again.
- Deleting a template keeps its deployments (they lose the template: they can be invoked, stopped
  and deleted, but not started again) and unlinks its models. System templates cannot be deleted.
- A model gets linked to a template when it is deployed with `bind_model_to_definition=True`.
  `ModelFilterOptions(definition_id_in=[...])` and `definition_id_is_null=True` find models by link.
