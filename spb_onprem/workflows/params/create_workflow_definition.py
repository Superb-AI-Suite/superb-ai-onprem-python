from typing import List, Union, Optional

from ..entities import WorkflowNodeDefinition


def create_workflow_definition_params(
    key: str,
    name: str,
    start_node_key: str,
    nodes: List[Union[WorkflowNodeDefinition, dict]],
    description: Optional[str] = None,
    trigger_schema: Optional[dict] = None,
):
    return {
        "key": key,
        "name": name,
        "description": description,
        "start_node_key": start_node_key,
        "trigger_schema": trigger_schema,
        "nodes": _dump_nodes(nodes),
    }


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
