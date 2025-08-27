from typing import Optional, List

from spb_onprem.base_model import CustomBaseModel
from spb_onprem.contents.entities import BaseContent


class AnnotationVersion(CustomBaseModel):
    """
    The version of the annotation.
    Annotation version is the version of the data annotation.
    This has the content of the data annotation.
    """
    id: Optional[str] = None
    channels: Optional[List[str]] = None
    version: Optional[str] = None
    content: Optional[BaseContent] = None
    meta: Optional[dict] = None


class Annotation(CustomBaseModel):
    """
    The annotation of the data.
    Annotation has the versions of the data annotation.
    """
    versions: Optional[List[AnnotationVersion]] = None
    meta: Optional[dict] = None

