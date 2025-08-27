from typing import List, Optional
from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.data.enums import DataType
from .scene import Scene
from .annotation import Annotation
from .prediction import Prediction
from .data_meta import DataMeta
from .data_slice import DataSlice
from .frame import Frame
from spb_onprem.contents.entities import BaseContent

class Data(CustomBaseModel):
    """
    THE DATA.
    """
    id: Optional[str] = None
    dataset_id: Optional[str] = Field(None, alias="datasetId")
    slice_ids: Optional[List[str]] = Field(None, alias="sliceIds")
    key: Optional[str] = None
    type: Optional[DataType] = None
    scene: Optional[List[Scene]] = None
    frames: Optional[List[Frame]] = None
    thumbnail: Optional[BaseContent] = None
    annotation: Optional[Annotation] = None
    predictions: Optional[List[Prediction]] = None
    meta: Optional[List[DataMeta]] = None
    system_meta: Optional[List[DataMeta]] = Field(None, alias="systemMeta")
    created_at: Optional[str] = Field(None, alias="createdAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    updated_by: Optional[str] = Field(None, alias="updatedBy")
    slices: Optional[List[DataSlice]] = None
