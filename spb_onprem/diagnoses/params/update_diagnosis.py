from typing import Optional, Union, Any

from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError

from ..enums import DiagnosisStatus


def update_diagnosis_params(
    dataset_id: str,
    diagnosis_id: str,
    name: Union[Optional[str], UndefinedType] = Undefined,
    description: Union[Optional[str], UndefinedType] = Undefined,
    status: Union[Optional[DiagnosisStatus], UndefinedType] = Undefined,
    score_key: Union[Optional[str], UndefinedType] = Undefined,
    score_value: Union[Optional[float], UndefinedType] = Undefined,
    score_unit: Union[Optional[str], UndefinedType] = Undefined,
    diagnosis_parameters: Union[Optional[dict], UndefinedType] = Undefined,
    contents: Union[Optional[dict], UndefinedType] = Undefined,
    source_slice_id: Union[Optional[str], UndefinedType] = Undefined,
    target_slice_id: Union[Optional[str], UndefinedType] = Undefined,
    source_data_count: Union[Optional[int], UndefinedType] = Undefined,
    target_data_count: Union[Optional[int], UndefinedType] = Undefined,
    diagnosis_data_count: Union[Optional[int], UndefinedType] = Undefined,
):
    if dataset_id is None:
        raise BadParameterError("dataset_id is required.")
    if diagnosis_id is None:
        raise BadParameterError("diagnosis_id is required.")

    variables = {
        "dataset_id": dataset_id,
        "diagnosis_id": diagnosis_id,
    }
    if name is not Undefined:
        variables["name"] = name
    if description is not Undefined:
        variables["description"] = description
    if status is not Undefined:
        variables["status"] = status.value if status is not None else None
    if score_key is not Undefined:
        variables["score_key"] = score_key
    if score_value is not Undefined:
        variables["score_value"] = score_value
    if score_unit is not Undefined:
        variables["score_unit"] = score_unit
    if diagnosis_parameters is not Undefined:
        variables["diagnosis_parameters"] = diagnosis_parameters
    if contents is not Undefined:
        variables["contents"] = contents
    if source_slice_id is not Undefined:
        variables["source_slice_id"] = source_slice_id
    if target_slice_id is not Undefined:
        variables["target_slice_id"] = target_slice_id
    if source_data_count is not Undefined:
        variables["source_data_count"] = source_data_count
    if target_data_count is not Undefined:
        variables["target_data_count"] = target_data_count
    if diagnosis_data_count is not Undefined:
        variables["diagnosis_data_count"] = diagnosis_data_count
    return variables
