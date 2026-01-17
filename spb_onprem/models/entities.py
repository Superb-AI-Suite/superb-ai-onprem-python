from typing import Optional, List, TYPE_CHECKING, Union

from spb_onprem.base_model import CustomBaseModel, Field

from .enums import ModelStatus, ModelTaskType


class TrainingReportItem(CustomBaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    model_id: Optional[str] = Field(None, alias="modelId")
    content_id: Optional[str] = Field(None, alias="contentId")
    description: Optional[str] = None

    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_by: Optional[str] = Field(None, alias="updatedBy")


class Model(CustomBaseModel):
    dataset_id: Optional[str] = Field(None, alias="datasetId")
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ModelStatus] = None
    task_type: Optional[ModelTaskType] = Field(None, alias="taskType")
    custom_dag_id: Optional[str] = Field(None, alias="customDagId")

    total_data_count: Optional[int] = Field(None, alias="totalDataCount")
    train_data_count: Optional[int] = Field(None, alias="trainDataCount")
    validation_data_count: Optional[int] = Field(None, alias="validationDataCount")

    training_parameters: Optional[dict] = Field(None, alias="trainingParameters")
    training_report: Union[List[TrainingReportItem], None] = Field(None, alias="trainingReport")
    contents: Optional[dict] = Field(None, alias="contents")

    train_slice_id: Optional[str] = Field(None, alias="trainSliceId")
    validation_slice_id: Optional[str] = Field(None, alias="validationSliceId")

    completed_at: Optional[str] = Field(None, alias="completedAt")

    is_pinned: Optional[bool] = Field(None, alias="isPinned")
    score_key: Optional[str] = Field(None, alias="scoreKey")
    score_value: Optional[float] = Field(None, alias="scoreValue")
    score_unit: Optional[str] = Field(None, alias="scoreUnit")

    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_by: Optional[str] = Field(None, alias="updatedBy")


class ModelPageInfo(CustomBaseModel):
    models: Optional[List[Model]] = None
    next: Optional[str] = None
    total_count: Optional[int] = Field(None, alias="totalCount")
