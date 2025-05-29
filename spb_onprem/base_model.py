from pydantic import BaseModel, Field


class CustomBaseModel(BaseModel):
    class Config:
        populate_by_name = True
