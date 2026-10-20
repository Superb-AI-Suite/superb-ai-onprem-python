"""A small in-memory platform for the model deployment and template operations.

It answers the GraphQL documents the SDK sends (through ``BaseService.request_gql``)
with the rules of zenith (branch fde-85-model-task-type-vlm) that the SDK relies on:
status transitions of stop/start/delete, template visibility and deletion
(C17 revision 3), and DELETE_MODEL_DEPLOYMENT through startJob (C17 revision 2).
Data is synthetic.
"""
import copy
import itertools
import re
from typing import Any, Dict, List, Optional

ACTIVE = {"PENDING", "STARTING", "READY", "UNRESPONSIVE"}
ENDED = {"STOPPED", "FAILED", "EXPIRED"}
ADMIN = "admin@example.test"


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
            "cosmos3-reasoner": self._definition("cosmos3-reasoner", "Cosmos 3 Reasoner", None, system=True),
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
    def post(self, endpoint, json=None, headers=None):
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
    def _definition(definition_id, name, dataset_id, system=False, image="team/server", tag=None):
        return {"id": definition_id, "name": name, "description": None, "datasetId": dataset_id,
                "isSystem": system, "isPinned": False, "serverImageName": image, "serverImageTag": tag,
                "startScript": None, "createdAt": "2026-10-20T00:00:00.000Z", "createdBy": ADMIN,
                "updatedAt": "2026-10-20T00:00:00.000Z", "updatedBy": ADMIN}

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
        definition = self._definition(input["id"], input["name"], datasetId if input["datasetOnly"] else None,
                                      image=input["serverImageName"], tag=input.get("serverImageTag"))
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
                              bindModelToDefinition=False):
        self._vlm(datasetId)
        self._require_admin()
        if not self._visible(datasetId, definitionId):
            raise PlatformError("NOT_FOUND", "Model deploy definition not found.")
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
            "createdAt": "2026-10-20T00:00:00.000Z", "createdBy": ADMIN,
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

    def startModelDeployment(self, datasetId, deploymentId, expiresAt=None):
        self._require_admin()
        record = self._deployment(datasetId, deploymentId)
        if record["status"] not in ENDED:
            raise PlatformError("CONFLICT", "Only stopped, failed or expired deployments can be started.")
        if not record["definitionId"]:
            raise PlatformError("BAD_REQUEST", "The template of this deployment was deleted.")
        record.update(status="PENDING", generation=record["generation"] + 1)
        if expiresAt:
            record["expiresAt"] = expiresAt
        self._new_runtime(record)
        return self._with_runtime(record)

    def setModelDeploymentPinned(self, datasetId, deploymentId, isPinned):
        record = self._deployment(datasetId, deploymentId)
        record["isPinned"] = isPinned
        return record

    # activities -----------------------------------------------------------------
    def startJob(self, datasetId, jobType, parameters=None, sliceId=None, **_):
        if jobType != "DELETE_MODEL_DEPLOYMENT":
            raise PlatformError("BAD_REQUEST", f"Unexpected job type {jobType}.")
        if parameters.get("dataset_id") != datasetId:
            raise PlatformError("BAD_REQUEST", "Parameter dataset_id must be the activity dataset.")
        must = parameters["deployment_filter"].get("must") or {}
        ids = [r["id"] for r in self.modelDeployments(datasetId, {"must": must})["modelDeployments"]]
        history = {"id": f"history-{len(self.jobs) + 1}", "jobId": "job-delete-deployment",
                   "datasetId": datasetId, "status": "PENDING" if self.admin else "AWAITING_APPROVAL",
                   "parameters": parameters, "meta": {"deploymentIds": ids}}
        self.jobs.append(history)
        if self.admin:
            for deployment_id in ids:
                if self.deployments[deployment_id]["status"] in ENDED:
                    del self.deployments[deployment_id]
                else:
                    self.deployments[deployment_id]["status"] = "DELETING"
        return history

    # what the platform would do later --------------------------------------------
    def runtime_reports(self, deployment_id: str, status: str):
        """The sidecar / activity moves a deployment on (READY, FAILED, STOPPED, or removed)."""
        if status == "REMOVED":
            del self.deployments[deployment_id]
        else:
            self.deployments[deployment_id]["status"] = status
