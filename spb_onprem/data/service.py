"""
base_service.py

This module defines the BaseService class, which serves as an abstract base class for services that handle data operations.

Classes:
    BaseService: An abstract base class that requires the implementation of the create_data method.
"""
from io import BytesIO
from typing import (
    Optional, List, Union,
)

from spb_onprem.contents.service import (
    ContentService
)
from spb_onprem.base_service import BaseService
from spb_onprem.base_types import (
    Undefined,
    UndefinedType,
)
from .queries import Queries
from .entities import (
    Data,
    Scene,
    AnnotationVersion,
    Annotation,
    DataMeta,
    Prediction,
    Frame,
)
from .enums import (
    DataType,
    SceneType,
    DataMetaValue,
    DataStatus,
)
from .params import (
    DataListFilter,
)
from spb_onprem.exceptions import BadParameterError

class DataService(BaseService):
    """
    Service class for handling data-related operations.
    """
    
    def get_data(
        self,
        dataset_id: str,
        data_id: str,
    ):
        """Get a data by id or key.

        Args:
            dataset_id (str): The dataset id.
            data_id (Union[ str, UndefinedType ], optional): The id of the data. Defaults to Undefined.

        Raises:
            BadParameterError: Either data_id or key must be provided.

        Returns:
            Data: The data.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if data_id is None:
            raise BadParameterError("data_id is required.")

        response = self.request_gql(
            Queries.GET,
            Queries.GET["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
            )
        )

        return Data.model_validate(response)

    def get_data_by_key(
        self,
        dataset_id: str,
        data_key: str,
    ):
        """Get a data by key.

        Args:
            dataset_id (str): The dataset id.
            data_key (str): The key of the data.

        Returns:
            Data: The data.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if data_key is None:
            raise BadParameterError("data_key is required.")
        response = self.request_gql(
            Queries.GET,
            Queries.GET["variables"](dataset_id=dataset_id, data_key=data_key)
        )
        return Data.model_validate(response)

    def get_data_list(
        self,
        dataset_id: str,
        data_filter: Optional[DataListFilter] = None,
        cursor: Optional[str] = None,
        length: int = 10
    ):
        """Get data list of a dataset.

        Args:
            dataset_id (str): The dataset id.
            data_filter (Optional[DataListFilter]): The filter to apply to the data.
            cursor (Optional[str]): The cursor to use for pagination.
            length (int): The length of the data to retrieve.

        Returns:
            tuple: A tuple containing the data, the next cursor, and the total count of data.
        """
        if length > 50:
            raise ValueError("Length must be less than or equal to 50.")

        response = self.request_gql(
            Queries.GET_LIST,
            Queries.GET_LIST["variables"](
                dataset_id=dataset_id,
                data_filter=data_filter,
                cursor=cursor,
                length=length
            )
        )
        data_list = response.get("data", [])
        data = [Data.model_validate(data_dict) for data_dict in data_list]
        return (
            data,
            response.get("next", None),
            response.get("totalCount", 0)
        )

    def get_data_id_list(
        self,
        dataset_id: str,
        data_filter: Optional[DataListFilter] = None,
        cursor: Optional[str] = None,
        length: int = 10
    ):
        """Get data id list of a dataset.

        Args:
            dataset_id (str): The dataset id.
            data_filter (Optional[DataListFilter]): The filter to apply to the data.
            cursor (Optional[str]): The cursor to use for pagination.
            length (int): The length of the data to retrieve.

        Returns:
            tuple: A tuple containing the data, the next cursor, and the total count of data.
        """
        if length > 50:
            raise ValueError("Length must be less than or equal to 50.")

        response = self.request_gql(
            Queries.GET_ID_LIST,
            Queries.GET_ID_LIST["variables"](
                dataset_id=dataset_id,
                data_filter=data_filter,
                cursor=cursor,
                length=length
            )
        )
        data_list = response.get("data", [])
        data = [Data.model_validate(data_dict) for data_dict in data_list]
        return (
            data,
            response.get("next", None),
            response.get("totalCount", 0)
        )

    def create_image_data(
        self,
        dataset_id: str,
        key: str,
        image_content: Union[
            BytesIO,
            str,
        ],
        slices: Optional[List[str]] = None,
        annotation: Optional[dict] = None,
        predictions: Optional[List[dict]] = None,
        meta: Optional[List[dict]] = None,
        system_meta: Optional[List[dict]] = None,
    ):
        """Create an image data.

        Args:
            dataset_id (str): The dataset id.
            key (str): The key of the data.
            image_content (Union[BytesIO, str]): The image content. If str, it is considered as a file path.
            slices (Optional[List[str]]): The slices to add the data to.
            annotation (Optional[dict]): The annotation data.
            predictions (Optional[List[dict]]): The predictions data.
            meta (Optional[List[dict]]): The meta data.
            system_meta (Optional[List[dict]]): The system meta data.

        Returns:
            Data: The created data.
        """
        content_service = ContentService()
        if isinstance(image_content, str):
            with open(image_content, "rb") as f:
                content = content_service.upload_content(
                    f.read(),
                    key,
                    f.name.split(".")[-1]
                )
        else:
            content = content_service.upload_content(
                image_content.read(),
                key,
                "jpg"
            )

        response = self.request_gql(
            Queries.CREATE,
            Queries.CREATE["variables"](
                dataset_id=dataset_id,
                key=key,
                type=DataType.SUPERB_IMAGE,
                slices=slices,
                scene=[{
                    "id": f"{key}_scene_0",
                    "type": SceneType.IMAGE,
                    "content": content.model_dump(by_alias=True),
                    "meta": {}
                }],
                thumbnail=content.model_dump(by_alias=True),
                annotation=annotation,
                predictions=predictions,
                meta=meta,
                system_meta=system_meta,
            )
        )
        data = Data.model_validate(response)
        return data

    def update_data(
        self,
        dataset_id: str,
        data_id: str,
        key: Union[
            str,
            UndefinedType,
        ] = Undefined,
        meta: Union[
            List[dict],
            UndefinedType,
        ] = Undefined,
        system_meta: Union[
            List[dict],
            UndefinedType,
        ] = Undefined,
    ):
        """Update a data.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            key (Union[str, UndefinedType], optional): The key of the data. Defaults to Undefined.
            meta (Union[List[dict], UndefinedType], optional): The meta data. Defaults to Undefined.
            system_meta (Union[List[dict], UndefinedType], optional): The system meta data. Defaults to Undefined.

        Returns:
            Data: The updated data.
        """
        response = self.request_gql(
            Queries.UPDATE,
            variables=Queries.UPDATE["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                key=key,
                meta=meta,
                system_meta=system_meta,
            )
        )
        data = Data.model_validate(response)
        return data

    def remove_data_from_slice(
        self,
        dataset_id: str,
        data_id: str,
        slice_id: str,
    ):
        """Remove a data from a slice.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            slice_id (str): The slice id.

        Returns:
            Data: The updated data.
        """
        response = self.request_gql(
            Queries.REMOVE_FROM_SLICE,
            Queries.REMOVE_FROM_SLICE["variables"](dataset_id=dataset_id, data_id=data_id, slice_id=slice_id)
        )
        data = Data.model_validate(response)
        return data
    
    def add_data_to_slice(
        self,
        dataset_id: str,
        data_id: str,
        slice_id: str,
    ):
        """Add a data to a slice.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            slice_id (str): The slice id.

        Returns:
            Data: The updated data.
        """
        response = self.request_gql(
            Queries.ADD_TO_SLICE,
            Queries.ADD_TO_SLICE["variables"](dataset_id=dataset_id, data_id=data_id, slice_id=slice_id)
        )
        data = Data.model_validate(response)
        return data
    
    def delete_data(
        self,
        dataset_id: str,
        data_id: str,
    ):
        """Delete a data.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.

        Returns:
            Data: The deleted data.
        """
        response = self.request_gql(
            Queries.DELETE,
            Queries.DELETE["variables"](dataset_id=dataset_id, data_id=data_id)
        )
        data = Data.model_validate(response)
        return data

    def insert_prediction(
        self,
        dataset_id: str,
        data_id: str,
        prediction: Prediction,
    ):
        """Insert a prediction.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            prediction (Prediction): The prediction.

        Returns:
            Data: The updated data.
        """
        response = self.request_gql(
            Queries.INSERT_PREDICTION,
            Queries.INSERT_PREDICTION["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                prediction=prediction,
            )
        )
        data = Data.model_validate(response)
        return data
    
    def delete_prediction(
        self,
        dataset_id: str,
        data_id: str,
        set_id: str,
    ):
        """Delete a prediction.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            set_id (str): The set id.

        Returns:
            Data: The updated data.
        """
        response = self.request_gql(
            Queries.DELETE_PREDICTION,
            Queries.DELETE_PREDICTION["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                set_id=set_id,
            )
        )
        data = Data.model_validate(response)
        return data
    
    def update_annotation(
        self,
        dataset_id: str,
        data_id: str,
        meta: Union[
            dict,
            UndefinedType
        ] = Undefined,
    ):
        """Update an annotation.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            meta (dict): The meta of the annotation.

        Returns:
            Data: The updated data.
        """
        response = self.request_gql(
            Queries.UPDATE_ANNOTATION,
            Queries.UPDATE_ANNOTATION["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                meta=meta,
            )
        )
        data = Data.model_validate(response)
        return data

    def insert_annotation_version(
        self,
        dataset_id: str,
        data_id: str,
        version: AnnotationVersion,
    ):
        """Insert an annotation version.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            version (AnnotationVersion): The annotation version.

        Returns:
            Data: The updated data.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if data_id is None:
            raise BadParameterError("data_id is required.")
        if version is None:
            raise BadParameterError("version is required.")
        
        response = self.request_gql(
            Queries.INSERT_ANNOTATION_VERSION,
            Queries.INSERT_ANNOTATION_VERSION["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                version=version,
            )
        )
        data = Data.model_validate(response)
        return data
    
    def delete_annotation_version(
        self,
        dataset_id: str,
        data_id: str,
        version_id: str,
    ):
        """Delete an annotation version.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            version_id (str): The version id.

        Returns:
            Data: The updated data.
        """
        response = self.request_gql(
            Queries.DELETE_ANNOTATION_VERSION,
            Queries.DELETE_ANNOTATION_VERSION["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                version_id=version_id,
            )
        )
        data = Data.model_validate(response)
        return data

    def update_slice_annotation(
        self,
        dataset_id: str,
        data_id: str,
        slice_id: str,
        meta: dict,
    ):
        """Update a slice annotation.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            slice_id (str): The slice id.
            meta (dict): The meta of the slice annotation.

        Returns:
            Data: The updated data.
        """
        response = self.request_gql(
            Queries.UPDATE_SLICE_ANNOTATION,
            Queries.UPDATE_SLICE_ANNOTATION["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                slice_id=slice_id,
                meta=meta,
            )
        )
        data = Data.model_validate(response)
        return data

    def insert_slice_annotation_version(
        self,
        dataset_id: str,
        data_id: str,
        slice_id: str,
        version: AnnotationVersion,
    ):
        """Insert a slice annotation version.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            slice_id (str): The slice id.
            version (AnnotationVersion): The annotation version.

        Returns:
            Data: The updated data.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if data_id is None:
            raise BadParameterError("data_id is required.")
        if slice_id is None:
            raise BadParameterError("slice_id is required.")
        if version is None:
            raise BadParameterError("version is required.")
        
        response = self.request_gql(
            Queries.INSERT_SLICE_ANNOTATION_VERSION,
            Queries.INSERT_SLICE_ANNOTATION_VERSION["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                slice_id=slice_id,
                version=version,
            )
        )
        data = Data.model_validate(response)
        return data

    def update_slice_annotation_version(
        self,
        dataset_id: str,
        data_id: str,
        slice_id: str,
        id: str,
        channels: Union[List[str], UndefinedType, None] = Undefined,
        version: Union[str, UndefinedType, None] = Undefined,
        meta: Union[dict, UndefinedType, None] = Undefined,
    ):
        """Update a slice annotation version.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            slice_id (str): The slice id.
            id (str): The annotation version id.
            channels (Union[List[str], UndefinedType, None], optional): The channels. Defaults to Undefined.
            version (Union[str, UndefinedType, None], optional): The version. Defaults to Undefined.
            meta (Union[dict, UndefinedType, None], optional): The meta. Defaults to Undefined.

        Returns:
            Data: The updated data.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if data_id is None:
            raise BadParameterError("data_id is required.")
        if slice_id is None:
            raise BadParameterError("slice_id is required.")
        if id is None:
            raise BadParameterError("id is required.")
        
        response = self.request_gql(
            Queries.UPDATE_SLICE_ANNOTATION_VERSION,
            Queries.UPDATE_SLICE_ANNOTATION_VERSION["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                slice_id=slice_id,
                id=id,
                channels=channels,
                version=version,
                meta=meta,
            )
        )
        data = Data.model_validate(response)
        return data

    def delete_slice_annotation_version(
        self,
        dataset_id: str,
        data_id: str,
        slice_id: str,
        id: str,
    ):
        """Delete a slice annotation version.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            slice_id (str): The slice id.
            id (str): The annotation version id.

        Returns:
            Data: The updated data.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if data_id is None:
            raise BadParameterError("data_id is required.")
        if slice_id is None:
            raise BadParameterError("slice_id is required.")
        if id is None:
            raise BadParameterError("id is required.")
        
        response = self.request_gql(
            Queries.DELETE_SLICE_ANNOTATION_VERSION,
            Queries.DELETE_SLICE_ANNOTATION_VERSION["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                slice_id=slice_id,
                id=id,
            )
        )
        data = Data.model_validate(response)
        return data

    def change_data_status(
        self,
        dataset_id: str,
        data_id: str,
        slice_id: str,
        status: DataStatus,
    ):
        """Change the status of a data slice.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            slice_id (str): The slice id.
            status (DataStatus): The new status.

        Returns:
            Data: The updated data.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if data_id is None:
            raise BadParameterError("data_id is required.")
        if slice_id is None:
            raise BadParameterError("slice_id is required.")
        if status is None:
            raise BadParameterError("status is required.")
        
        response = self.request_gql(
            Queries.CHANGE_DATA_STATUS,
            Queries.CHANGE_DATA_STATUS["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                slice_id=slice_id,
                status=status,
            )
        )
        data = Data.model_validate(response)
        return data

    def change_data_labeler(
        self,
        dataset_id: str,
        data_id: str,
        slice_id: str,
        labeler: Optional[str],
    ):
        """Change the labeler of a data slice.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            slice_id (str): The slice id.
            labeler (Optional[str]): The labeler id. None to unassign.

        Returns:
            Data: The updated data.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if data_id is None:
            raise BadParameterError("data_id is required.")
        if slice_id is None:
            raise BadParameterError("slice_id is required.")
        
        response = self.request_gql(
            Queries.CHANGE_DATA_LABELER,
            Queries.CHANGE_DATA_LABELER["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                slice_id=slice_id,
                labeler=labeler,
            )
        )
        data = Data.model_validate(response)
        return data

    def change_data_reviewer(
        self,
        dataset_id: str,
        data_id: str,
        slice_id: str,
        reviewer: Optional[str],
    ):
        """Change the reviewer of a data slice.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            slice_id (str): The slice id.
            reviewer (Optional[str]): The reviewer id. None to unassign.

        Returns:
            Data: The updated data.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if data_id is None:
            raise BadParameterError("data_id is required.")
        if slice_id is None:
            raise BadParameterError("slice_id is required.")
        
        response = self.request_gql(
            Queries.CHANGE_DATA_REVIEWER,
            Queries.CHANGE_DATA_REVIEWER["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                slice_id=slice_id,
                reviewer=reviewer,
            )
        )
        data = Data.model_validate(response)
        return data

    def update_data_slice(
        self,
        dataset_id: str,
        data_id: str,
        slice_id: str,
        meta: dict,
    ):
        """Update the metadata of a data slice.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            slice_id (str): The slice id.
            meta (dict): The meta of the data slice.

        Returns:
            Data: The updated data.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if data_id is None:
            raise BadParameterError("data_id is required.")
        if slice_id is None:
            raise BadParameterError("slice_id is required.")
        if meta is None:
            raise BadParameterError("meta is required.")
        
        response = self.request_gql(
            Queries.UPDATE_DATA_SLICE,
            Queries.UPDATE_DATA_SLICE["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                slice_id=slice_id,
                meta=meta,
            )
        )
        data = Data.model_validate(response)
        return data

    def update_frames(
        self,
        dataset_id: str,
        data_id: str,
        frames: Union[List[Frame], UndefinedType, None] = Undefined,  
    ):
        """Update frames of selected data.
        Args:
            dataset_id (str): dataset id which the data belongs to
            data_id (str): data id to be updated
            frames (list[Frame]): list of frames to be updated  
            
        Returns:
            Data: The updated data.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if data_id is None:
            raise BadParameterError("data_id is required.")

        response = self.request_gql(
            Queries.UPDATE_FRAMES,
            Queries.UPDATE_FRAMES["variables"](
                dataset_id=dataset_id,
                data_id=data_id,
                frames=frames,
            )
        )
        data = Data.model_validate(response)
        return data
