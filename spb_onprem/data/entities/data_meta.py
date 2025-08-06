from typing import Optional, Union, Dict, List
from datetime import datetime
from spb_onprem.data.enums import DataMetaTypes, DataMetaValue
from spb_onprem.base_model import CustomBaseModel


class DataMeta(CustomBaseModel):
    """
    The meta of the data.
    Meta is the metadata of the data.
    """
    key: Optional[str] = None
    type: Optional[DataMetaTypes] = None
    value: Optional[DataMetaValue] = None

    @classmethod
    def from_dict(cls, meta: Dict[str, DataMetaValue]) -> List["DataMeta"]:
        return [
            cls(
                key=key,
                value=val,
                type=(
                    DataMetaTypes.BOOLEAN if isinstance(val, bool) else
                    DataMetaTypes.NUMBER if isinstance(val, (int, float)) else
                    DataMetaTypes.DATETIME if isinstance(val, datetime) else
                    DataMetaTypes.STRING if isinstance(val, str) else
                    DataMetaTypes.ANNOTATION  # list or dict
                ),
            )
            for key, val in meta.items()
        ]
