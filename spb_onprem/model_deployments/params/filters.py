from typing import Any, List, Mapping, Optional, Union

from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.exceptions import BadParameterError
from spb_onprem.models.enums import OrderDirection

from ..enums import ModelDeploymentOrderField, ModelDeploymentStatus


class ModelDeploymentFilterOptions(CustomBaseModel):
    """Conditions on model deployments. Every given condition must match.

    ``status_in`` uses the status as computed when the list is read
    (EXPIRED and UNRESPONSIVE included).
    """

    id_in: Optional[List[str]] = Field(None, alias="idIn")
    name_contains: Optional[str] = Field(None, alias="nameContains")
    status_in: Optional[List[ModelDeploymentStatus]] = Field(None, alias="statusIn")
    definition_id_in: Optional[List[str]] = Field(None, alias="definitionIdIn")


class ModelDeploymentFilter(CustomBaseModel):
    """``must`` conditions all match; a deployment matching any ``not`` condition is left out.

    The same shape as the ``deployment_filter`` of DELETE_MODEL_DEPLOYMENT.
    """

    must_filter: Optional[ModelDeploymentFilterOptions] = Field(None, alias="must")
    not_filter: Optional[ModelDeploymentFilterOptions] = Field(None, alias="not")


class ModelDeploymentOrderBy(CustomBaseModel):
    field: ModelDeploymentOrderField
    direction: OrderDirection


def filter_variable(
    value: Optional[Union[CustomBaseModel, Mapping[str, Any]]],
    expected: type,
    name: str,
) -> Optional[dict]:
    """A filter or order model as GraphQL input; a dict is sent as it is (GraphQL field names)."""
    if value is None:
        return None
    if isinstance(value, expected):
        return value.model_dump(mode="json", by_alias=True, exclude_unset=True)
    if isinstance(value, Mapping):
        return dict(value)
    raise BadParameterError(f"{name} must be {expected.__name__} or a dict.")
