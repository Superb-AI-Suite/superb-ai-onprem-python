"""Model deployments and deployment templates (FDE-133)."""
import time
from typing import Any, Collection, List, Mapping, Optional, Tuple, Union
from urllib.parse import quote

import requests

from spb_onprem.activities.deletion import (
    DeletionActivityType,
    deletion_filter,
    require_id,
    start_deletion_activity,
)
from spb_onprem.activities.entities import ActivityHistory
from spb_onprem.base_service import BaseService
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError, BadResponseError
from spb_onprem.models.entities import Model

from .entities import (
    ModelDeployDefinition,
    ModelDeployDefinitionDeletion,
    ModelDeployDefinitionInput,
    ModelDeployDefinitionUsage,
    ModelDeployment,
    ModelDeploymentRuntime,
)
from .enums import ENDED_MODEL_DEPLOYMENT_STATUSES, ModelDeploymentStatus
from .invoke import DeploymentInvokeRequest, DeploymentInvokeResult, invoke_error, parse_multipart
from .params import ModelDeploymentFilter, ModelDeploymentOrderBy
from .params.filters import check_deployment_filter_keys
from .params.deployments import ExpiresAt
from .queries import Queries

#: Seconds to connect, and to wait for each read. The relay itself answers 504
#: TIMEOUT when the server sends no headers within the deployment's
#: ``invoke_timeout_seconds`` (at most 3600), and cuts a body that stalls for 60 s.
DEFAULT_INVOKE_TIMEOUT = (30.0, 3660.0)


