import mimetypes
import requests
import json

from io import BytesIO
from typing import Optional, Tuple, Union

from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import BadParameterError, BadRequestError
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
            auth=False,  # presigned storage URL: no platform credentials
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
            auth=False,  # presigned storage URL: no platform credentials
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
            auth=False,  # presigned storage URL: no platform credentials
            url=upload_url,
            headers={
                'Content-Type': content_type
            },
            data=file_data.read(),
        )

        # Retrieve the uploaded content details
        content = response['content']
        return BaseContent.model_validate(content)
    
    def get_update_url(self, content_id: str, content_type: Optional[str] = None) -> str:
        '''
        Gets a presigned URL to overwrite an existing content (generateContentUpdateURL).

        The platform does not check that the content exists: a PUT to a
        mistyped ID creates a new object. ``content_exists`` checks first.

        The web editor saves an annotation this way: the content keeps its ID,
        so nothing points at a new content and no old content is left behind.

        Args:
            content_id (str): The ID of the content to overwrite.
            content_type (Optional[str]): The MIME type the PUT will send. It is
                part of the signature, so send the same Content-Type.

        Returns:
            str: The presigned PUT URL. Its query is a credential: do not log it.
        '''
        return self.request_gql(
            query=Queries.GET_UPDATE_URL,
            variables=Queries.GET_UPDATE_URL["variables"](content_id, content_type),
        )

    def content_exists(self, content_id: str) -> bool:
        '''
        Whether a (single-file) content exists in storage.

        Sends a HEAD request to a presigned URL (generateContentHeadURL), without
        platform credentials.

        Raises:
            BadParameterError: If content_id is missing or blank (nothing is sent).

        Returns:
            bool: True when the object exists, False when storage answers 404.
        '''
        if content_id is None or not isinstance(content_id, str) or not content_id.strip():
            raise BadParameterError("content_id is required.")
        head_url = self.request_gql(
            query=Queries.GET_HEAD_URL,
            variables=Queries.GET_HEAD_URL["variables"](content_id),
        )
        try:
            self.request(method="HEAD", url=head_url, headers={}, auth=False)
        except BadRequestError as error:
            if "404 Client Error" in str(error):
                return False
            raise
        return True

    def _check_exists(self, content_id: str) -> None:
        if not self.content_exists(content_id):
            raise BadParameterError(
                f"content {content_id} does not exist. Overwriting it would create a new object "
                "under that ID; pass check_exists=False if that is what you want."
            )

    def update_content_with_data(
        self,
        content_id: str,
        file_data: Union[BytesIO, bytes],
        content_type: str,
        check_exists: bool = True,
    ) -> str:
        '''
        Overwrites an existing content with new data, keeping its ID.

        The platform does not check that the content exists: a mistyped ID
        would create a new object under it. So by default the SDK checks first
        (``content_exists``, one extra request) and refuses a missing content.

        Args:
            content_id (str): The ID of the content to overwrite.
            file_data (BytesIO | bytes): The new data.
            content_type (str): The MIME type of the data (e.g. "application/json").
            check_exists (bool): Check that the content exists first. Defaults to True.

        Raises:
            BadParameterError: If content_id or content_type is missing, or the
                content does not exist (with ``check_exists``).

        Returns:
            str: The content ID (unchanged).
        '''
        if not content_type:
            raise BadParameterError("content_type is required.")
        if isinstance(file_data, BytesIO):
            file_data.seek(0)
            body = file_data.read()
        elif isinstance(file_data, (bytes, bytearray)):
            body = bytes(file_data)
        else:
            raise BadParameterError("file_data must be BytesIO or bytes.")
        if check_exists:
            self._check_exists(content_id)
        update_url = self.get_update_url(content_id, content_type)
        self.request(
            method="PUT",
            auth=False,  # presigned storage URL: no platform credentials
            url=update_url,
            headers={'Content-Type': content_type},
            data=body,
        )
        return content_id

    def update_content(self, content_id: str, file_path: str, check_exists: bool = True) -> str:
        '''
        Overwrites an existing content with a file, keeping its ID.

        The platform does not check that the content exists (a mistyped ID
        creates a new object); with ``check_exists`` (default) the SDK does.

        Args:
            content_id (str): The ID of the content to overwrite.
            file_path (str): The file to upload (its type is guessed from the name).
            check_exists (bool): Check that the content exists first. Defaults to True.

        Returns:
            str: The content ID (unchanged).
        '''
        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        with open(file_path, 'rb') as f:
            return self.update_content_with_data(content_id, f.read(), content_type, check_exists)

    def update_json_content(self, content_id: str, data: Union[dict, list], check_exists: bool = True) -> str:
        '''
        Overwrites an existing content with JSON (e.g. an annotation), keeping its ID.

        The platform does not check that the content exists (a mistyped ID
        creates a new object); with ``check_exists`` (default) the SDK does.

        Args:
            content_id (str): The ID of the content to overwrite.
            data (dict | list): The JSON data.
            check_exists (bool): Check that the content exists first. Defaults to True.

        Returns:
            str: The content ID (unchanged).
        '''
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        return self.update_content_with_data(content_id, body, "application/json", check_exists)

    def create_folder_content(self) -> str:
        '''
        Creates a folder content ID for S3 upload.
        
        Returns:
            str: The folder content ID.
        '''
        response = self.request_gql(
            query=Queries.CREATE_FOLDER_CONTENT,
            variables=Queries.CREATE_FOLDER_CONTENT["variables"]()
        )
        return response['id']
    
    def get_upload_url(
        self,
        content_id: str,
        file_name: str,
        content_type: Optional[str] = None,
    ) -> str:
        '''
        Gets the upload URL for the content.
        Args:
            content_id (str): The ID of the content to get the upload URL for.
            file_name (str): The name of the file to be uploaded.
            content_type (Optional[str]): The MIME type of the file being uploaded.
        '''
        response = self.request_gql(
            query=Queries.GET_UPLOAD_URL,
            variables=Queries.GET_UPLOAD_URL["variables"](content_id, file_name, content_type)
        )
        return response

    def get_download_url(
        self,
        content_id: str,
        file_name: Optional[str] = None,
    ) -> str:
        '''
        Gets the download URL for the content.
        Args:
            content_id (str): The ID of the content to get.
            file_name (Optional[str]): The name of the file to download. If provided, uses generateFileDownloadURL mutation.
        Returns:
            str: The download URL.
        '''
        if file_name is not None:
            response = self.request_gql(
                query=Queries.GET_FILE_DOWNLOAD_URL,
                variables=Queries.GET_FILE_DOWNLOAD_URL["variables"](content_id, file_name)
            )
        else:
            response = self.request_gql(
                query=Queries.GET_DOWNLOAD_URL,
                variables=Queries.GET_DOWNLOAD_URL["variables"](content_id)
            )
        return response

    def delete_content(
        self,
        content_id: str,
    ) -> bool:
        '''
        Delete a content by ID.

        A content is a file in storage, not a platform entity, so this deletes
        it at once (no activity). A key that does not exist counts as deleted.
        When storage fails, the server returns an error and this raises
        (``UnknownError``, with the server code such as ``STORAGE_TRANSIENT``
        or ``STORAGE_PERMANENT`` in the message) instead of returning False.

        Args:
            content_id (str): The ID of the content to delete.

        Raises:
            UnknownError: If the server could not delete the file.

        Returns:
            bool: True if deletion was successful.
        '''
        response = self.request_gql(
            query=Queries.DELETE,
            variables=Queries.DELETE["variables"](content_id)
        )
        return response
