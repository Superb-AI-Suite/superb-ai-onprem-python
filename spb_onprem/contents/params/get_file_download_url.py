

def get_file_download_url_params(
    content_id: str,
    file_name: str,
):
    return {
        "content_id": content_id,
        "file_name": file_name
    }
