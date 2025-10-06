from typing import Optional


def get_upload_url_params(
    content_id: str,
    file_name: str,
    content_type: Optional[str] = None,
):
    return {
        "content_id": content_id,
        "file_name": file_name,
        "content_type": content_type
    }
