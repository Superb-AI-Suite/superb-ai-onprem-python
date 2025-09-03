from typing import Optional, Dict, Any, List, Tuple, Union

from spb_onprem.base_service import BaseService
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError
from .queries import Queries
from .entities import PredictionSet


class PredictionService(BaseService):
    """Service class for handling prediction set operations."""
    
    def get_prediction_sets(
        self,
        dataset_id: str,
        filter: Union[UndefinedType, Dict[str, Any]] = Undefined,
        cursor: Union[UndefinedType, str] = Undefined,
        length: int = 50
    ) -> Tuple[List[PredictionSet], Optional[str], int]:
        """Get paginated list of prediction sets for a dataset.
        
        Args:
            dataset_id (str): The dataset ID.
            filter (Union[UndefinedType, Dict[str, Any]]): Filter for prediction sets.
            cursor (Union[UndefinedType, str]): Cursor for pagination.
            length (int): Number of items to retrieve per page.
        
        Returns:
            Tuple[List[PredictionSet], Optional[str], int]: A tuple containing prediction sets, next cursor, and total count.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")

        response = self.request_gql(
            Queries.GET_PREDICTION_SETS,
            Queries.GET_PREDICTION_SETS["variables"](
                dataset_id=dataset_id,
                filter=filter,
                cursor=cursor,
                length=length
            )
        )
        prediction_sets_list = response.get("predictionSets", [])
        return (
            [PredictionSet.model_validate(ps) for ps in prediction_sets_list],
            response.get("next"),
            response.get("totalCount", 0)
        )
    
    def get_prediction_set(
        self,
        dataset_id: str,
        prediction_set_id: str
    ) -> PredictionSet:
        """Get detailed prediction set information including content IDs.
        
        Args:
            dataset_id (str): The dataset ID.
            prediction_set_id (str): The prediction set ID.
        
        Returns:
            PredictionSet: The prediction set entity.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if prediction_set_id is None:
            raise BadParameterError("prediction_set_id is required.")

        response = self.request_gql(
            Queries.GET_PREDICTION_SET,
            Queries.GET_PREDICTION_SET["variables"](
                dataset_id=dataset_id,
                prediction_set_id=prediction_set_id
            )
        )
        prediction_set_dict = response.get("predictionSet", {})
        return PredictionSet.model_validate(prediction_set_dict)
    
    def delete_prediction_set(
        self,
        dataset_id: str,
        prediction_set_id: str
    ) -> bool:
        """Delete a prediction set from the dataset.
        
        Args:
            dataset_id (str): The dataset ID.
            prediction_set_id (str): The prediction set ID to delete.
        
        Returns:
            bool: True if deletion was successful.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if prediction_set_id is None:
            raise BadParameterError("prediction_set_id is required.")

        response = self.request_gql(
            Queries.DELETE_PREDICTION_SET,
            Queries.DELETE_PREDICTION_SET["variables"](
                dataset_id=dataset_id,
                prediction_set_id=prediction_set_id
            )
        )
        return response.get("deletePredictionSet", False)
    
    def delete_prediction_from_data(
        self,
        dataset_id: str,
        data_id: str,
        prediction_set_id: str
    ) -> bool:
        """Delete predictions from a specific data item for a given prediction set.
        
        Args:
            dataset_id (str): The dataset ID.
            data_id (str): The data ID.
            prediction_set_id (str): The prediction set ID.
        
        Returns:
            bool: True if deletion was successful.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if data_id is None:
            raise BadParameterError("data_id is required.")
        if prediction_set_id is None:
            raise BadParameterError("prediction_set_id is required.")

        response = self.request_gql(
            Queries.DELETE_PREDICTION_FROM_DATA,
            Queries.DELETE_PREDICTION_FROM_DATA["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                prediction_set_id=prediction_set_id
            )
        )
        return response.get("deletePrediction") is not None