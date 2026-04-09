from typing import Optional


def start_workflow_run_params(
    workflow_definition_id: str,
    trigger_input: Optional[dict] = None,
):
    return {
        "workflow_definition_id": workflow_definition_id,
        "trigger_input": trigger_input,
    }
