"""A small in-memory platform for the model deployment and template operations.

It answers the GraphQL documents the SDK sends (through ``BaseService.request_gql``)
with the rules of zenith (branch fde-85-model-task-type-vlm) that the SDK relies on:
status transitions of stop/start/delete, template visibility and deletion
(C17 revision 3), and DELETE_MODEL_DEPLOYMENT through startJob: the request only
records the activity and the targets are picked when it runs (C20).
C38 (FDE-237, zenith 31a05ce): definition ``params`` (key rule, at most 32, no
widget hints), deployment ``parameters`` (unknown keys refused, defaults filled
in, required items; null for a deployment from before forms until its start),
the expiry input of start and ``setModelDeploymentExpiry`` (the expiry is
checked before the status, UNRESPONSIVE is refused, the same expiry changes
nothing). Data is synthetic.
"""
import copy
import itertools
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

ACTIVE = {"PENDING", "STARTING", "READY", "UNRESPONSIVE"}
ENDED = {"STOPPED", "FAILED", "EXPIRED"}
EXPIRY_CHANGEABLE = {"PENDING", "STARTING", "READY"}
ADMIN = "admin@example.test"
PARAM_KEY = re.compile(r"[a-z][a-z0-9_]{0,63}")
MODEL_TYPE_PARAM = {
    "schema": {"type": "string", "enum": ["edge", "nano"], "title": "Model type",
               "values_display": {"edge": "Cosmos3-Edge", "nano": "Cosmos3-Nano"}},
    "value": "edge",
    "description": "Base model size.",
}


class _Response:
    status_code = 200
    elapsed = None

    def __init__(self, body):
        self._body = body

    def raise_for_status(self):
        return None

    def json(self):
        return self._body


