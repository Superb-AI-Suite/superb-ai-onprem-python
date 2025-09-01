from typing import List, Optional
from spb_onprem.base_model import BaseModel


class PredictionSet(BaseModel):
    """PredictionSet entity representing a set of predictions in the dataset."""
    
    id: str
    name: Optional[str] = None
    annotations_contents: Optional[List[str]] = None
    evaluation_result_content: Optional[dict] = None
    
    class Config:
        populate_by_name = True
        alias_generator = lambda field_name: (
            "annotationsContents" if field_name == "annotations_contents"
            else "evaluationResultContent" if field_name == "evaluation_result_content"
            else field_name
        )