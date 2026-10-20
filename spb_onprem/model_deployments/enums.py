from enum import Enum


class ModelDeploymentStatus(str, Enum):
    """Status of a model deployment, as the platform computes it when it is read.

    - PENDING: requested; the server is not launched yet.
    - STARTING: the server is launched and loads the model.
    - READY: the server answers; ``invoke`` works.
    - UNRESPONSIVE: no health report for a while (computed, not stored).
    - FAILED: the launch or the model loading failed. The server is removed.
    - STOPPING / DELETING: a stop or delete was requested; waiting until the
      server is removed.
    - STOPPED: stopped. ``start_model_deployment`` starts it again.
    - EXPIRED: ``expiresAt`` passed (computed). The server is removed.
    """

    PENDING = "PENDING"
    STARTING = "STARTING"
    READY = "READY"
    UNRESPONSIVE = "UNRESPONSIVE"
    FAILED = "FAILED"
    STOPPED = "STOPPED"
    EXPIRED = "EXPIRED"
    STOPPING = "STOPPING"
    DELETING = "DELETING"


#: The server is gone and stays gone until someone starts the deployment again
#: (``start_model_deployment`` runs it as a new generation).
ENDED_MODEL_DEPLOYMENT_STATUSES = frozenset({
    ModelDeploymentStatus.STOPPED,
    ModelDeploymentStatus.FAILED,
    ModelDeploymentStatus.EXPIRED,
})


class ModelDeploymentRuntimeEndStatus(str, Enum):
    """Why one run (generation) of a deployment ended. DELETED: removed by a delete."""

    STOPPED = "STOPPED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"
    DELETED = "DELETED"


class ModelDeploymentOrderField(str, Enum):
    CREATED_AT = "CREATED_AT"
    NAME = "NAME"
    EXPIRES_AT = "EXPIRES_AT"
