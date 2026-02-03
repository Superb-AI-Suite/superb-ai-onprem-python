from typing import Optional, Any

from spb_onprem.exceptions import BadParameterError


def create_diagnosis_params(
    dataset_id: str,
    name: str,
    description: Optional[str] = None,
    score_key: Optional[str] = None,
    score_value: Optional[float] = None,
    score_unit: Optional[str] = None,
    diagnosis_parameters: Optional[dict] = None,
):
    if dataset_id is None:
        raise BadParameterError("dataset_id is required.")
    if name is None:
        raise BadParameterError("name is required.")

    return {
        "dataset_id": dataset_id,
        "name": name,
        "description": description,
        "score_key": score_key,
        "score_value": score_value,
        "score_unit": score_unit,
        "diagnosis_parameters": diagnosis_parameters,
    }
