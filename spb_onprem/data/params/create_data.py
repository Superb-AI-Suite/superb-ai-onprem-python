from spb_onprem.data.entities import Data


def create_params(
    data: Data,
):
    """Make the variables for the createData query.

    Args:
        data (Data): The data object what you want to create.
    """
    return {
        "datasetId": data.dataset_id,
        "key": data.key,
        "type": data.type.value,
        "slices": data.slice_ids if data.slice_ids is not None else [],
        "scene": [
            {
                "type": scene.type.value,
                "content": {
                    "id": scene.content.id,
                },
                "meta": scene.meta,
            }
            for scene in data.scene
        ] if data.scene is not None else None,
        "thumbnail": {
            "id": data.thumbnail.id,
        } if data.thumbnail is not None else None,
        "annotation": {
            "versions": [
                {
                    "content": {
                        "id": version.content.id,
                    },
                    "meta": version.meta,
                }
                for version in data.annotation.versions
            ],
            "meta": data.annotation.meta
        } if data.annotation is not None else None,
        "predictions": [
            {
                "setId": prediction.set_id,
                "content": {
                    "id": prediction.content.id,
                },
                "meta": prediction.meta,
            }
            for prediction in data.predictions
        ] if data.predictions is not None else [],
        "meta": [
            {
                "key": meta.key,
                "type": meta.type.value,
                "value": meta.value,
            }
            for meta in data.meta
        ] if data.meta is not None else None,
        "systemMeta": [
            {
                "key": meta.key,
                "type": meta.type.value,
                "value": meta.value,
            }
            for meta in data.system_meta
        ] if data.system_meta is not None else None,
    }
