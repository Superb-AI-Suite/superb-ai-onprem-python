from typing import Optional
from spb_onprem.base_model import CustomBaseModel
from spb_onprem.data.enums import SceneType
from spb_onprem.contents.entities import BaseContent

class Scene(CustomBaseModel):
    """
    The scene of the data.
    Scene is the representation of the file of the data.
    """
    id: Optional[str] = None
    type: Optional[SceneType] = None
    content: Optional[BaseContent] = None
    meta: Optional[dict] = None
