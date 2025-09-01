from typing import Optional
from spb_onprem.base_model import BaseModel


class Model(BaseModel):
    """Model entity representing a model in the dataset."""
    
    id: str
    name: Optional[str] = None