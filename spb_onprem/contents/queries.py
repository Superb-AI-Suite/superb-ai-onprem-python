from .params import (
    create_variables,
    get_download_url_params,
)

class Queries:
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
    
    
    GET_DOWNLOAD_URL = {
        "name": "generateContentDownloadURL",
        "query": '''
            mutation GenerateContentDownloadURL($id: ID!) {
                generateContentDownloadURL(id: $id) 
            }
        ''',
        "variables": get_download_url_params
    }
