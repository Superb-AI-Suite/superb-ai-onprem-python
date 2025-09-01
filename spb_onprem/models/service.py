from typing import Optional, Dict, Any

from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import BadParameterError
from .queries import Queries
from .entities import Model


class ModelService(BaseService):
    """Service class for handling model operations."""
    
    def get_models(
        self,
        dataset_id: str,
        filter: Optional[Dict[str, Any]] = None,
        cursor: Optional[str] = None,
        length: int = 50
    ) -> Dict[str, Any]:
        """Get paginated list of models for a dataset.
        
        Args:
            dataset_id (str): The dataset ID.
            filter (Optional[Dict[str, Any]]): Filter for models.
            cursor (Optional[str]): Cursor for pagination.
            length (int): Number of items to retrieve per page.
        
        Returns:
            Dict[str, Any]: Response containing models, next cursor, and totalCount.
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
        return response.get("models", {})
    
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