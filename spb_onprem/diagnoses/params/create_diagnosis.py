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
    contents: Optional[dict] = None,
    source_slice_id: Optional[str] = None,
    target_slice_id: Optional[str] = None,
    source_data_count: Optional[int] = None,
    target_data_count: Optional[int] = None,
    diagnosis_data_count: Optional[int] = None,
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
        "contents": contents,
        "source_slice_id": source_slice_id,
        "target_slice_id": target_slice_id,
        "source_data_count": source_data_count,
        "target_data_count": target_data_count,
        "diagnosis_data_count": diagnosis_data_count,
    }
