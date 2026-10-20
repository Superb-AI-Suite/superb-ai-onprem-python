from typing import Optional, List

from spb_onprem.base_model import CustomBaseModel, Field

from ..enums import ModelStatus, ModelTaskType, ModelOrderField, OrderDirection


class ModelOrderBy(CustomBaseModel):
    field: ModelOrderField
    direction: OrderDirection


class ModelFilterOptions(CustomBaseModel):
    id_in: Optional[List[str]] = Field(None, alias="idIn")
    name_contains: Optional[str] = Field(None, alias="nameContains")
    status_in: Optional[List[ModelStatus]] = Field(None, alias="statusIn")
    task_type_in: Optional[List[ModelTaskType]] = Field(None, alias="taskTypeIn")
    created_by_in: Optional[List[str]] = Field(None, alias="createdByIn")
    score_key_in: Optional[List[str]] = Field(None, alias="scoreKeyIn")
    # Deployment template link (platforms with model deployments only).
    definition_id_in: Optional[List[str]] = Field(None, alias="definitionIdIn")
    definition_id_is_null: Optional[bool] = Field(
        None, alias="definitionIdIsNull", description="True: models without a template"
    )


class ModelFilter(CustomBaseModel):
    must_filter: Optional[ModelFilterOptions] = Field(None, alias="must")
    not_filter: Optional[ModelFilterOptions] = Field(None, alias="not")
