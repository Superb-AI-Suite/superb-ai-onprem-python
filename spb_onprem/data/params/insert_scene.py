from spb_onprem.data.entities import Scene


def insert_scene_params(
    dataset_id: str,
    data_id: str,
    scene: Scene
):
    """Insert scene to selected data.

    Args:
        dataset_id (str): dataset id which the data belongs to
        data_id (str): data id to be inserted
        scene (Scene): scene to be inserted

    Returns:
        dict: the params for graphql query
    """

    if not isinstance(scene, Scene):
        raise ValueError("scene must be an instance of Scene.")
    else:
        if scene.type is None:
            raise ValueError("scene.type must be provided.")

    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "scene": scene.model_dump(
            by_alias=True, exclude_unset=True
        ),
    }
