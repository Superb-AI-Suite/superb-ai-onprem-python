from spb_onprem.data.entities import Scene


def update_scene_params(
    dataset_id: str,
    data_id: str,
    scene: Scene
):
    """Update scene to selected data.

    Args:
        dataset_id (str): dataset id which the data belongs to
        data_id (str): data id to be updated
        scene (Scene): scene to be updated

    Returns:
        dict: the params for graphql query
    """

    if not isinstance(scene, Scene):
        raise ValueError("scene must be an instance of Scene.")
    else:
        if scene.id is None:
            raise ValueError("scene.id must be provided.")
        if scene.type is None:
            raise ValueError("scene.type must be provided.")

    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "id": scene.id,
        "scene": {
            "content": scene.content,
            "type": scene.type.value,
            "meta": scene.meta,
        },
    }
