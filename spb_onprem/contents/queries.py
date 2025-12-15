from .params import (
    create_variables,
    get_download_url_params,
    delete_content_params,
    get_upload_url_params,
    get_file_download_url_params,
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
    
    GET_UPLOAD_URL = {
        "name": "generateFileUploadURL",
        "query": '''
            mutation GenerateFileUploadURL($content_id: ID!, $file_name: String!, $content_type: String) {
                generateFileUploadURL(contentId: $content_id, fileName: $file_name, contentType: $content_type) 
            }
        ''',
        "variables": get_upload_url_params
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
    
    GET_FILE_DOWNLOAD_URL = {
        "name": "generateFileDownloadURL",
        "query": '''
            mutation GenerateFileDownloadURL($content_id: ID!, $file_name: String!) {
                generateFileDownloadURL(contentId: $content_id, fileName: $file_name) 
            }
        ''',
        "variables": get_file_download_url_params
    }
    
    CREATE_FOLDER_CONTENT = {
        "name": "createFolderContent",
        "query": '''
            mutation CreateFolderContent {
                createFolderContent {
                    id
                }
            }
        ''',
        "variables": lambda: {}
    }
    
    DELETE = {
        "name": "deleteContent",
        "query": '''
            mutation DeleteContent($id: ID!) {
                deleteContent(id: $id)
            }
        ''',
        "variables": delete_content_params
    }
