from typing import (
    Union,
    Optional,
    List
)
from spb_onprem.base_types import (
    Undefined,
    UndefinedType,
)
from spb_onprem.data.entities import (
    DataMeta,
    DataAnnotationStat,
)


def update_params(
    dataset_id: str,
    data_id: str,
    key: Union[
        Optional[str],
        UndefinedType
    ] = Undefined,
    meta: Union[
        Optional[List[DataMeta]],
        UndefinedType
    ] = Undefined,
    annotation_stats: Union[
        Optional[List[DataAnnotationStat]],
        UndefinedType
    ] = Undefined,
    caption: Union[
        Optional[str],
        UndefinedType
    ] = Undefined,
    expected_caption: Union[
        UndefinedType,
        None,
        str
    ] = Undefined,
    caption_source: Union[
        str,
        UndefinedType
    ] = Undefined
):
    """Make the variables for the updateData query.

    Args:
        dataset_id (str): The dataset ID of the data.
        data_id (str): The ID of the data.
        key (str): The key of the data.
        meta (List[DataMeta]): The meta of the data.
        annotation_stats (List[DataAnnotationStat]): The annotation stats of the data.
        caption (str): The caption of the data.
        expected_caption (str): The expected caption of the data.
        caption_source (str): Which slot the caption writes to (contract v2):
            "GROUND_TRUTH" or "VLM_GENERATED". Omitted = server default (VLM).
    """
    variables = {
        "dataset_id": dataset_id,
        "data_id": data_id,
    }
    
    if key is not Undefined:
        variables["key"] = key
    
    if meta is not Undefined:
        if meta is not None and not isinstance(meta, list):
            raise ValueError("meta must be a list of DataMeta or None.")
        variables["meta"] = [
            {
                "key": meta_item.key,
                "type": meta_item.type.value,
                "value": meta_item.value,
            }
            for meta_item in meta
        ] if meta is not None else None

    if annotation_stats is not Undefined:
        variables["annotation_stats"] = [
            stat.model_dump(by_alias=True, exclude_unset=True) for stat in annotation_stats
        ] if annotation_stats is not None else None

    if caption is not Undefined:
        variables["caption"] = caption

    if expected_caption is not Undefined:
        variables["expectedCaption"] = expected_caption

    if caption_source is not Undefined:
        variables["captionSource"] = caption_source

    return variables
