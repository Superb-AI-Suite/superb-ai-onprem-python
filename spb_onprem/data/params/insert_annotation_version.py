from spb_onprem.data.entities import AnnotationVersion


def insert_annotation_version_params(
    dataset_id: str,
    data_id: str,
    version: AnnotationVersion,
):
    """Insert annotation version to selected data.

    Args:
        dataset_id (str): dataset id which the data belongs to
        data_id (str): data id to be inserted
        annotation (AnnotationVersion): annotation version to be inserted

    Returns:
        dict: the params for graphql query
    """
    version_data = {
        "content": version.content.model_dump(
            by_alias=True, exclude_unset=True
        ),
        "meta": version.meta
    }
    
    # channels과 version 필드가 있으면 추가
    if version.channels is not None:
        version_data["channels"] = version.channels
    if version.version is not None:
        version_data["version"] = version.version

    return {
        "dataset_id": dataset_id,
        "data_id": data_id,
        "version": version_data,
    }
