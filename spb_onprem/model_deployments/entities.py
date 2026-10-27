from typing import Any, Dict, List, Optional, Union

from spb_onprem.base_model import CustomBaseModel, Field

from .enums import ModelDeploymentRuntimeEndStatus, ModelDeploymentStatus


class ModelDeploymentRuntime(CustomBaseModel):
    """One run (generation) of a deployment as launched in the cluster. No secrets.

    A new generation starts with every ``start_model_deployment``. The
    activity history IDs point to the deploy activity (DEPLOY_MODEL) and the
    cleanup activity (STOP_MODEL_DEPLOYMENT or DELETE_MODEL_DEPLOYMENT) of this
    generation; they are filled shortly after the request.
    """

    deployment_id: Optional[str] = Field(None, alias="deploymentId")
    generation: Optional[int] = None
    namespace: Optional[str] = None
    resource_name: Optional[str] = Field(None, alias="resourceName")
    resource_uid: Optional[str] = Field(None, alias="resourceUid")
    image: Optional[str] = Field(None, description="Full image reference including the registry")
    start_script: Optional[str] = Field(None, alias="startScript")
    gpu_types: Optional[List[str]] = Field(None, alias="gpuTypes")
    gpu_count: Optional[int] = Field(None, alias="gpuCount")
    deploy_activity_history_id: Optional[str] = Field(None, alias="deployActivityHistoryId")
    cleanup_activity_history_id: Optional[str] = Field(None, alias="cleanupActivityHistoryId")
    requested_at: Optional[str] = Field(None, alias="requestedAt")
    registered_at: Optional[str] = Field(None, alias="registeredAt")
    ready_at: Optional[str] = Field(None, alias="readyAt")
    removed_at: Optional[str] = Field(None, alias="removedAt")
    # An unknown value from a newer platform stays a str instead of failing.
    end_status: Optional[Union[ModelDeploymentRuntimeEndStatus, str]] = Field(
        None, alias="endStatus", union_mode="left_to_right"
    )
    failure_reason: Optional[str] = Field(None, alias="failureReason")


