import json

from pydantic import BaseModel, Field


class CustomBaseModel(BaseModel):
    class Config:
        populate_by_name = True
        
    def __json__(self):
        return self.model_dump()
        
    @classmethod
    def __from_json__(cls, json_str):
        if isinstance(json_str, str):
            data = json.loads(json_str)
        else:
            data = json_str
        return cls.model_validate(data)
