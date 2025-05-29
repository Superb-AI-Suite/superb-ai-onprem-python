from typing import Optional

from spb_onprem.base_model import CustomBaseModel, Field

class BaseContent(CustomBaseModel):
    """The content.
    This is the actual file that is stored in the file storage.

    Args:
        BaseModel (_type_): _description_
    """
    id: str
    download_url:Optional[str] = Field(None, alias="downloadURL")
