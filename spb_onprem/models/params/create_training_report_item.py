from typing import Optional

from spb_onprem.exceptions import BadParameterError
from spb_onprem.reports.entities.analytics_report_item import AnalyticsReportItemType


def create_training_report_item_params(
    dataset_id: str,
    model_id: str,
    name: str,
    type: AnalyticsReportItemType,
    content_id: Optional[str] = None,
    description: Optional[str] = None,
):
    if dataset_id is None:
        raise BadParameterError("dataset_id is required.")
    if model_id is None:
        raise BadParameterError("model_id is required.")
    if name is None:
        raise BadParameterError("name is required.")
    if type is None:
        raise BadParameterError("type is required.")
    

    return {
        "dataset_id": dataset_id,
        "model_id": model_id,
        "name": name,
        "type": type.value,
        "content_id": content_id,
        "description": description,
    }
