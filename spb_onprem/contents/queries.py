from typing import (
    Union,
)

from spb_onprem.base_types import (
    Undefined,
    UndefinedType,
)

class Queries:
    """ Content Queries """
    
    @staticmethod
    def create_variables(
        key: Union[str, UndefinedType] = Undefined,
        content_type: Union[str, UndefinedType] = Undefined,
    ):
        params = {}
        
        if key is not Undefined:
            params["key"] = key
        if content_type is not Undefined:
            params["content_type"] = content_type
        return params

    CREATE = {
        "name": "createContent",
        "query": '''
            mutation CreateContent($key: String, $content_type: String) {
                createContent(key: $key, contentType: $content_type) {
                    content {
                        id
                        key
                        location
                        createdAt
                        createdBy
                    }
                    uploadURL
                }
            }
        ''',
        "variables": create_variables
    }
    
    @staticmethod
    def get_download_url_params(
        content_id: str,
    ):
        return {
            "id": content_id
        }
    
    GET_DOWNLOAD_URL = {
        "name": "generateContentDownloadURL",
        "query": '''
            mutation GenerateContentDownloadURL($id: ID!) {
                generateContentDownloadURL(id: $id) 
            }
        ''',
        "variables": get_download_url_params
    }
