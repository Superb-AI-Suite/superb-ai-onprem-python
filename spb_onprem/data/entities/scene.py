from typing import Optional
from sdk.base_model import CustomBaseModel
from sdk.data.enums import SceneType
from sdk.contents.entities import BaseContent

class Scene(CustomBaseModel):
    """
    The scene of the data.
    Scene is the representation of the file of the data.
    """
    id: Optional[str] = None
    type: Optional[SceneType] = None
    content: Optional[BaseContent] = None
    meta: Optional[dict] = None
