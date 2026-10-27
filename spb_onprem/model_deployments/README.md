# Model Deployments and Deployment Definitions

A **model deployment** runs a model server on GPUs and answers calls. It is made from a
**deployment definition** (`ModelDeployDefinition`, the server image to run) and a trained model of the
dataset, or the definition's base model. Deployments belong to **VLM datasets**.

- `ModelDeploymentService`: create, list, wait, call (`invoke`), change the expiry, stop, start again, delete.
- `ModelDeployDefinitionService`: list, create, delete and pin definitions; unlink a model from its definition.

> **Changed (FDE-237):** `start_model_deployment` needs an explicit expiry: `expires_at=...` or
> `never_expires=True`. A call without one raises `BadParameterError`; it no longer keeps or renews
> the previous expiry. See [Expiry](#expiry). This SDK needs a platform with the same change.

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
    definition_id="cosmos3-reasoner",        # a definition visible in the dataset
    name="reasoner r4",
    model_id="model_456",                    # None deploys the definition's base model
    expires_at=timedelta(hours=8),           # or a datetime / ISO 8601 string; None never expires
    gpu_types=["NVIDIA-A100-SXM4-80GB"],     # None: any GPU
    gpu_count=1,
    invoke_timeout_seconds=600,              # wait for the server's response headers (10-3600)
    parameters={"model_type": "edge"},       # the definition's form (params); items left out get defaults
)
print(deployment.status)                     # PENDING; a DEPLOY_MODEL activity launches the server
print(deployment.parameters)                 # stored with the defaults filled in

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
  a model reads is up to its server; see the definition's documentation.
- Files: `DeploymentInvokeFile.from_path(path)` or `DeploymentInvokeFile.from_bytes(data, "input.png")`.
  The file name matters: servers read the type from the extension.
- The call goes through the platform (`POST {host}/graphql/model-deployments/{dataset}/{deployment}/invoke`)
  with your access key. The system SDK (no config file) cannot call it.
- It is never retried: a server handles one request at a time, and a retry can run the model twice.
  A request is at most 1 GiB as sent (bodies plus the multipart frame); the request and the
  response are held in memory: plan for about 2× the request size and 3–4× the response size.
- Time: the platform waits up to the deployment's `invoke_timeout_seconds` for the response headers
  (`504 TIMEOUT`), and cuts a response that sends nothing for 60 seconds.

### Form values (`parameters`)