class ModelDeployment(CustomBaseModel):
    """A model deployment: a model server that answers ``invoke`` calls.

    ``model_id`` is None for a base model deployment (the definition's server
    loads its own base weights). ``definition_id`` is None when the definition
    was deleted: the deployment can still be invoked, stopped and deleted, but
    not started again.

    ``parameters`` are the form values of the definition's ``params``, stored
    with the defaults filled in (``{"model_type": "edge"}``). The server gets
    them as ``SUPERB_PARAM_<KEY>`` environment variables. None for a
    deployment made before form values existed (the platform uses the
    defaults). ``expires_at`` None means it never expires.
    """

    id: Optional[str] = None
    dataset_id: Optional[str] = Field(None, alias="datasetId")
    definition_id: Optional[str] = Field(None, alias="definitionId")
    model_id: Optional[str] = Field(None, alias="modelId")
    name: Optional[str] = None
    description: Optional[str] = None
    # An unknown value from a newer platform stays a str instead of failing.
    status: Optional[Union[ModelDeploymentStatus, str]] = Field(None, union_mode="left_to_right")
    last_heartbeat_at: Optional[str] = Field(None, alias="lastHeartbeatAt")
    expires_at: Optional[str] = Field(None, alias="expiresAt")
    gpu_types: Optional[List[str]] = Field(None, alias="gpuTypes")
    gpu_count: Optional[int] = Field(None, alias="gpuCount")
    is_pinned: Optional[bool] = Field(None, alias="isPinned")
    started_at: Optional[str] = Field(None, alias="startedAt")
    invoke_timeout_seconds: Optional[int] = Field(None, alias="invokeTimeoutSeconds")
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Form values of the definition's params, defaults filled in. Not secret: stored as is."
    )
    runtime: Optional[ModelDeploymentRuntime] = Field(
        None, description="The current generation. Filled by get_model_deployment and the mutations, not by lists."
    )

    created_at: Optional[str] = Field(None, alias="createdAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    updated_by: Optional[str] = Field(None, alias="updatedBy")

    @property
    def is_base_model(self) -> bool:
        """True for a base model deployment (no trained model)."""
        return self.model_id is None


class ModelDeployDefinition(CustomBaseModel):
    """A deployment definition: the server image (and start script) a deployment runs.

    ``dataset_id`` is None for a definition shared by all datasets (system
    definitions included) and set for a definition of one dataset. System definitions
    come from the platform and cannot be deleted.

    ``params`` is the input form a deployment of this definition fills in
    (``create_model_deployment(parameters=...)``), in the shape of a training
    Param: ``{key: {"schema": {...}, "value": default, "description": ...}}``.
    None or ``{}``: no form items. An item without ``value`` whose schema does
    not allow null is required.
    """

    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    dataset_id: Optional[str] = Field(None, alias="datasetId")
    is_system: Optional[bool] = Field(None, alias="isSystem")
    is_pinned: Optional[bool] = Field(None, alias="isPinned")
    server_image_name: Optional[str] = Field(None, alias="serverImageName")
    server_image_tag: Optional[str] = Field(None, alias="serverImageTag", description="None means latest")
    start_script: Optional[str] = Field(None, alias="startScript")
    params: Optional[Dict[str, Any]] = Field(None, description="Input form items by key; None or {} for none")

    created_at: Optional[str] = Field(None, alias="createdAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    updated_by: Optional[str] = Field(None, alias="updatedBy")


class ModelDeployDefinitionInput(CustomBaseModel):
    """A new deployment definition (``create_model_deploy_definition``).

    Attributes:
        id: 3 to 63 lowercase letters, numbers and hyphens, starting with a
            letter. Training DAGs refer to it, so it cannot change later.
        name: 1 to 50 characters.
        server_image_name: Image repository path without a tag or digest. A
            name without a registry uses the platform registry.
        server_image_tag: Image tag. None means ``latest``.
        description: Up to 1000 characters.
        start_script: Runs instead of the image's default command (up to
            20000 characters). None runs the default command.
        dataset_only: True (default) makes the definition visible only in the
            dataset it is created in; False shares it with all datasets.
        params: The input form of its deployments, or None (no form). Keys
            match ``^[a-z][a-z0-9_]{0,63}$`` (at most 32); each item is
            ``{"schema": {...}, "value": default, "description": ...}`` like a
            training Param. ``schema.type`` is string, number, integer, boolean,
            array (of string enums) or object, or ``[type, "null"]`` for an
            optional item. The platform refuses widget hints
            (``platform_config.ui_type_hint``, ``platform_config.invisible``,
            ``x-superb-widget``, ``x-superb-gpu-supported``). Values reach the
            server as ``SUPERB_PARAM_<KEY>`` environment variables and are not
            secret.
    """

    id: str
    name: str
    server_image_name: str = Field(..., alias="serverImageName")
    server_image_tag: Optional[str] = Field(None, alias="serverImageTag")
    description: Optional[str] = None
    start_script: Optional[str] = Field(None, alias="startScript")
    dataset_only: bool = Field(True, alias="datasetOnly")
    params: Optional[Dict[str, Dict[str, Any]]] = None


class ModelDeployDefinitionUsage(CustomBaseModel):
    """Deployments and models in all datasets that use a definition."""

    deployment_count: Optional[int] = Field(None, alias="deploymentCount")
    model_count: Optional[int] = Field(None, alias="modelCount")


class ModelDeployDefinitionDeletion(CustomBaseModel):
    """Result of deleting a definition.

    Deployments are kept and lose the definition (``detached_deployment_count``):
    they can still be invoked, stopped and deleted, but not started again.
    Models are unlinked (``unlinked_model_count``).
    """

    id: Optional[str] = None
    detached_deployment_count: Optional[int] = Field(None, alias="detachedDeploymentCount")
    unlinked_model_count: Optional[int] = Field(None, alias="unlinkedModelCount")
