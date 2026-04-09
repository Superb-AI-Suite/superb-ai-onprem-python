from typing import Optional, Union

from spb_onprem.base_types import Undefined, UndefinedType


def stop_workflow_run_params(
    workflow_run_id: str,
    reason: Union[Optional[str], UndefinedType] = Undefined,
):
    params = {
        "workflow_run_id": workflow_run_id,
    }
    if reason is not Undefined:
        params["reason"] = reason
    return params