class PlatformError(Exception):
    def __init__(self, code: str, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.code = code
        self.details = details


class FakePlatform:
    """Use as ``patch.object(BaseService, "requests_retry_session", return_value=platform)``."""

    def __init__(self, dataset_id: str = "dataset-1", dataset_type: str = "VLM", admin: bool = True):
        self.dataset_id = dataset_id
        self.dataset_type = dataset_type
        self.admin = admin
        self.ids = (f"01JDEPLOY{n:017d}" for n in itertools.count(1))
        self.definitions: Dict[str, dict] = {
            "cosmos3-reasoner": self._definition("cosmos3-reasoner", "Cosmos 3 Reasoner", None, system=True,
                                                 params={"model_type": copy.deepcopy(MODEL_TYPE_PARAM)}),
        }
        self.models: Dict[str, dict] = {
            "model-1": {"datasetId": dataset_id, "id": "model-1", "name": "tuned", "status": "COMPLETED",
                        "definitionId": None},
        }
        self.deployments: Dict[str, dict] = {}
        self.runtimes: Dict[str, List[dict]] = {}
        self.jobs: List[dict] = []
        self.requests: List[dict] = []

    # session protocol ---------------------------------------------------------
    def post(self, endpoint, json=None, headers=None, allow_redirects=True, hooks=None):
        self.requests.append({"endpoint": endpoint, "payload": copy.deepcopy(json), "headers": headers})
        operation = re.search(r"\{\s*(\w+)", json["query"]).group(1)
        try:
            data = getattr(self, operation)(**json["variables"])
            return _Response({"data": {operation: copy.deepcopy(data)}})
        except PlatformError as error:
            body = {"message": str(error), "code": error.code}
            if error.details:
                body["details"] = error.details
            return _Response({"errors": [body], "data": None})

    def close(self):
        pass

    # helpers ------------------------------------------------------------------
    @staticmethod
    def _definition(definition_id, name, dataset_id, system=False, image="team/server", tag=None, params=None):
        return {"id": definition_id, "name": name, "description": None, "datasetId": dataset_id,
                "isSystem": system, "isPinned": False, "serverImageName": image, "serverImageTag": tag,
                "startScript": None, "params": params, "createdAt": "2026-10-20T00:00:00.000Z",
                "createdBy": ADMIN, "updatedAt": "2026-10-20T00:00:00.000Z", "updatedBy": ADMIN}

    @staticmethod
    def _check_params(params):
        """C38 item 1, the parts the SDK relies on."""
        if not params:
            return
        if len(params) > 32:
            raise PlatformError("BAD_REQUEST", "params can have at most 32 items.")
        for key, item in params.items():
            if not PARAM_KEY.fullmatch(key):
                raise PlatformError("BAD_REQUEST", f"params key {key!r} is invalid.")
            platform_config = item.get("platform_config") or {}
            schema = item.get("schema") or {}
            if ("ui_type_hint" in platform_config or "invisible" in platform_config
                    or "x-superb-widget" in schema or "x-superb-gpu-supported" in schema):
                raise PlatformError("BAD_REQUEST", f"params item {key!r} uses a widget hint.")

    @staticmethod
    def _fill_parameters(params, parameters):
        """C38 item 2: unknown keys refused, missing items get their default, required items checked."""
        params = params or {}
        parameters = dict(parameters or {})
        unknown = set(parameters) - set(params)
        if unknown:
            raise PlatformError("BAD_REQUEST", f"Unknown deployment parameters: {sorted(unknown)}.")
        for key, item in params.items():
            if key in parameters:
                enum = (item.get("schema") or {}).get("enum")
                if enum is not None and parameters[key] not in enum:
                    raise PlatformError("BAD_REQUEST", f"parameters.{key} must be one of {enum}.")
            elif "value" in item:
                parameters[key] = copy.deepcopy(item["value"])
            else:
                types = (item.get("schema") or {}).get("type")
                if "null" not in (types if isinstance(types, list) else [types]):
                    raise PlatformError("BAD_REQUEST", f"parameters.{key} is required.")
        return parameters

    @staticmethod
    def _instant(value):
        return None if value is None else datetime.fromisoformat(value.replace("Z", "+00:00"))

    @staticmethod
    def _expires_at(expiry):
        """C38 item 5: neverExpires takes no expiresAt; otherwise a future expiresAt is required."""
        if expiry["neverExpires"]:
            if expiry.get("expiresAt") is not None:
                raise PlatformError("BAD_REQUEST", "expiresAt must be empty when neverExpires is true.")
            return None
        if not expiry.get("expiresAt"):
            raise PlatformError("BAD_REQUEST", "expiresAt is required unless neverExpires is true.")
        if datetime.fromisoformat(expiry["expiresAt"].replace("Z", "+00:00")) <= datetime.now(timezone.utc):
            raise PlatformError("BAD_REQUEST", "expiresAt must be in the future.")
        return expiry["expiresAt"]

    def _vlm(self, datasetId):
        if datasetId != self.dataset_id:
            raise PlatformError("NOT_FOUND", "Dataset not found.", {"resource": "dataset"})
        if self.dataset_type != "VLM":
            raise PlatformError("BAD_REQUEST", "Model deployments require a vision-language dataset.")

    def _require_admin(self):
        if not self.admin:
            raise PlatformError("FORBIDDEN", "Forbidden.")

    def _visible(self, datasetId, definition_id):
        definition = self.definitions.get(definition_id)
        if definition and definition["datasetId"] in (None, datasetId):
            return definition
        return None

    def _deployment(self, datasetId, deploymentId):
        record = self.deployments.get(deploymentId)
        if not record or record["datasetId"] != datasetId:
            raise PlatformError("NOT_FOUND", "Model deployment not found.")
        return record

    def _with_runtime(self, record):
        result = dict(record)
        result["runtime"] = self.runtimes[record["id"]][0]
        return result

    def _new_runtime(self, record):
        self.runtimes.setdefault(record["id"], []).insert(0, {
            "deploymentId": record["id"], "generation": record["generation"], "gpuTypes": record["gpuTypes"],
            "gpuCount": record["gpuCount"], "requestedAt": "2026-10-20T00:00:00.000Z",
            "deployActivityHistoryId": f"history-deploy-{record['id']}-{record['generation']}",
            "cleanupActivityHistoryId": None, "endStatus": None,
        })

    # templates ------------------------------------------------------------------
    def modelDeployDefinitions(self, datasetId):
        self._vlm(datasetId)
        return [item for item in self.definitions.values() if item["datasetId"] in (None, datasetId)]

    def modelDeployDefinition(self, datasetId, definitionId):
        self._vlm(datasetId)
        return self._visible(datasetId, definitionId)

    def modelDeployDefinitionUsage(self, datasetId, definitionId):
        self._require_admin()
        if not self._visible(datasetId, definitionId):
            raise PlatformError("NOT_FOUND", "Model deploy definition not found.")
        return {
            "deploymentCount": sum(d["definitionId"] == definitionId for d in self.deployments.values()),
            "modelCount": sum(m["definitionId"] == definitionId for m in self.models.values()),
        }

    def createModelDeployDefinition(self, datasetId, input):
        self._vlm(datasetId)
        self._require_admin()
        if not re.fullmatch(r"[a-z][a-z0-9-]{1,61}[a-z0-9]", input["id"]):
            raise PlatformError("BAD_REQUEST", "id must be 3 to 63 lowercase letters, numbers, and hyphens.")
        if input["id"] in self.definitions:
            raise PlatformError("CONFLICT", "A deploy definition with this ID already exists.")
        self._check_params(input.get("params"))
        definition = self._definition(input["id"], input["name"], datasetId if input["datasetOnly"] else None,
                                      image=input["serverImageName"], tag=input.get("serverImageTag"),
                                      params=input.get("params"))
        definition.update(description=input.get("description"), startScript=input.get("startScript"))
        self.definitions[input["id"]] = definition
        return definition

    def deleteModelDeployDefinition(self, datasetId, definitionId):
        self._vlm(datasetId)
        self._require_admin()
        definition = self._visible(datasetId, definitionId)
        if not definition:
            raise PlatformError("NOT_FOUND", "Model deploy definition not found.")
        if definition["isSystem"]:
            raise PlatformError("BAD_REQUEST", "System templates cannot be deleted.")
        detached = unlinked = 0
        for record in self.deployments.values():
            if record["definitionId"] == definitionId:
                record["definitionId"] = None
                detached += 1
        for model in self.models.values():
            if model["definitionId"] == definitionId:
                model["definitionId"] = None
                unlinked += 1
        del self.definitions[definitionId]
        return {"id": definitionId, "detachedDeploymentCount": detached, "unlinkedModelCount": unlinked}

    def setModelDeployDefinitionPinned(self, datasetId, definitionId, isPinned):
        self._require_admin()
        definition = self._visible(datasetId, definitionId)
        if not definition:
            raise PlatformError("NOT_FOUND", "Model deploy definition not found.")
        definition["isPinned"] = isPinned
        return definition

    def unbindModelDeployDefinition(self, datasetId, modelId):
        self._require_admin()
        model = self.models[modelId]
        model["definitionId"] = None
        return model

    # deployments ----------------------------------------------------------------
    def createModelDeployment(self, datasetId, definitionId, name, modelId=None, description=None,
                              expiresAt=None, gpuTypes=None, gpuCount=None, invokeTimeoutSeconds=None,
                              bindModelToDefinition=False, parameters=None):
        self._vlm(datasetId)
        self._require_admin()
        definition = self._visible(datasetId, definitionId)
        if not definition:
            raise PlatformError("NOT_FOUND", "Model deploy definition not found.")
        parameters = self._fill_parameters(definition["params"], parameters)
        if modelId is not None:
            model = self.models.get(modelId)
            if not model:
                raise PlatformError("NOT_FOUND", "Model not found.", {"resource": "model"})
            if model["definitionId"] and model["definitionId"] != definitionId:
                raise PlatformError("BAD_REQUEST", "Model is not registered for this deployment definition.")
            if not model["definitionId"] and bindModelToDefinition:
                model["definitionId"] = definitionId
        record = {
            "id": next(self.ids), "datasetId": datasetId, "definitionId": definitionId, "modelId": modelId,
            "name": name, "description": description, "status": "PENDING", "lastHeartbeatAt": None,
            "expiresAt": expiresAt, "gpuTypes": gpuTypes or [], "gpuCount": gpuCount or 1, "isPinned": False,
            "startedAt": "2026-10-20T00:00:00.000Z", "invokeTimeoutSeconds": invokeTimeoutSeconds or 600,
            "parameters": parameters, "createdAt": "2026-10-20T00:00:00.000Z", "createdBy": ADMIN,
            "updatedAt": "2026-10-20T00:00:00.000Z", "updatedBy": ADMIN, "generation": 1,
        }
        self.deployments[record["id"]] = record
        self._new_runtime(record)
        return self._with_runtime(record)

    def modelDeployment(self, datasetId, deploymentId):
        self._vlm(datasetId)
        record = self.deployments.get(deploymentId)
        return self._with_runtime(record) if record and record["datasetId"] == datasetId else None

    def modelDeployments(self, datasetId, filter=None, orderBy=None, cursor=None, length=None):
        self._vlm(datasetId)
        records = list(self.deployments.values())
        must = (filter or {}).get("must") or {}
        if must.get("idIn"):
            records = [r for r in records if r["id"] in must["idIn"]]
        if must.get("statusIn"):
            records = [r for r in records if r["status"] in must["statusIn"]]
        if must.get("nameContains"):
            records = [r for r in records if must["nameContains"] in r["name"]]
        return {"modelDeployments": records, "next": None, "totalCount": len(records)}

    def modelDeploymentRuntimes(self, datasetId, deploymentId):
        self._deployment(datasetId, deploymentId)
        return self.runtimes[deploymentId]

    def updateModelDeployment(self, datasetId, deploymentId, **changes):
        self._require_admin()
        record = self._deployment(datasetId, deploymentId)
        record.update(changes)
        return self._with_runtime(record)

    def stopModelDeployment(self, datasetId, deploymentId):
        self._require_admin()
        record = self._deployment(datasetId, deploymentId)
        if record["status"] not in ACTIVE | {"STOPPING"}:
            raise PlatformError("CONFLICT", "Only pending or running deployments can be stopped.")
        record["status"] = "STOPPING"
        self.runtimes[deploymentId][0]["cleanupActivityHistoryId"] = f"history-stop-{deploymentId}"
        return self._with_runtime(record)

    def startModelDeployment(self, datasetId, deploymentId, expiry):
        self._require_admin()
        expires_at = self._expires_at(expiry)  # zenith checks the expiry first
        record = self._deployment(datasetId, deploymentId)
        if record["status"] not in ENDED:
            raise PlatformError("CONFLICT", "Only stopped, failed or expired deployments can be started.")
        if not record["definitionId"]:
            raise PlatformError("BAD_REQUEST", "The template of this deployment was deleted.")
        # Stored values (null for a deployment from before forms) are used as they are;
        # an item added to the definition since gets its default.
        parameters = self._fill_parameters(self.definitions[record["definitionId"]]["params"],
                                           record["parameters"])
        record.update(status="PENDING", generation=record["generation"] + 1, expiresAt=expires_at,
                      parameters=parameters)
        self._new_runtime(record)
        return self._with_runtime(record)

    def setModelDeploymentExpiry(self, datasetId, deploymentId, expiry):
        self._require_admin()
        expires_at = self._expires_at(expiry)  # zenith checks the expiry first
        record = self._deployment(datasetId, deploymentId)
        if record["status"] not in EXPIRY_CHANGEABLE:
            raise PlatformError("CONFLICT", "Only pending, starting or ready deployments can change the expiry.")
        if self._instant(record["expiresAt"]) == self._instant(expires_at):
            return self._with_runtime(record)  # the same expiry changes nothing
        record.update(expiresAt=expires_at, updatedAt=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
        return self._with_runtime(record)

    def setModelDeploymentPinned(self, datasetId, deploymentId, isPinned):
        record = self._deployment(datasetId, deploymentId)
        record["isPinned"] = isPinned
        return record

    # activities -----------------------------------------------------------------
    def startJob(self, datasetId, jobType, parameters=None, sliceId=None, **_):
        """C20: the request only records the activity; nothing is checked or changed yet."""
        if jobType != "DELETE_MODEL_DEPLOYMENT":
            raise PlatformError("BAD_REQUEST", f"Unexpected job type {jobType}.")
        history = {"id": f"history-{len(self.jobs) + 1}", "jobId": "job-delete-deployment",
                   "datasetId": datasetId, "status": "PENDING" if self.admin else "AWAITING_APPROVAL",
                   "parameters": parameters}
        self.jobs.append(history)
        return history

    def run_deletion_activity(self, history_id: str) -> dict:
        """What the DELETE_MODEL_DEPLOYMENT activity does when it runs (beginModelDeploymentDeletion)."""
        history = next(job for job in self.jobs if job["id"] == history_id)
        assert history["status"] == "PENDING", "an activity awaiting approval does not run"
        parameters = history["parameters"]
        deployment_filter = parameters.get("deployment_filter") or {}
        unknown = set(deployment_filter) - {"must", "not"} or set(deployment_filter.get("must") or {}) - {
            "idIn", "nameContains", "statusIn", "definitionIdIn"}
        if parameters.get("dataset_id") != history["datasetId"] or unknown:
            history["status"] = "FAILED"
            return history
        ids = [r["id"] for r in self.modelDeployments(history["datasetId"], deployment_filter)["modelDeployments"]]
        for deployment_id in ids:
            if self.deployments[deployment_id]["status"] in ENDED:
                del self.deployments[deployment_id]
            else:
                self.deployments[deployment_id]["status"] = "DELETING"
        history["status"] = "SUCCESS"
        return history

    # what the platform would do later --------------------------------------------
    def runtime_reports(self, deployment_id: str, status: str):
        """The sidecar / activity moves a deployment on (READY, FAILED, STOPPED, or removed)."""
        if status == "REMOVED":
            del self.deployments[deployment_id]
        else:
            self.deployments[deployment_id]["status"] = status
