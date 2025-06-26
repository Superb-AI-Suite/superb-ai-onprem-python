import mimetypes
import requests
import json

from io import BytesIO
from typing import Optional, Tuple, Union

from spb_onprem.base_service import BaseService
from spb_onprem.base_types import (
    Undefined,
    UndefinedType,
)
from .entities import BaseContent, Content
from .queries import Queries



class ContentService(BaseService):
    """The content service for the SDK.
    Content service is the service that handles the content operations.
    """

    def create_content(
        self,
        key: Union[
            str,
            UndefinedType
        ] = Undefined,
        content_type: Union[
            str,
            UndefinedType
        ] = Undefined,
    ) -> Tuple[Content, str]:
        '''
        Creates a new content.
        Args:
            key (Optional[str]):
                An optional key to associate with the uploaded content.
            content_type (Optional[str]):
                An optional content type to associate with the uploaded content.
        Returns:
            str: The upload URL for the content.
        '''
        response = self.request_gql(
            query=Queries.CREATE,
            variables=Queries.CREATE["variables"](key, content_type)
        )
        content = Content.model_validate(response['content'])
        return content, response['uploadURL']

    def upload_content(
        self,
        file_path: str,
        key: Union[
            str,
            UndefinedType    
        ] = Undefined,
    ):
        '''
        Uploads the content to the server.
        Args:
            file_path (str):
                The path of the file to be uploaded.
                You must provide the full path of the file (with extensions).
        '''
        with open(file_path, 'rb') as f:
            file = f.read()
        response = self.request_gql(
            query=Queries.CREATE,
            variables=Queries.CREATE["variables"](key, mimetypes.guess_type(file_path)[0])
        )
        upload_url = response['uploadURL']
        
        self.request(
            method="PUT",
            url=upload_url,
            headers={
                'Content-Type': mimetypes.guess_type(file_path)[0]
            },
            data=file,
        )
        content = response['content']
        return BaseContent.model_validate(content)
    
    def upload_json_content(
        self,
        data: dict,
        key: Union[
            str,
            UndefinedType    
        ] = Undefined,
    ):
        '''
        Uploads the JSON content to the server.

        Args:
            data (dict):
                The JSON data to be uploaded.
            key (Optional[str]):
                An optional key to associate with the uploaded content.
        '''
        response = self.request_gql(
            query=Queries.CREATE,
            variables=Queries.CREATE["variables"](key, "application/json") if key else None
        )
        upload_url = response['uploadURL']
        self.request(
            method="PUT",
            url=upload_url,
            headers={
                'Content-Type': 'application/json'
            },
            json_data=data,
        )
        content = response['content']
        return BaseContent.model_validate(content)

    def upload_content_with_data(
        self,
        file_data: BytesIO,
        content_type: str,
        key: Union[
            str,
            UndefinedType    
        ] = Undefined,
    ):
        '''
        Uploads the content to the server.

        Args:
            file_data (BytesIO):
                The file data to be uploaded.
            content_type (str):
                The MIME type of the file being uploaded (e.g., "image/jpeg").
            key (Optional[str]):
                An optional key to associate with the uploaded content.
        '''
        # Reset the BytesIO pointer to the beginning
        file_data.seek(0)

        # Request to get the upload URL
        response = self.request_gql(
            query=Queries.CREATE,
            variables=Queries.CREATE["variables"](key, content_type)
        )
        upload_url = response['uploadURL']

        # Upload the file data using the PUT request
        self.request(
            method="PUT",
            url=upload_url,
            headers={
                'Content-Type': content_type
            },
            data=file_data.read(),
        )

        # Retrieve the uploaded content details
        content = response['content']
        return BaseContent.model_validate(content)

    def get_download_url(
        self,
        content_id: str,
    ) -> str:
        '''
        Gets the content from the server.
        Args:
            content_id (str): The ID of the content to get.
        Returns:
            Content: The content object.
        '''
        
        response = self.request_gql(
            query=Queries.GET_DOWNLOAD_URL,
            variables=Queries.GET_DOWNLOAD_URL["variables"](content_id)
        )
        return response
