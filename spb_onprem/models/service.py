from typing import Optional, List, Tuple, Union

from spb_onprem.base_service import BaseService
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError
from spb_onprem.activities.deletion import (
    DeletionActivityType,
    deletion_filter,
    require_id,
    start_deletion_activity,
    warn_deprecated,
)
from spb_onprem.activities.entities import ActivityHistory
from spb_onprem.reports.entities.analytics_report_item import AnalyticsReportItemType
from spb_onprem.contents.service import ContentService
from spb_onprem.charts import ChartDataResult

from .queries import Queries
from .entities import Model, TrainingAnnotations
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
        training_annotations: Optional[list[TrainingAnnotations]] = None,
        training_parameters: Optional[dict] = None,
        train_slice_id: Optional[str] = None,
        validation_slice_id: Optional[str] = None,
        is_pinned: Optional[bool] = None,
        score_key: Optional[str] = None,
        score_value: Optional[float] = None,
        score_unit: Optional[str] = None,
        contents: Optional[dict] = None,
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
                training_annotations=training_annotations,
                training_parameters=training_parameters,
                train_slice_id=train_slice_id,
                validation_slice_id=validation_slice_id,
                is_pinned=is_pinned,
                score_key=score_key,
                score_value=score_value,
                score_unit=score_unit,
                contents=contents,
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
        training_annotations: Union[Optional[list[TrainingAnnotations]], UndefinedType] = Undefined,
        training_parameters: Union[Optional[dict], UndefinedType] = Undefined,
        train_slice_id: Union[Optional[str], UndefinedType] = Undefined,
        validation_slice_id: Union[Optional[str], UndefinedType] = Undefined,
        is_pinned: Union[Optional[bool], UndefinedType] = Undefined,
        score_key: Union[Optional[str], UndefinedType] = Undefined,
        score_value: Union[Optional[float], UndefinedType] = Undefined,
        score_unit: Union[Optional[str], UndefinedType] = Undefined,
        contents: Union[Optional[dict], UndefinedType] = Undefined,
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
                training_annotations=training_annotations,
                training_parameters=training_parameters,
                train_slice_id=train_slice_id,
                validation_slice_id=validation_slice_id,
                is_pinned=is_pinned,
                score_key=score_key,
                score_value=score_value,
                score_unit=score_unit,
                contents=contents,
            ),
        )
        return Model.model_validate(response)

    def delete_models(
        self,
        dataset_id: str,
        model_ids: Optional[List[str]] = None,
        model_filter: Optional[Union[ModelFilter, dict]] = None,
    ) -> ActivityHistory:
        """Start deleting models.

        Starts one ``DELETE_MODEL`` activity for every model that ``model_ids``
        or ``model_filter`` selects (pass exactly one). The activity deletes
        each model, its training report and their files. Diagnoses made with the
        models stay. To block until it ends, use
        ``ActivityService.wait_for_activity``.
        Targets are found when the activity runs. If none match or they are
        already deleted, it succeeds without deleting anything. A target that
        cannot be deleted then (still training, or used by a deployment) is not refused at request time; the
        activity ends FAILED (see its ``status`` and ``meta``).
        A caller who is not an admin of the dataset (Owner, WorkspaceAdmin or
        DATASET-ADMIN) submits it as AWAITING_APPROVAL.

        Args:
            dataset_id (str): The dataset ID.
            model_ids (Optional[List[str]]): The model IDs.
            model_filter (Optional[ModelFilter | dict]): A ModelFilter
                (``{"must": ..., "not": ...}``). A dict is sent as it is, in
                the GraphQL field names. A filter without a condition is refused.
                A filter with only ``not`` selects every target except those.

        Raises:
            BadParameterError: If dataset_id is missing.
            BadDeletionTargetError: If none or both of model_ids and
                model_filter are given, or they are empty (also a
                ValueError).
            InvalidInputError: If the platform refuses the filter (format
                checks at request time, e.g. an empty ``idIn``).
            UnknownError: Other request errors (e.g. no role in the dataset).

        Returns:
            ActivityHistory: The started activity.
        """
        require_id(dataset_id, "dataset_id")
        parameters = {
            "dataset_id": dataset_id,
            "model_filter": deletion_filter(
                ids=model_ids,
                ids_name="model_ids",
                filter=model_filter,
                filter_name="model_filter",
                filter_types=(ModelFilter,),
            ),
        }
        return start_deletion_activity(
            self, dataset_id, DeletionActivityType.DELETE_MODEL, parameters
        )

    def delete_model(
        self,
        dataset_id: str,
        model_id: str,
    ) -> ActivityHistory:
        """Start deleting one model. Deprecated: use ``delete_models``.

        It will be removed in the next major version. It warns with
        DeprecationWarning and calls ``delete_models(dataset_id, model_ids=[model_id])``,
        so it starts one activity with the filter ``{"must": {"idIn": [model_id]}}``.
        Calling it in a loop starts one activity per model; pass all the IDs to
        ``delete_models`` instead.

        Raises:
            BadParameterError: If dataset_id or model_id is missing.

        Returns:
            ActivityHistory: The started activity.
        """
        warn_deprecated("delete_model", "delete_models", "model", "model_ids", "model_filter")
        require_id(dataset_id, "dataset_id")
        require_id(model_id, "model_id")
        return self.delete_models(dataset_id, model_ids=[model_id])

    def create_training_report_item(
        self,
        dataset_id: str,
        model_id: str,
        name: str,
        type: AnalyticsReportItemType,
        content_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Model:
        response = self.request_gql(
            Queries.CREATE_TRAINING_REPORT,
            Queries.CREATE_TRAINING_REPORT["variables"](
                dataset_id=dataset_id,
                model_id=model_id,
                name=name,
                type=type,
                content_id=content_id,
                description=description,
            ),
        )
        return Model.model_validate(response)

    def update_training_report_item(
        self,
        dataset_id: str,
        model_id: str,
        training_report_id: str,
        name: Union[Optional[str], UndefinedType] = Undefined,
        type: Union[Optional[AnalyticsReportItemType], UndefinedType] = Undefined,
        content_id: Union[Optional[str], UndefinedType] = Undefined,
        description: Union[Optional[str], UndefinedType] = Undefined,
    ) -> Model:
        response = self.request_gql(
            Queries.UPDATE_TRAINING_REPORT,
            Queries.UPDATE_TRAINING_REPORT["variables"](
                dataset_id=dataset_id,
                model_id=model_id,
                training_report_id=training_report_id,
                name=name,
                type=type,
                content_id=content_id,
                description=description,
            ),
        )
        return Model.model_validate(response)

    def delete_training_report_item(
        self,
        dataset_id: str,
        model_id: str,
        training_report_id: str,
    ) -> Model:
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if model_id is None:
            raise BadParameterError("model_id is required.")
        if training_report_id is None:
            raise BadParameterError("training_report_id is required.")

        response = self.request_gql(
            Queries.DELETE_TRAINING_REPORT,
            Queries.DELETE_TRAINING_REPORT["variables"](
                dataset_id=dataset_id,
                model_id=model_id,
                training_report_id=training_report_id,
            ),
        )
        return Model.model_validate(response)

    def _upload_json_file(
        self,
        content_id: str,
        file_name: str,
        data: dict,
    ) -> bool:
        """Upload a JSON file to S3 for the given content ID.
        
        Args:
            content_id (str): The folder content ID
            file_name (str): The name of the file to upload
            data (dict): The data to be uploaded as JSON
        
        Returns:
            bool: True if upload was successful
        """
        if content_id is None:
            raise BadParameterError("content_id is required.")
        
        if data is None:
            raise BadParameterError("data is required.")
        
        # Get upload URL
        content_service = ContentService()
        upload_url = content_service.get_upload_url(
            content_id=content_id,
            file_name=file_name,
            content_type="application/json"
        )
        
        # Upload the JSON data
        self.request(
            method="PUT",
            auth=False,  # presigned storage URL: no platform credentials
            url=upload_url,
            headers={'Content-Type': 'application/json'},
            json_data=data,
        )
        
        return True
    
    def upload_reports_json(
        self,
        content_id: str,
        chart_data: ChartDataResult,
    ) -> bool:
        """Upload reports.json to S3 for the given content ID.
        
        Args:
            content_id (str): The folder content ID where reports.json will be uploaded
            chart_data (ChartDataResult): Chart data result from ChartDataFactory
        
        Returns:
            bool: True if upload was successful
        """
        return self._upload_json_file(content_id, "reports.json", chart_data.reports_json)
    
    def upload_data_ids_json(
        self,
        content_id: str,
        chart_data: ChartDataResult,
    ) -> bool:
        """Upload data_ids.json to S3 for the given content ID.
        
        Args:
            content_id (str): The folder content ID where data_ids.json will be uploaded
            chart_data (ChartDataResult): Chart data result from ChartDataFactory
        
        Returns:
            bool: True if upload was successful
        
        Raises:
            BadParameterError: If chart_data has no data_ids_json
        """
        if chart_data.data_ids_json is None:
            raise BadParameterError("chart_data does not contain data_ids_json")
        
        return self._upload_json_file(content_id, "data_ids.json", chart_data.data_ids_json)

