from typing import Optional
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.contents.entities import BaseContent


class Prediction(CustomBaseModel):
    """
    The prediction of the data.
    Prediction has the predictions of the data.
    """
    set_id: Optional[str] = Field(None, alias="setId")
    content: Optional[BaseContent] = None
    meta: Optional[dict] = None
