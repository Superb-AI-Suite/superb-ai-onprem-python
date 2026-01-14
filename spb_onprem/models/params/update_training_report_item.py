from typing import Optional, Union

from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError
from spb_onprem.reports.entities.analytics_report_item import AnalyticsReportItemType


def update_training_report_item_params(
    dataset_id: str,
    model_id: str,
    training_report_id: str,
    name: Union[Optional[str], UndefinedType] = Undefined,
    type: Optional[AnalyticsReportItemType] = None,
    content_id: Union[Optional[str], UndefinedType] = Undefined,
    description: Union[Optional[str], UndefinedType] = Undefined,
):
    if dataset_id is None:
        raise BadParameterError("dataset_id is required.")
    if model_id is None:
        raise BadParameterError("model_id is required.")
    if training_report_id is None:
        raise BadParameterError("training_report_id is required.")

    variables = {
        "dataset_id": dataset_id,
        "model_id": model_id,
        "training_report_id": training_report_id,
    }

    if name is not Undefined:
        variables["name"] = name
    if content_id is not Undefined:
        variables["content_id"] = content_id
    if description is not Undefined:
        variables["description"] = description
    if type is not Undefined and type is not None:
        variables["type"] = type.value

    return variables
