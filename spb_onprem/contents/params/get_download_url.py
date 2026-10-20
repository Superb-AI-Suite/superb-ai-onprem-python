from spb_onprem.exceptions import BadParameterError


def get_download_url_params(
    content_id: str,
):
    if content_id is None or not isinstance(content_id, str) or not content_id.strip():
        raise BadParameterError("content_id is required.")
    return {
        "id": content_id
    }
