from typing import List, Optional
from spb_onprem.base_model import CustomBaseModel, Field


class PredictionSet(CustomBaseModel):
    """PredictionSet entity representing a set of predictions in the dataset."""
    
    id: str
    name: Optional[str] = None
    annotations_contents: Optional[List[str]] = Field(None, alias="annotationsContents")
    evaluation_result_content: Optional[dict] = Field(None, alias="evaluationResultContent")