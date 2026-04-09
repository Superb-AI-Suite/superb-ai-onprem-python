from typing import Optional

from spb_onprem.exceptions import BadParameterError


def get_workflow_runs_params(
    cursor: Optional[str] = None,
    length: int = 10,
):
    if length < 1 or length > 50:
        raise BadParameterError("length must be between 1 and 50.")

    return {
        "cursor": cursor,
        "length": length,
    }
