from typing import Optional

from spb_onprem.exceptions import BadParameterError
from spb_onprem.reports.entities.analytics_report_item import AnalyticsReportItemType


def create_diagnosis_report_item_params(
    dataset_id: str,
    diagnosis_id: str,
    name: str,
    type: AnalyticsReportItemType,
    content_id: Optional[str] = None,
    description: Optional[str] = None,
    discriminator_value: Optional[str] = None,
):
    if dataset_id is None:
        raise BadParameterError("dataset_id is required.")
    if diagnosis_id is None:
        raise BadParameterError("diagnosis_id is required.")
    if name is None:
        raise BadParameterError("name is required.")
    if type is None:
        raise BadParameterError("type is required.")

    return {
        "dataset_id": dataset_id,
        "diagnosis_id": diagnosis_id,
        "name": name,
        "type": type.value,
        "content_id": content_id,
        "description": description,
        "discriminator_value": discriminator_value,
    }
