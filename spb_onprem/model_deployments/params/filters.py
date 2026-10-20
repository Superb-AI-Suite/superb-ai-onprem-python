from typing import Any, List, Mapping, Optional, Union

from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.exceptions import BadDeletionTargetError, BadParameterError
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


FILTER_KEYS = ("must", "not")
FILTER_OPTION_KEYS = ("idIn", "nameContains", "statusIn", "definitionIdIn")


def check_deployment_filter_keys(value: Mapping[str, Any], name: str) -> None:
    """Refuse a dict filter with keys a ModelDeploymentFilter does not have.

    The platform checks the deletion filter only when the activity runs (C20),
    so a typo would end as a failed activity. The SDK refuses it before sending.
    """
    unknown = [key for key in value if key not in FILTER_KEYS]
    for side in FILTER_KEYS:
        options = value.get(side)
        if isinstance(options, Mapping):
            unknown += [f"{side}.{key}" for key in options if key not in FILTER_OPTION_KEYS]
    if unknown:
        raise BadDeletionTargetError(
            f"{name} has unknown keys {sorted(unknown)}; use {', '.join(FILTER_KEYS)} with "
            f"{', '.join(FILTER_OPTION_KEYS)} (GraphQL field names)."
        )