class ModelDeploymentService(BaseService):
    """Create, watch, call, stop, start and delete model deployments.

    A deployment runs a template's server image with a trained model (or the
    template's base model) on GPUs and answers ``invoke_model_deployment``.
    Only VLM datasets have deployments.

    Lifecycle (the platform runs the activities; their progress shows in the
    Activity log):

    - ``create_model_deployment``: PENDING, then a DEPLOY_MODEL activity
      launches the server: STARTING, READY.
    - ``stop_model_deployment``: STOPPING, then STOP_MODEL_DEPLOYMENT removes
      the server: STOPPED.
    - ``start_model_deployment``: a STOPPED, FAILED or EXPIRED deployment runs
      again as a new generation (DEPLOY_MODEL).
    - ``delete_model_deployments``: one DELETE_MODEL_DEPLOYMENT activity for all
      targets. When it runs, a deployment whose server is gone is deleted at
      once; the others become DELETING until their server is removed.

    Creating, updating, stopping, starting, pinning and deleting need a dataset
    admin (Owner, WorkspaceAdmin or DATASET-ADMIN); another member's delete is
    submitted as AWAITING_APPROVAL. Reading and invoking need a role in the
    dataset (not Collaborator).

    Errors from the platform: ``InvalidInputError`` (BAD_REQUEST, for example not
    a VLM dataset, a model of another template, or starting a deployment whose
    template was deleted), ``ConflictError`` (the status does not allow it),
    ``NotFoundError`` and ``ForbiddenError``.
    """

    # Read --------------------------------------------------------------------
    def get_model_deployment(self, dataset_id: str, deployment_id: str) -> Optional[ModelDeployment]:
        """A deployment with its current runtime record, or None if there is none."""
        response = self.request_gql(
            Queries.GET_MODEL_DEPLOYMENT,
            Queries.GET_MODEL_DEPLOYMENT["variables"](dataset_id, deployment_id),
        )
        return ModelDeployment.model_validate(response) if response else None

    def get_model_deployments(
        self,
        dataset_id: str,
        filter: Optional[Union[ModelDeploymentFilter, Mapping[str, Any]]] = None,
        order_by: Optional[Union[ModelDeploymentOrderBy, Mapping[str, Any]]] = None,
        cursor: Optional[str] = None,
        length: int = 20,
    ) -> Tuple[List[ModelDeployment], Optional[str], int]:
        """One page of deployments: ``(deployments, next_cursor, total_count)``.

        Pinned deployments come first, then ``order_by`` (default: newest
        first). ``runtime`` is not filled in lists; use ``get_model_deployment``.

        Args:
            filter: A ModelDeploymentFilter, or a dict in GraphQL field names.
            order_by: A ModelDeploymentOrderBy, or a dict in GraphQL field names.
            cursor: ``next_cursor`` of the previous page.
            length: 1 to 100. Defaults to 20.
        """
        response = self.request_gql(
            Queries.GET_MODEL_DEPLOYMENTS,
            Queries.GET_MODEL_DEPLOYMENTS["variables"](dataset_id, filter, order_by, cursor, length),
        )
        response = response if isinstance(response, dict) else {}
        deployments = [ModelDeployment.model_validate(item) for item in response.get("modelDeployments") or []]
        return deployments, response.get("next"), response.get("totalCount", 0)

    def get_model_deployment_runtimes(self, dataset_id: str, deployment_id: str) -> List[ModelDeploymentRuntime]:
        """The runtime record of every generation of a deployment, newest first."""
        response = self.request_gql(
            Queries.GET_MODEL_DEPLOYMENT_RUNTIMES,
            Queries.GET_MODEL_DEPLOYMENT_RUNTIMES["variables"](dataset_id, deployment_id),
        )
        return [ModelDeploymentRuntime.model_validate(item) for item in response or []]

    def wait_for_model_deployment(
        self,
        dataset_id: str,
        deployment_id: str,
        until: Collection[ModelDeploymentStatus] = (ModelDeploymentStatus.READY,),
        timeout: float = 1800.0,
        poll_interval: float = 10.0,
    ) -> Optional[ModelDeployment]:
        """Wait until a deployment reaches one of ``until`` and return it.

        It also returns, without raising, when the deployment reaches STOPPED,
        FAILED or EXPIRED (it stays there until someone starts it again), and
        returns None when the deployment no longer exists (deleted). Check
        ``status`` of what it returns.

        Args:
            until: Statuses to wait for. Defaults to READY.
            timeout: Seconds to wait in total. Defaults to 1800 (loading a large
                model can take minutes).
            poll_interval: Seconds between two reads. Defaults to 10.

        Raises:
            TimeoutError: If none of these happened within ``timeout``. The
                message has the last status seen.
        """
        if timeout <= 0:
            raise ValueError("timeout must be positive.")
        if poll_interval <= 0:
            raise ValueError("poll_interval must be positive.")
        targets = {ModelDeploymentStatus(status) for status in until}
        deadline = time.monotonic() + timeout
        while True:
            deployment = self.get_model_deployment(dataset_id, deployment_id)
            if deployment is None or deployment.status in targets or deployment.status in ENDED_MODEL_DEPLOYMENT_STATUSES:
                return deployment
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                status = getattr(deployment.status, "value", deployment.status)
                raise TimeoutError(
                    f"Model deployment {deployment_id} did not reach "
                    f"{sorted(status.value for status in targets)} within {timeout:g}s (last status: {status})."
                )
            time.sleep(min(poll_interval, remaining))

    # Change ------------------------------------------------------------------
    def create_model_deployment(
        self,
        dataset_id: str,
        definition_id: str,
        name: str,
        model_id: Optional[str] = None,
        description: Optional[str] = None,
        expires_at: Optional[ExpiresAt] = None,
        gpu_types: Optional[List[str]] = None,
        gpu_count: Optional[int] = None,
        invoke_timeout_seconds: Optional[int] = None,
        bind_model_to_definition: bool = False,
    ) -> ModelDeployment:
        """Deploy a model with a template. The deployment starts as PENDING.

        The platform starts a DEPLOY_MODEL activity that launches the server.
        Use ``wait_for_model_deployment`` to wait until it is READY.

        Args:
            dataset_id: A VLM dataset.
            definition_id: The template (``ModelDeployDefinition.id``) visible
                in this dataset.
            name: 1 to 256 characters.
            model_id: A COMPLETED model of the dataset. None deploys the
                template's base model (no fine-tuned weights).
            description: Free text.
            expires_at: When the server is removed: a datetime, an ISO 8601
                string, or a timedelta from now. None never expires.
            gpu_types: GPU product labels the server may run on (for example
                ``["NVIDIA-A100-SXM4-80GB"]``). None or empty: any GPU.
            gpu_count: 1 to 8. Defaults to 1.
            invoke_timeout_seconds: 10 to 3600 seconds the invoke relay waits for
                the server's response headers. Defaults to 600.
            bind_model_to_definition: For a model without a template only: True
                links the model to this template; False (default) deploys it
                once without linking. A model linked to another template is
                refused (InvalidInputError).
        """
        response = self.request_gql(
            Queries.CREATE_MODEL_DEPLOYMENT,
            Queries.CREATE_MODEL_DEPLOYMENT["variables"](
                dataset_id=dataset_id,
                definition_id=definition_id,
                name=name,
                model_id=model_id,
                description=description,
                expires_at=expires_at,
                gpu_types=gpu_types,
                gpu_count=gpu_count,
                invoke_timeout_seconds=invoke_timeout_seconds,
                bind_model_to_definition=bind_model_to_definition,
            ),
        )
        return ModelDeployment.model_validate(response)

    def update_model_deployment(
        self,
        dataset_id: str,
        deployment_id: str,
        name: Union[str, UndefinedType] = Undefined,
        description: Union[Optional[str], UndefinedType] = Undefined,
        invoke_timeout_seconds: Union[int, UndefinedType] = Undefined,
    ) -> ModelDeployment:
        """Change the name, description or invoke timeout. Only the given arguments change.

        A new ``invoke_timeout_seconds`` applies to the next call at once (no restart).
        ``description=None`` clears the description.
        """
        response = self.request_gql(
            Queries.UPDATE_MODEL_DEPLOYMENT,
            Queries.UPDATE_MODEL_DEPLOYMENT["variables"](
                dataset_id=dataset_id,
                deployment_id=deployment_id,
                name=name,
                description=description,
                invoke_timeout_seconds=invoke_timeout_seconds,
            ),
        )
        return ModelDeployment.model_validate(response)

    def stop_model_deployment(self, dataset_id: str, deployment_id: str) -> ModelDeployment:
        """Stop a PENDING, STARTING, READY or UNRESPONSIVE deployment.

        It becomes STOPPING; a STOP_MODEL_DEPLOYMENT activity removes the server
        and frees the GPUs, then it is STOPPED. Stopping a STOPPING deployment
        again retries the cleanup. Other statuses: ConflictError.

        Returns:
            ModelDeployment: The deployment, STOPPING. The cleanup activity's ID
            appears shortly after in ``runtime.cleanup_activity_history_id``.
        """
        response = self.request_gql(
            Queries.STOP_MODEL_DEPLOYMENT,
            Queries.STOP_MODEL_DEPLOYMENT["variables"](dataset_id, deployment_id),
        )
        return ModelDeployment.model_validate(response)

    def start_model_deployment(
        self,
        dataset_id: str,
        deployment_id: str,
        expires_at: Optional[ExpiresAt] = None,
    ) -> ModelDeployment:
        """Start a STOPPED, FAILED or EXPIRED deployment again as a new generation (PENDING).

        Other statuses: ConflictError. A deployment whose template was deleted
        cannot start again (InvalidInputError); delete it and create a new one.

        Args:
            expires_at: A new expiry (datetime, ISO 8601 string or timedelta
                from now). Without it, a remaining expiry is kept and a passed
                one is renewed for the same duration.
        """
        response = self.request_gql(
            Queries.START_MODEL_DEPLOYMENT,
            Queries.START_MODEL_DEPLOYMENT["variables"](dataset_id, deployment_id, expires_at),
        )
        return ModelDeployment.model_validate(response)

    def set_model_deployment_pinned(self, dataset_id: str, deployment_id: str, is_pinned: bool) -> ModelDeployment:
        """Pin or unpin a deployment. Pinned deployments come first for everyone."""
        response = self.request_gql(
            Queries.SET_MODEL_DEPLOYMENT_PINNED,
            Queries.SET_MODEL_DEPLOYMENT_PINNED["variables"](dataset_id, deployment_id, is_pinned),
        )
        return ModelDeployment.model_validate(response)

    def delete_model_deployments(
        self,
        dataset_id: str,
        deployment_ids: Optional[List[str]] = None,
        deployment_filter: Optional[Union[ModelDeploymentFilter, dict]] = None,
    ) -> ActivityHistory:
        """Start deleting deployments.

        Starts one ``DELETE_MODEL_DEPLOYMENT`` activity with ``deployment_ids``
        or ``deployment_filter`` as its filter (pass exactly one). The request
        changes no deployment. When the activity runs, it picks the deployments
        that match at that moment: one whose server is gone (STOPPED, FAILED,
        EXPIRED) is deleted at once, the others become DELETING and are deleted
        when their server is removed. Runtime records go with the deployment.
        Running deployments may be deleted without a stop.

        Nothing matching (or already deleted) is a success that deletes
        nothing. A condition the activity cannot handle (for example a filter
        the platform refuses, or a server that cannot be removed) makes the
        activity FAILED in the Activity log; it is not an error of this call.
        Use ``ActivityService.wait_for_activity`` and check its ``status``.

        A caller who is not an admin of the dataset (Owner, WorkspaceAdmin or
        DATASET-ADMIN) submits it as AWAITING_APPROVAL; nothing happens until
        an admin approves.

        Args:
            dataset_id (str): The dataset ID.
            deployment_ids (Optional[List[str]]): The deployment IDs.
            deployment_filter (Optional[ModelDeploymentFilter | dict]): A
                ModelDeploymentFilter (``{"must": ..., "not": ...}``). A dict is
                sent as it is, in the GraphQL field names (``idIn``,
                ``nameContains``, ``statusIn``, ``definitionIdIn``). A filter
                without a condition is refused. A filter with only ``not``
                selects every deployment except those.

        Raises:
            BadParameterError: If dataset_id is missing.
            BadDeletionTargetError: If none or both of deployment_ids and
                deployment_filter are given, they are empty, or a dict filter
                has an unknown key (also a ValueError).
            InvalidInputError / ForbiddenError: If the platform refuses the
                request itself (for example no role in the dataset).

        Returns:
            ActivityHistory: The started activity.
        """
        require_id(dataset_id, "dataset_id")
        if isinstance(deployment_filter, Mapping):
            check_deployment_filter_keys(deployment_filter, "deployment_filter")
        parameters = {
            "dataset_id": dataset_id,
            "deployment_filter": deletion_filter(
                ids=deployment_ids,
                ids_name="deployment_ids",
                filter=deployment_filter,
                filter_name="deployment_filter",
                filter_types=(ModelDeploymentFilter,),
            ),
        }
        return start_deletion_activity(
            self, dataset_id, DeletionActivityType.DELETE_MODEL_DEPLOYMENT, parameters
        )

    # Call --------------------------------------------------------------------
    def invoke_model_deployment(
        self,
        dataset_id: str,
        deployment_id: str,
        request: DeploymentInvokeRequest,
        timeout: Union[float, Tuple[float, float]] = DEFAULT_INVOKE_TIMEOUT,
    ) -> DeploymentInvokeResult:
        """Call a READY deployment through the platform's invoke relay.

        Sends ``request`` as ``multipart/form-data`` to
        ``{host}/graphql/model-deployments/{dataset_id}/{deployment_id}/invoke``
        and returns the server's multipart response as parts. The call is never
        retried: a model server handles one request at a time and a retry can
        run the model twice.

        The whole request (at most 1 GiB) and response are held in memory.
        It needs an access key config (``~/.spb/onprem-config``); the system
        SDK cannot call the relay.

        Args:
            request: The parts to send (``DeploymentInvokeRequest``).
            timeout: ``requests`` timeout: seconds, or ``(connect, read)``. The
                read timeout is the longest silence between two reads.

        Raises:
            DeploymentInvokeError: The relay or the server refused or failed the
                call (``status_code``, ``code``, ``message``, ``retry_after``). Also
                ``ForbiddenError`` (403), ``NotFoundError`` (404),
                ``ConflictError`` (not READY, or busy) or ``InvalidInputError``
                (invalid, too large or unprocessable input), by status.
            BadResponseError: The connection failed, or the success response is
                not a complete multipart body.

        Returns:
            DeploymentInvokeResult: The response parts in order.
        """
        if not isinstance(request, DeploymentInvokeRequest):
            raise BadParameterError("request must be a DeploymentInvokeRequest.")
        url = (
            f"{self._auth_user.host.rstrip('/')}/graphql/model-deployments/"
            f"{quote(require_id(dataset_id, 'dataset_id'), safe='')}/"
            f"{quote(require_id(deployment_id, 'deployment_id'), safe='')}/invoke"
        )
        files = request.multipart_files()
        try:
            # No retry session: a retried invoke runs the model again.
            response = requests.post(
                url,
                files=files,
                headers=dict(self._auth_user.auth_headers),
                timeout=timeout,
                allow_redirects=False,
            )
        except requests.exceptions.RequestException as error:
            # The exception text has the URL only (no credentials, no query).
            raise BadResponseError(f"Model deployment invoke failed: {type(error).__name__}: {error}") from error
        if response.status_code != 200:
            if 300 <= response.status_code < 400:
                raise BadResponseError(
                    f"Model deployment invoke got an unexpected redirect (HTTP {response.status_code})."
                )
            raise invoke_error(response.status_code, response.content, response.headers.get("Retry-After"))
        content_type = response.headers.get("Content-Type", "")
        return DeploymentInvokeResult(
            status_code=response.status_code,
            content_type=content_type,
            parts=tuple(parse_multipart(content_type, response.content)),
        )


