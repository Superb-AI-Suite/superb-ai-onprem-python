from typing import Optional, Union

from spb_onprem.base_service import BaseService
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError

from spb_onprem.models.entities import Model

from .queries import Queries


class TrainingReportService(BaseService):
    def create_training_report(
        self,
        dataset_id: str,
        model_id: str,
        name: str,
        content_id: str,
        description: Optional[str] = None,
    ) -> Model:
        response = self.request_gql(
            Queries.CREATE,
            Queries.CREATE["variables"](
                dataset_id=dataset_id,
                model_id=model_id,
                name=name,
                content_id=content_id,
                description=description,
            ),
        )
        return Model.model_validate(response)

    def update_training_report(
        self,
        dataset_id: str,
        model_id: str,
        training_report_id: str,
        name: Union[Optional[str], UndefinedType] = Undefined,
        content_id: Union[Optional[str], UndefinedType] = Undefined,
        description: Union[Optional[str], UndefinedType] = Undefined,
    ) -> Model:
        response = self.request_gql(
            Queries.UPDATE,
            Queries.UPDATE["variables"](
                dataset_id=dataset_id,
                model_id=model_id,
                training_report_id=training_report_id,
                name=name,
                content_id=content_id,
                description=description,
            ),
        )
        return Model.model_validate(response)

    def delete_training_report(
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
            Queries.DELETE,
            Queries.DELETE["variables"](
                dataset_id=dataset_id,
                model_id=model_id,
                training_report_id=training_report_id,
            ),
        )
        return Model.model_validate(response)
