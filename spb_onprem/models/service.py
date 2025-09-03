from typing import Optional, Dict, Any, List, Tuple, Union

from spb_onprem.base_service import BaseService
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError
from .queries import Queries
from .entities import Model


class ModelService(BaseService):
    """Service class for handling model operations."""
    
    def get_models(
        self,
        dataset_id: str,
        filter: Union[UndefinedType, Dict[str, Any]] = Undefined,
        cursor: Union[UndefinedType, str] = Undefined,
        length: int = 50
    ) -> Tuple[List[Model], Optional[str], int]:
        """Get paginated list of models for a dataset.
        
        Args:
            dataset_id (str): The dataset ID.
            filter (Union[UndefinedType, Dict[str, Any]]): Filter for models.
            cursor (Union[UndefinedType, str]): Cursor for pagination.
            length (int): Number of items to retrieve per page.
        
        Returns:
            Tuple[List[Model], Optional[str], int]: A tuple containing models, next cursor, and total count.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")

        response = self.request_gql(
            Queries.GET_MODELS,
            Queries.GET_MODELS["variables"](
                dataset_id=dataset_id,
                filter=filter,
                cursor=cursor,
                length=length
            )
        )
        models_list = response.get("models", [])
        return (
            [Model.model_validate(model) for model in models_list],
            response.get("next"),
            response.get("totalCount", 0)
        )
    
    def delete_model(
        self,
        dataset_id: str,
        model_id: str
    ) -> bool:
        """Delete a model from the dataset.
        
        Args:
            dataset_id (str): The dataset ID.
            model_id (str): The model ID to delete.
        
        Returns:
            bool: True if deletion was successful.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if model_id is None:
            raise BadParameterError("model_id is required.")

        response = self.request_gql(
            Queries.DELETE_MODEL,
            Queries.DELETE_MODEL["variables"](
                dataset_id=dataset_id,
                model_id=model_id
            )
        )
        return response.get("deleteModel", False)