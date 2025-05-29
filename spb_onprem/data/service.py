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
from .utils import Utils
from .entities import (
    Data,
    Scene,
    AnnotationVersion,
    Annotation,
    DataMeta,
    Prediction,
)
from .enums import (
    DataType,
    SceneType,
    DataMetaValue,
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
        filter: Optional[DataListFilter] = None,
        cursor: Optional[str] = None,
        length: Optional[int] = 10,
    ):
        """Get a list of data.

        Args:
            dataset_id (str): The dataset id.
            filter (Optional[DataListFilter], optional): The filter for the data list. Defaults to None.
            cursor (Optional[str], optional): The cursor for the data list. Defaults to None.
            length (Optional[int], optional): The length of the data list. Defaults to 10.

        Raises:
            BadParameterError: The maximum length is 50.

        Returns:
            Tuple[List[Data], Optional[str], int]: The data list, the next cursor, and the total count.
        """
        if length > 50:
            raise BadParameterError("The maximum length is 50.")
        
        response = self.request_gql(
            Queries.GET_LIST,
            Queries.GET_LIST["variables"](
                dataset_id=dataset_id,
                data_list_filter=filter,
                cursor=cursor,
                length=length
            )
        )
        data_list = [Data.model_validate(data) for data in response.get("data", [])]
        return (
            data_list,
            response.get("next", None),
            response.get("totalCount", False)
        )

    def get_data_id_list(
        self,
        dataset_id: str,
        filter: Optional[DataListFilter] = None,
        cursor: Optional[str] = None,
        length: Optional[int] = 50,
    ):
        """Get a list of data.

        Args:
            dataset_id (str): The dataset id.
            filter (Optional[DataListFilter], optional): The filter for the data list. Defaults to None.
            cursor (Optional[str], optional): The cursor for the data list. Defaults to None.
            length (Optional[int], optional): The length of the data list. Defaults to 50.

        Raises:
            BadParameterError: The maximum length is 500.

        Returns:
            Tuple[List[Data], Optional[str], int]: The data list, the next cursor, and the total count.
        """
    
        if length > 50:
            raise ValueError("The maximum length is 500.")
        
        response = self.request_gql(
            Queries.GET_ID_LIST,
            Queries.GET_ID_LIST["variables"](
                dataset_id=dataset_id,
                data_list_filter=filter,
                cursor=cursor,
                length=length,
            )
        )
        data_ids = response.get("data", [])
        data_list = [Data.model_validate(data_id) for data_id in data_ids]
        return (
            data_list,
            response.get("next", None),
            response.get("totalCount", False)
        )

    def update_data(
        self,
        dataset_id: str,
        data_id: str,
        key: Union[
            Optional[str],
            UndefinedType
        ] = Undefined,
        meta: Union[
            Optional[List[DataMeta]],
            UndefinedType,
        ] = Undefined,
        system_meta: Union[
            Optional[List[DataMeta]],
            UndefinedType,
        ] = Undefined,
    ):
        """Update a data.

        Args:
            dataset_id (str): The dataset id.
            data_id (str): The data id.
            key (Union[Optional[str], UndefinedType], optional): The key of the data. Defaults to Undefined.
            meta (Union[Optional[List[DataMeta]], UndefinedType], optional): The meta of the data. Defaults to Undefined.
            system_meta (Union[Optional[List[DataMeta]], UndefinedType], optional): The system meta of the data. Defaults to Undefined.

        Returns:
            Data: The updated data.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if data_id is None:
            raise BadParameterError("data_id is required.")

        response = self.request_gql(
            query=Queries.UPDATE,
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

    def remove_data_feom_slice(
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
            Boolean: True if the data is deleted, False otherwise.
        """
        response = self.request_gql(
            Queries.DELETE,
            Queries.DELETE["variables"](
                dataset_id=dataset_id,
                data_id=data_id
            )
        )
        return response
    
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
                prediction=prediction
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
            set_id (str): The prediction Set id to delete.
        
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

    def upload_image_data_from_path(
        self,
        dataset_id: str,
        key: str,
        slice_ids: Optional[List[str]] = None,
        image_path: Optional[BytesIO] = None,
        annotation: Optional[dict] = None,
        meta: Optional[dict[str, DataMetaValue]] = None,
    ):
        """Upload an image data from a path.

        Args:
            dataset_id (str): The dataset id.
            key (str): The key of the data.
            slice_ids (Optional[List[str]], optional): The slice ids of the data. Defaults to None.
            image_path (Optional[BytesIO], optional): The image path of the data. Defaults to None.
            annotation (Optional[dict], optional): The annotation of the data. Defaults to None.
            meta (Optional[dict], optional): The meta of the data. Defaults to None.

        Returns:
            Data: The uploaded data.
        """
        with open(image_path, 'rb') as f:
            image_content = f.read()
        image = BytesIO(image_content)

        return self.upload_image_data(
            dataset_id=dataset_id,
            key=key,
            slice_ids=slice_ids,
            image=image,
            annotation=annotation,
            meta=meta,
        )

    def upload_image_data(
        self,
        dataset_id: str,
        key: str,
        slice_ids: Optional[List[str]] = None,
        image: Optional[BytesIO] = None,
        annotation: Optional[dict] = None,
        meta: Optional[dict[str, DataMetaValue]] = None,
    ):
        """
        Upload image data to a dataset.

        Args:
            dataset_id (str): The ID of the dataset to upload the image data to.
            key (str): The key for the image data.
            slice_ids (Optional[List[str]]): List of slice IDs associated with the image data.
            image (Optional[BytesIO]): The image data to upload.
            annotation (Optional[dict]): Annotations associated with the image data.
            meta (Optional[dict]): Metadata of the data. { "key1": val1, "key2": val2, ... }

        Returns:
            None
        """
        content_service = ContentService()
        data = Data(
            dataset_id=dataset_id,
            key=key,
            type=DataType.SUPERB_IMAGE,
        )
        data.slice_ids = slice_ids
        
        if image is not None:
            # Build Image Content
            image_content = content_service.upload_content_with_data(
                image,
                content_type="image/jpeg",
                key=f"{key}_image",
            )
            thumbnail = Utils.create_thumbnail(
                image=image,
            )
            thumbnail_content = content_service.upload_content_with_data(
                thumbnail,
                content_type="image/jpeg",
                key=f"{key}_thumbnail",
            )
            scene = Scene(
                type=SceneType.IMAGE,
                content=image_content,
                meta=None,
            )
            data.scene = [scene]
            data.thumbnail = thumbnail_content
        if annotation is not None:
            # Build Image Annotation
            annotation_content = content_service.upload_json_content(
                annotation,
                key=f"{key}_annotation",
            )
            annotation_version = AnnotationVersion(
                content=annotation_content,
                meta=None
            )
            annotation=Annotation(
                versions=[annotation_version],
                meta=None
            )
            data.annotation = annotation
        if meta is not None:
            data.meta = DataMeta.from_dict(meta)

        response = self.request_gql(
            Queries.CREATE,
            Queries.CREATE["variables"](data)
        )
        data = Data.model_validate(response)
        return data
