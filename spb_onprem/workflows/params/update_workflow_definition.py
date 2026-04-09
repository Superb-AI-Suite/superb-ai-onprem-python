from typing import List, Optional, Union

from spb_onprem.base_types import Undefined, UndefinedType

from ..entities import WorkflowNodeDefinition


def update_workflow_definition_params(
    workflow_definition_id: str,
    name: Union[Optional[str], UndefinedType] = Undefined,
    description: Union[Optional[str], UndefinedType] = Undefined,
    start_node_key: Union[Optional[str], UndefinedType] = Undefined,
    nodes: Union[Optional[List[Union[WorkflowNodeDefinition, dict]]], UndefinedType] = Undefined,
    trigger_schema: Union[Optional[dict], UndefinedType] = Undefined,
):
    params = {
        "workflow_definition_id": workflow_definition_id,
    }

    if name is not Undefined:
        params["name"] = name
    if description is not Undefined:
        params["description"] = description
    if start_node_key is not Undefined:
        params["start_node_key"] = start_node_key
    if trigger_schema is not Undefined:
        params["trigger_schema"] = trigger_schema
    if nodes is not Undefined:
        params["nodes"] = _dump_nodes(nodes or [])

    return params


def _dump_nodes(nodes: List[Union[WorkflowNodeDefinition, dict]]):
    dumped_nodes = []
    for node in nodes:
        if isinstance(node, WorkflowNodeDefinition):
            dumped_nodes.append(
                node.model_dump(by_alias=True, exclude_none=True, mode="json")
            )
        else:
            dumped_nodes.append(node)
    return dumped_nodes
