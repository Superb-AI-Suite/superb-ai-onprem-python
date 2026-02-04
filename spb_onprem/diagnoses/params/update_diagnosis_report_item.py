from typing import Optional, Union

from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError
from spb_onprem.reports.entities.analytics_report_item import AnalyticsReportItemType


def update_diagnosis_report_item_params(
    dataset_id: str,
    diagnosis_id: str,
    diagnosis_report_item_id: str,
    name: Union[Optional[str], UndefinedType] = Undefined,
    type: Union[Optional[AnalyticsReportItemType], UndefinedType] = Undefined,
    content_id: Union[Optional[str], UndefinedType] = Undefined,
    description: Union[Optional[str], UndefinedType] = Undefined,
):
    if dataset_id is None:
        raise BadParameterError("dataset_id is required.")
    if diagnosis_id is None:
        raise BadParameterError("diagnosis_id is required.")
    if diagnosis_report_item_id is None:
        raise BadParameterError("diagnosis_report_item_id is required.")

    variables = {
        "dataset_id": dataset_id,
        "diagnosis_id": diagnosis_id,
        "diagnosis_report_item_id": diagnosis_report_item_id,
    }
    if name is not Undefined:
        variables["name"] = name
    if type is not Undefined:
        variables["type"] = type.value if type is not None else None
    if content_id is not Undefined:
        variables["content_id"] = content_id
    if description is not Undefined:
        variables["description"] = description
    return variables
