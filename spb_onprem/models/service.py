from typing import Optional, Union, List, Any
from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import BadParameterError
from spb_onprem.base_types import Undefined, UndefinedType
from .queries import Queries
from .entities import Model, ModelPageInfo, ModelTrainClass
from .params.models import ModelsFilter


class ModelService(BaseService):
    """
    Service class for handling model-related operations.
    """
    
    def get_models(
        self,
        dataset_id: str,
        models_filter: Optional[ModelsFilter] = None,
        cursor: Optional[str] = None,
        length: Optional[int] = 10
    ):
        """
        Get a list of models based on the provided filter and pagination parameters.
        
        Args:
            dataset_id (str): The dataset ID
            models_filter (Optional[ModelsFilter]): Filter criteria for models
            cursor (Optional[str]): Cursor for pagination
            length (Optional[int]): Number of items per page (default: 10)
        
        Returns:
            tuple: A tuple containing:
                - List[Model]: A list of Model objects
                - str: Next cursor for pagination
                - int: Total count of models
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        
        if length > 50:
            raise BadParameterError("The maximum length is 50.")
        
        response = self.request_gql(
            Queries.MODELS,
            Queries.MODELS["variables"](
                dataset_id=dataset_id,
                models_filter=models_filter,
                cursor=cursor,
                length=length
            )
        )
        
        page_info = ModelPageInfo.model_validate(response)
        return (
            page_info.models or [],
            page_info.next,
            page_info.total_count or 0
        )

    def get_model(
        self,
        dataset_id: str,
        model_id: str,
    ):
        """
        Retrieve a model by its ID.

        Args:
            dataset_id (str): The dataset ID
            model_id (str): The ID of the model to retrieve

        Returns:
            Model: The retrieved model object
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        
        if model_id is None:
            raise BadParameterError("model_id is required.")
        
        response = self.request_gql(
            Queries.MODEL,
            Queries.MODEL["variables"](
                dataset_id=dataset_id,
                model_id=model_id
            ),
        )
        return Model.model_validate(response)
    
    def create_model(
        self,
        dataset_id: str,
        name: str,
        baseline_model: str,
        training_slice_ids: List[str],
        validation_slice_ids: List[str],
        description: Union[str, UndefinedType] = Undefined,
        training_classes: Union[List[ModelTrainClass], UndefinedType] = Undefined,
        model_content_id: Union[str, UndefinedType] = Undefined,
        is_trained: Union[bool, UndefinedType] = Undefined,
        trained_at: Union[str, UndefinedType] = Undefined,
        is_pinned: Union[bool, UndefinedType] = Undefined,
        meta: Union[Any, UndefinedType] = Undefined,
    ):
        """
        Create a new model.

        Args:
            dataset_id (str): The dataset ID
            name (str): The model name
            baseline_model (str): The baseline model used
            training_slice_ids (List[str]): The IDs of the training slices
            validation_slice_ids (List[str]): The IDs of the validation slices
            description (Optional[str]): The description of the model
            training_classes (Optional[List[ModelTrainClass]]): The training classes
            model_content_id (Optional[str]): The model content ID
            is_trained (Optional[bool]): Whether the model is trained
            trained_at (Optional[str]): When the model was trained
            is_pinned (Optional[bool]): Whether the model is pinned
            meta (Optional[Any]): The metadata of the model

        Returns:
            Model: The created model object
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        
        if name is None:
            raise BadParameterError("name is required.")
        
        if baseline_model is None:
            raise BadParameterError("baseline_model is required.")
        
        if training_slice_ids is None:
            raise BadParameterError("training_slice_ids is required.")
        
        if validation_slice_ids is None:
            raise BadParameterError("validation_slice_ids is required.")
        
        response = self.request_gql(
            Queries.CREATE_MODEL,
            Queries.CREATE_MODEL["variables"](
                dataset_id=dataset_id,
                name=name,
                baseline_model=baseline_model,
                training_slice_ids=training_slice_ids,
                validation_slice_ids=validation_slice_ids,
                description=description,
                training_classes=training_classes,
                model_content_id=model_content_id,
                is_trained=is_trained,
                trained_at=trained_at,
                is_pinned=is_pinned,
                meta=meta,
            ),
        )
        return Model.model_validate(response)
    
    def update_model(
        self,
        dataset_id: str,
        model_id: str,
        name: Union[str, UndefinedType] = Undefined,
        description: Union[str, UndefinedType] = Undefined,
        training_classes: Union[List[ModelTrainClass], UndefinedType] = Undefined,
        model_content_id: Union[str, UndefinedType] = Undefined,
        is_trained: Union[bool, UndefinedType] = Undefined,
        trained_at: Union[str, UndefinedType] = Undefined,
        meta: Union[Any, UndefinedType] = Undefined,
    ):
        """
        Update a model.

        Args:
            dataset_id (str): The dataset ID
            model_id (str): The ID of the model to update
            name (Optional[str]): The new name
            description (Optional[str]): The new description
            training_classes (Optional[List[ModelTrainClass]]): The new training classes
            model_content_id (Optional[str]): The new model content ID
            is_trained (Optional[bool]): The new trained status
            trained_at (Optional[str]): The new trained timestamp
            meta (Optional[Any]): The new metadata

        Returns:
            Model: The updated model object
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        
        if model_id is None:
            raise BadParameterError("model_id is required.")
        
        response = self.request_gql(
            Queries.UPDATE_MODEL,
            Queries.UPDATE_MODEL["variables"](
                dataset_id=dataset_id,
                model_id=model_id,
                name=name,
                description=description,
                training_classes=training_classes,
                model_content_id=model_content_id,
                is_trained=is_trained,
                trained_at=trained_at,
                meta=meta,
            ),
        )
        return Model.model_validate(response)
    
    def pin_model(
        self,
        dataset_id: str,
        model_id: str,
    ):
        """
        Pin a model.

        Args:
            dataset_id (str): The dataset ID
            model_id (str): The ID of the model to pin

        Returns:
            Model: The pinned model object
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        
        if model_id is None:
            raise BadParameterError("model_id is required.")
        
        response = self.request_gql(
            Queries.PIN_MODEL,
            Queries.PIN_MODEL["variables"](
                dataset_id=dataset_id,
                model_id=model_id,
            ),
        )
        return Model.model_validate(response)
    
    def unpin_model(
        self,
        dataset_id: str,
        model_id: str,
    ):
        """
        Unpin a model.

        Args:
            dataset_id (str): The dataset ID
            model_id (str): The ID of the model to unpin

        Returns:
            Model: The unpinned model object
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        
        if model_id is None:
            raise BadParameterError("model_id is required.")
        
        response = self.request_gql(
            Queries.UNPIN_MODEL,
            Queries.UNPIN_MODEL["variables"](
                dataset_id=dataset_id,
                model_id=model_id,
            ),
        )
        return Model.model_validate(response)
    
    def delete_model(
        self,
        dataset_id: str,
        model_id: str,
    ) -> bool:
        """Delete a model.
        
        Args:
            dataset_id (str): The dataset ID
            model_id (str): The ID of the model to delete
        
        Returns:
            bool: True if deletion was successful
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        
        if model_id is None:
            raise BadParameterError("model_id is required.")

        response = self.request_gql(
            Queries.DELETE_MODEL,
            Queries.DELETE_MODEL["variables"](
                dataset_id=dataset_id,
                model_id=model_id,
            )
        )
        return response
