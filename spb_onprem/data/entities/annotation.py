from typing import Optional, List

from sdk.base_model import CustomBaseModel
from sdk.contents.entities import BaseContent


class AnnotationVersion(CustomBaseModel):
    """
    The version of the annotation.
    Annotation version is the version of the data annotation.
    This has the content of the data annotation.
    """
    id: Optional[str] = None
    content: Optional[BaseContent] = None
    meta: Optional[dict] = None


class Annotation(CustomBaseModel):
    """
    The annotation of the data.
    Annotation has the versions of the data annotation.
    """
    versions: Optional[List[AnnotationVersion]] = None
    meta: Optional[dict] = None

