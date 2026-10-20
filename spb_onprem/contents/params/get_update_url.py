from typing import Optional

from spb_onprem.exceptions import BadParameterError


def get_update_url_params(content_id: str, content_type: Optional[str] = None):
    """Variables of generateContentUpdateURL (presigned PUT URL of an existing content)."""
    if content_id is None or (isinstance(content_id, str) and not content_id.strip()):
        raise BadParameterError("content_id is required.")
    params = {"id": content_id}
    if content_type is not None:
        params["content_type"] = content_type
    return params
