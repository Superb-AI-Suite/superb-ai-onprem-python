from typing import Optional, List, Tuple, Union

from spb_onprem.base_service import BaseService
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError

from .queries import Queries
from .entities import Model
from .enums import ModelTaskType, ModelStatus
from .params import ModelFilter, ModelOrderBy


class ModelService(BaseService):
    def get_model(
        self,
        dataset_id: str,
        model_id: str,
    ) -> Optional[Model]:
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if model_id is None:
            raise BadParameterError("model_id is required.")

        response = self.request_gql(
            Queries.GET,
            Queries.GET["variables"](dataset_id=dataset_id, model_id=model_id),
        )
        return Model.model_validate(response) if response is not None else None

    def get_model_by_name(
        self,
        dataset_id: str,
        name: str,
    ) -> Optional[Model]:
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if name is None:
            raise BadParameterError("name is required.")

        response = self.request_gql(
            Queries.GET,
            Queries.GET["variables"](dataset_id=dataset_id, name=name),
        )
        return Model.model_validate(response) if response is not None else None

    def get_models(
        self,
        dataset_id: str,
        filter: Optional[ModelFilter] = None,
        order_by: Optional[ModelOrderBy] = None,
        cursor: Optional[str] = None,
        length: int = 10,
    ) -> Tuple[List[Model], Optional[str], int]:
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")

        response = self.request_gql(
            Queries.GET_LIST,
            Queries.GET_LIST["variables"](
                dataset_id=dataset_id,
                filter=filter,
                order_by=order_by,
                cursor=cursor,
                length=length,
            ),
        )

        models_list = response.get("models", []) if isinstance(response, dict) else []
        models = [Model.model_validate(model_dict) for model_dict in models_list]

        next_cursor = response.get("next") if isinstance(response, dict) else None
        total_count = response.get("totalCount", 0) if isinstance(response, dict) else 0

        return (
            models,
            next_cursor,
            total_count,
        )

    def create_model(
        self,
        dataset_id: str,
        name: str,
        task_type: ModelTaskType,
        description: Optional[str] = None,
        custom_dag_id: Optional[str] = None,
        total_data_count: Optional[int] = None,
        train_data_count: Optional[int] = None,
        validation_data_count: Optional[int] = None,
        training_parameters: Optional[dict] = None,
        train_slice_id: Optional[str] = None,
        validation_slice_id: Optional[str] = None,
        is_pinned: Optional[bool] = None,
        score_key: Optional[str] = None,
        score_value: Optional[float] = None,
        score_unit: Optional[str] = None,
    ) -> Model:
        response = self.request_gql(
            Queries.CREATE,
            Queries.CREATE["variables"](
                dataset_id=dataset_id,
                name=name,
                task_type=task_type,
                description=description,
                custom_dag_id=custom_dag_id,
                total_data_count=total_data_count,
                train_data_count=train_data_count,
                validation_data_count=validation_data_count,
                training_parameters=training_parameters,
                train_slice_id=train_slice_id,
                validation_slice_id=validation_slice_id,
                is_pinned=is_pinned,
                score_key=score_key,
                score_value=score_value,
                score_unit=score_unit,
            ),
        )
        return Model.model_validate(response)

    def update_model(
        self,
        dataset_id: str,
        model_id: str,
        name: Union[Optional[str], UndefinedType] = Undefined,
        description: Union[Optional[str], UndefinedType] = Undefined,
        status: Union[Optional[ModelStatus], UndefinedType] = Undefined,
        task_type: Union[Optional[ModelTaskType], UndefinedType] = Undefined,
        custom_dag_id: Union[Optional[str], UndefinedType] = Undefined,
        total_data_count: Union[Optional[int], UndefinedType] = Undefined,
        train_data_count: Union[Optional[int], UndefinedType] = Undefined,
        validation_data_count: Union[Optional[int], UndefinedType] = Undefined,
        training_parameters: Union[Optional[dict], UndefinedType] = Undefined,
        train_slice_id: Union[Optional[str], UndefinedType] = Undefined,
        validation_slice_id: Union[Optional[str], UndefinedType] = Undefined,
        is_pinned: Union[Optional[bool], UndefinedType] = Undefined,
        score_key: Union[Optional[str], UndefinedType] = Undefined,
        score_value: Union[Optional[float], UndefinedType] = Undefined,
        score_unit: Union[Optional[str], UndefinedType] = Undefined,
    ) -> Model:
        response = self.request_gql(
            Queries.UPDATE,
            Queries.UPDATE["variables"](
                dataset_id=dataset_id,
                model_id=model_id,
                name=name,
                description=description,
                status=status,
                task_type=task_type,
                custom_dag_id=custom_dag_id,
                total_data_count=total_data_count,
                train_data_count=train_data_count,
                validation_data_count=validation_data_count,
                training_parameters=training_parameters,
                train_slice_id=train_slice_id,
                validation_slice_id=validation_slice_id,
                is_pinned=is_pinned,
                score_key=score_key,
                score_value=score_value,
                score_unit=score_unit,
            ),
        )
        return Model.model_validate(response)

    def delete_model(
        self,
        dataset_id: str,
        model_id: str,
    ) -> bool:
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if model_id is None:
            raise BadParameterError("model_id is required.")

        response = self.request_gql(
            Queries.DELETE,
            Queries.DELETE["variables"](dataset_id=dataset_id, model_id=model_id),
        )
        return bool(response)
