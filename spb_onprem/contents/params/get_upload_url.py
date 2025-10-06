

def get_upload_url_params(
    content_id: str,
    file_name: str,
    content_type: str = None,
):
    return {
        "id": content_id,
        "file_name": file_name,
        "content_type": content_type
    }