A definition can have an input form, `ModelDeployDefinition.params` (see
[Deployment definitions](#deployment-definitions)). `create_model_deployment(parameters={...})` fills
it in by key:

- Items left out get their default (`value`); `parameters=None` uses every default. An item without
  a default whose schema does not allow null is required.
- The platform checks the values against the form when the deployment is created and refuses a key
  the definition does not have, a value its schema does not allow, a missing required item or more
  than 16 KB of values (`InvalidInputError`). The SDK only checks that it is a JSON object.
- The values are stored with the defaults filled in (`ModelDeployment.parameters`) and cannot change
  later; create a new deployment for other values. A start uses the stored values and fills in items
  added to the definition since; values that no longer fit the form are refused at the start.
- The server receives them as environment variables: `SUPERB_PARAM_<KEY in upper case>` for each
  value (a string as it is, other values in JSON, nothing for null) and `SUPERB_DEPLOYMENT_PARAMETERS` with all of
  them. What they mean is up to the server (for example `model_type` of the Cosmos 3 definitions:
  `edge` or `nano`, the size the model was trained with).
- **No secrets:** the values are stored as plain text and shown in the deployment details.
- Deployments made before form values existed have `parameters` None; the platform uses the defaults.

### Expiry

When a deployment expires, its server is removed and the status becomes EXPIRED.

| Call | Expiry |
| --- | --- |
| `create_model_deployment(..., expires_at=...)` | Optional: None (default) never expires. |
| `start_model_deployment(dataset_id, deployment_id, expires_at=...)` or `(..., never_expires=True)` | **Required**: exactly one of the two. |
| `set_model_deployment_expiry(dataset_id, deployment_id, expires_at=...)` or `(..., never_expires=True)` | Changes a PENDING, STARTING or READY deployment without a restart, from the server's next heartbeat. |

```python
from datetime import timedelta

service.set_model_deployment_expiry("dataset_123", deployment.id, expires_at=timedelta(hours=2))
service.set_model_deployment_expiry("dataset_123", deployment.id, never_expires=True)
```

- `expires_at` is a datetime, an ISO 8601 string with a UTC offset or `Z`, or a timedelta from now,
  and must be in the future. A naive datetime is read as this machine's local time.
- Neither or both of `expires_at` and `never_expires=True` raise `BadParameterError` before
  anything is sent. "Never expires" is a choice too, so it has to be said.
- `set_model_deployment_expiry` on another status raises `ConflictError`. It needs the same role as
  creating a deployment.

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

restarted = service.start_model_deployment(                               # new generation, PENDING
    "dataset_123", deployment.id, expires_at=timedelta(hours=8),          # or never_expires=True
)
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
- A start needs an expiry ([Expiry](#expiry)). The model, the GPUs and the form values stay as
  created.
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

## Deployment definitions

```python
from spb_onprem import ModelDeployDefinitionInput, ModelDeployDefinitionService

definitions = ModelDeployDefinitionService()

for definition in definitions.get_model_deploy_definitions("dataset_123"):  # system, shared and this dataset's
    print(definition.id, definition.is_system, definition.dataset_id, definition.server_image_name)

definition = definitions.create_model_deploy_definition(
    "dataset_123",
    ModelDeployDefinitionInput(
        id="my-vlm-server",                      # lowercase letters, numbers, hyphens; cannot change
        name="My VLM server",
        server_image_name="team/my-vlm-server",  # without a registry: the platform registry
        server_image_tag="1.0.0",                # None: latest
        dataset_only=True,                       # False shares it with all datasets
        params={                                 # the input form of its deployments; None: no form
            "model_type": {
                "schema": {"type": "string", "enum": ["edge", "nano"], "title": "Model type"},
                "value": "edge",                 # the default; without one the item is required
                "description": "Base model size.",
            },
            "max_frames": {"schema": {"type": ["integer", "null"], "minimum": 1, "maximum": 64}},
        },
    ),
)
print(definition.params)

usage = definitions.get_model_deploy_definition_usage("dataset_123", definition.id)
deleted = definitions.delete_model_deploy_definition("dataset_123", definition.id)
print(deleted.detached_deployment_count, deleted.unlinked_model_count)

model = definitions.unbind_model_deploy_definition("dataset_123", "model_456")  # model.definition_id is None
```

- Creating, deleting and pinning definitions and reading their usage need Owner or WorkspaceAdmin.
  Definitions cannot be edited; delete and create again.
- `params` has the shape of a training Param: `{key: {"schema": {...}, "value": default,
  "description": ...}}`. Keys match `^[a-z][a-z0-9_]{0,63}$` (at most 32 items). `schema.type` is
  `string` (with `enum`, `examples`, `format: date`, `title`, `values_display`), `number` or
  `integer` (`minimum`, `maximum`, `enum`), `array` (a list of string `enum` values, multiple
  choice) or `object` (JSON); `["<type>", "null"]` makes the item optional. Widget hints
  (`platform_config.ui_type_hint`, `platform_config.invisible`, `x-superb-widget`,
  `x-superb-gpu-supported`) are refused (`InvalidInputError`). The platform checks the form, not
  the SDK.
- Deleting a definition keeps its deployments (they lose the definition: they can be invoked, stopped
  and deleted, but not started again) and unlinks its models. System definitions cannot be deleted.
- A model gets linked to a definition when it is deployed with `bind_model_to_definition=True`.
  `ModelFilterOptions(definition_id_in=[...])` and `definition_id_is_null=True` find models by link.
