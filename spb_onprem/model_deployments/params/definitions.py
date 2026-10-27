from typing import Any, Mapping, Union

from pydantic import ValidationError

from spb_onprem.activities.deletion import require_id
from spb_onprem.exceptions import BadParameterError

from ..entities import ModelDeployDefinitionInput
from .deployments import json_object_variable


def model_deploy_definitions_params(dataset_id: str) -> dict:
    return {"datasetId": require_id(dataset_id, "dataset_id")}


def model_deploy_definition_params(dataset_id: str, definition_id: str) -> dict:
    return {
        "datasetId": require_id(dataset_id, "dataset_id"),
        "definitionId": require_id(definition_id, "definition_id"),
    }


def create_model_deploy_definition_params(
    dataset_id: str,
    definition: Union[ModelDeployDefinitionInput, Mapping[str, Any]],
) -> dict:
    """``definition`` is a ModelDeployDefinitionInput, or a dict with its field names or GraphQL names."""
    if isinstance(definition, Mapping):
        try:
            definition = ModelDeployDefinitionInput.model_validate(dict(definition))
        except ValidationError as error:
            raise BadParameterError(f"definition is invalid: {error}") from error
    if not isinstance(definition, ModelDeployDefinitionInput):
        raise BadParameterError("definition must be a ModelDeployDefinitionInput or a dict.")
    if definition.params is not None:
        # The same check as a deployment's parameters, before model_dump meets a value it cannot write.
        json_object_variable(definition.params, "definition.params")
    return {
        "datasetId": require_id(dataset_id, "dataset_id"),
        "input": definition.model_dump(mode="json", by_alias=True),
    }


def set_model_deploy_definition_pinned_params(dataset_id: str, definition_id: str, is_pinned: bool) -> dict:
    if not isinstance(is_pinned, bool):
        raise BadParameterError("is_pinned must be True or False.")
    variables = model_deploy_definition_params(dataset_id, definition_id)
    variables["isPinned"] = is_pinned
    return variables


def unbind_model_deploy_definition_params(dataset_id: str, model_id: str) -> dict:
    return {
        "datasetId": require_id(dataset_id, "dataset_id"),
        "modelId": require_id(model_id, "model_id"),
    }