class ModelDeployDefinitionService(BaseService):
    """Deployment templates (model deploy definitions).

    A template names the server image (and start script) a deployment runs.
    System templates come from the platform. Other templates are shared by
    all datasets or belong to one dataset.

    - Creating and deleting a template (shared or dataset-only) needs Owner or
      WorkspaceAdmin. Templates cannot be edited; delete and create again.
    - Deleting a template keeps its deployments and models: deployments lose
      the template (they can still be invoked, stopped and deleted, but not
      started again) and models are unlinked. System templates cannot be
      deleted. Deleting a dataset deletes its dataset-only templates.
    - A model is linked to a template when it is deployed with
      ``bind_model_to_definition=True``; ``unbind_model_deploy_definition``
      unlinks it.
    """

    def get_model_deploy_definitions(self, dataset_id: str) -> List[ModelDeployDefinition]:
        """The templates a dataset can use: system, shared and its own. Only VLM datasets have them."""
        response = self.request_gql(
            Queries.GET_MODEL_DEPLOY_DEFINITIONS,
            Queries.GET_MODEL_DEPLOY_DEFINITIONS["variables"](dataset_id),
        )
        return [ModelDeployDefinition.model_validate(item) for item in response or []]

    def get_model_deploy_definition(self, dataset_id: str, definition_id: str) -> Optional[ModelDeployDefinition]:
        """A template visible in the dataset, or None."""
        response = self.request_gql(
            Queries.GET_MODEL_DEPLOY_DEFINITION,
            Queries.GET_MODEL_DEPLOY_DEFINITION["variables"](dataset_id, definition_id),
        )
        return ModelDeployDefinition.model_validate(response) if response else None

    def get_model_deploy_definition_usage(self, dataset_id: str, definition_id: str) -> ModelDeployDefinitionUsage:
        """How many deployments and models in all datasets use a template (Owner or WorkspaceAdmin)."""
        response = self.request_gql(
            Queries.GET_MODEL_DEPLOY_DEFINITION_USAGE,
            Queries.GET_MODEL_DEPLOY_DEFINITION_USAGE["variables"](dataset_id, definition_id),
        )
        return ModelDeployDefinitionUsage.model_validate(response)

    def create_model_deploy_definition(
        self,
        dataset_id: str,
        definition: Union[ModelDeployDefinitionInput, Mapping[str, Any]],
    ) -> ModelDeployDefinition:
        """Create a template (Owner or WorkspaceAdmin).

        ``definition.dataset_only`` (default True) keeps it in ``dataset_id``;
        False shares it with all datasets. An ID that is taken (also by a system
        template) raises ConflictError.
        """
        response = self.request_gql(
            Queries.CREATE_MODEL_DEPLOY_DEFINITION,
            Queries.CREATE_MODEL_DEPLOY_DEFINITION["variables"](dataset_id, definition),
        )
        return ModelDeployDefinition.model_validate(response)

    def delete_model_deploy_definition(self, dataset_id: str, definition_id: str) -> ModelDeployDefinitionDeletion:
        """Delete a template at once (no activity, no files; Owner or WorkspaceAdmin).

        Deployments in all datasets that use it are kept and detached, and
        linked models are unlinked; the result has both counts. A system
        template raises InvalidInputError.
        """
        response = self.request_gql(
            Queries.DELETE_MODEL_DEPLOY_DEFINITION,
            Queries.DELETE_MODEL_DEPLOY_DEFINITION["variables"](dataset_id, definition_id),
        )
        return ModelDeployDefinitionDeletion.model_validate(response)

    def set_model_deploy_definition_pinned(
        self, dataset_id: str, definition_id: str, is_pinned: bool
    ) -> ModelDeployDefinition:
        """Pin or unpin a template (system ones too; Owner or WorkspaceAdmin). Pinned ones come first."""
        response = self.request_gql(
            Queries.SET_MODEL_DEPLOY_DEFINITION_PINNED,
            Queries.SET_MODEL_DEPLOY_DEFINITION_PINNED["variables"](dataset_id, definition_id, is_pinned),
        )
        return ModelDeployDefinition.model_validate(response)

    def unbind_model_deploy_definition(self, dataset_id: str, model_id: str) -> Model:
        """Unlink a model from its template (``definition_id`` becomes None). Idempotent.

        Deployments of the model keep their own template.
        """
        response = self.request_gql(
            Queries.UNBIND_MODEL_DEPLOY_DEFINITION,
            Queries.UNBIND_MODEL_DEPLOY_DEFINITION["variables"](dataset_id, model_id),
        )
        return Model.model_validate(response)
