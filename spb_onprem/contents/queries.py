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
    ):
        if key is not Undefined:
            return {"key": key}
        else:
            return {}

    CREATE = {
        "name": "createContent",
        "query": '''
            mutation CreateContent($key: String) {
                createContent(key: $key) {
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
        id: str,
    ):
        return {
            "id": id
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
