import json
from typing import Union, List
from spb_onprem.data.entities import Frame
from spb_onprem.base_types import UndefinedType, Undefined


def update_frames_params(
    dataset_id: str,
    data_id: str,
    frames: Union[List[Frame], UndefinedType, None] = Undefined,  
):
    """Update frames of selected data.
    Args:
        dataset_id (str): dataset id which the data belongs to
        data_id (str): data id to be updated
        frames (list[Frame]): list of frames to be updated  
        
    Returns:
        dict: the params for graphql query
    """
    result = {
        "dataset_id": dataset_id,
        "data_id": data_id,
    }
    if frames is not Undefined:
        result["frames"] = []
        for frame in frames:
            frame_data = {
                "index": frame.index,
                "capturedAt": frame.captured_at,
                "meta": json.dumps(frame.meta) if frame.meta else None,
            }
            if frame.geo_location is not None:
                frame_data["geoLocation"] = {
                    "lat": frame.geo_location.lat,
                    "lon": frame.geo_location.lon
                }
            result["frames"].append(frame_data)

    return result
