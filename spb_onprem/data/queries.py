from .params import (
    create_params,
    update_params,
    get_params,
    get_data_id_list_params,
    get_data_list_params,
    remove_data_from_slice_params,
    insert_data_to_slice_params,
    delete_data_params,
    insert_prediction_params,
    delete_prediction_params,
    update_annotation_params,
    insert_annotation_version_params,
    delete_annotation_version_params,
    update_slice_annotation_params,
    insert_slice_annotation_version_params,
    update_slice_annotation_version_params,
    delete_slice_annotation_version_params,
    change_data_status_params,
    change_data_labeler_params,
    change_data_reviewer_params,
    update_data_slice_params,
    update_frames_params,
)


class Schemas:
    DATA_ID_PAGE = '''
        data {
            id
        }
        next
        totalCount
    '''
    
    DATA = '''
        id
        datasetId
        sliceIds
        key
        type
        scene {
            id
            type
            content {
                id
            }
            meta
        }
        frames {
            id
            index
            capturedAt
            geoLocation {
                lat
                lon
            }
            meta
        }
        annotation {
            meta
            versions {
                id
                channels
                version
                content {
                    id
                }
                meta
            }
        }
        meta {
            key
            type
            value
        }
        slices {
            id
            status
            labeler
            reviewer
            tags
            statusChangedAt
            annotation {
                versions {
                    id
                    channels
                    version
                    content {
                        id
                    }
                    meta
                }
                meta
            }
            meta
        }
        createdAt
        updatedAt
        createdBy
        updatedBy
    '''

    DATA_PAGE = f'''
        data {{
            {DATA}  
        }}
    '''


class Queries():
    CREATE = {
        "name": "createData",
        "query": f'''
            mutation createData(
                $datasetId: ID!,
                $key: String!,
                $type: DataType!,
                $slices: [ID!],
                $scene: [SceneInput!],
                $thumbnail: ContentBaseInput,
                $annotation: AnnotationInput,
                $predictions: [PredictionInput!],
                $meta: [DataMetaInput!]
                $systemMeta: [DataMetaInput!]
            ) {{
            createData(
                datasetId: $datasetId,
                key: $key,
                type: $type,
                slices: $slices,
                scene: $scene,
                thumbnail: $thumbnail,
                annotation: $annotation,
                predictions: $predictions,
                meta: $meta,
                systemMeta: $systemMeta
            ) 
                {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": create_params,
    }

    UPDATE = {
        "name": "updateData",
        "query": f'''
            mutation updateData(
                $dataset_id: ID!,
                $data_id: ID!,
                $key: String,
                $meta: [DataMetaInput!],
                $systemMeta: [DataMetaInput!]
            ) {{
            updateData(
                datasetId: $dataset_id,
                id: $data_id,
                key: $key,
                meta: $meta,
                systemMeta: $systemMeta
            ) 
                {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": update_params,
    }

    GET = {
        "name": "data",
        "query": f'''
            query Query(
                $dataset_id: String!,
                $key: String,
                $id: ID,
            ) {{
                data(
                    datasetId: $dataset_id,
                    id: $id,
                    key: $key,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": get_params,
    }

    GET_ID_LIST = {
        "name": "dataList",
        "query": f'''
            query Query(
                $dataset_id: String!,
                $filter: DataFilter,
                $cursor: String,
                $length: Int
            ) {{
                dataList(
                    datasetId: $dataset_id,
                    filter: $filter,
                    cursor: $cursor,
                    length: $length
                ) {{
                    {Schemas.DATA_ID_PAGE}
                }}
            }}
        ''',
        "variables": get_data_id_list_params
    }

    GET_LIST = {
        "name": "dataList",
        "query": f'''
            query Query(
                $dataset_id: String!,
                $filter: DataFilter,
                $cursor: String,
                $length: Int
            ) {{
                dataList(
                    datasetId: $dataset_id,
                    filter: $filter,
                    cursor: $cursor,
                    length: $length
                ) {{
                    {Schemas.DATA_PAGE}
                    next
                    totalCount
                }}
            }}
        ''',
        "variables": get_data_list_params,
    }

    REMOVE_FROM_SLICE = {
        "name": "removeDataFromSlice",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $slice_id: ID!,
            ) {{
                removeDataFromSlice(
                    datasetId: $dataset_id,
                    id: $data_id,
                    sliceId: $slice_id,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": remove_data_from_slice_params,
    }

    ADD_TO_SLICE = {
        "name": "addDataToSlice",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $slice_id: ID!,
            ) {{
                addDataToSlice(
                    datasetId: $dataset_id,
                    id: $data_id,
                    sliceId: $slice_id,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": insert_data_to_slice_params,
    }

    DELETE = {
        "name": "deleteData",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
            ) {{
                deleteData(
                    datasetId: $dataset_id,
                    id: $data_id,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": delete_data_params,
    }

    INSERT_PREDICTION = {
        "name": "insertPrediction",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $prediction: PredictionInput!,
            ) {{
                insertPrediction(
                    datasetId: $dataset_id,
                    dataId: $data_id,
                    prediction: $prediction,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": insert_prediction_params,
    }

    DELETE_PREDICTION = {
        "name": "deletePrediction",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $set_id: ID!,
            ) {{
                deletePrediction(
                    datasetId: $dataset_id,
                    dataId: $data_id,
                    setId: $set_id,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": delete_prediction_params,
    }
    
    UPDATE_ANNOTATION = {
        "name": "updateAnnotation",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $meta: JSONObject!,
            ) {{
                updateAnnotation(
                    datasetId: $dataset_id,
                    dataId: $data_id,
                    meta: $meta,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": update_annotation_params,
    }

    INSERT_ANNOTATION_VERSION = {
        "name": "insertAnnotationVersion",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $version: AnnotationVersionInput!,
            ) {{
                insertAnnotationVersion(
                    datasetId: $dataset_id,
                    dataId: $data_id,
                    version: $version,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": insert_annotation_version_params,
    }
    
    DELETE_ANNOTATION_VERSION = {
        "name": "deleteAnnotationVersion",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $version_id: ID!,
            ) {{
                deleteAnnotationVersion(
                    datasetId: $dataset_id,
                    dataId: $data_id,
                    id: $version_id,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": delete_annotation_version_params,
    }

    UPDATE_SLICE_ANNOTATION = {
        "name": "updateSliceAnnotation",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $slice_id: ID!,
                $meta: JSONObject!,
            ) {{
                updateSliceAnnotation(
                    datasetId: $dataset_id,
                    dataId: $data_id,
                    sliceId: $slice_id,
                    meta: $meta,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": update_slice_annotation_params,
    }

    INSERT_SLICE_ANNOTATION_VERSION = {
        "name": "insertSliceAnnotationVersion",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $slice_id: ID!,
                $version: AnnotationVersionInput!,
            ) {{
                insertSliceAnnotationVersion(
                    datasetId: $dataset_id,
                    dataId: $data_id,
                    sliceId: $slice_id,
                    version: $version,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": insert_slice_annotation_version_params,
    }

    UPDATE_SLICE_ANNOTATION_VERSION = {
        "name": "updateSliceAnnotationVersion",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $slice_id: ID!,
                $id: ID!,
                $channel: String,
                $version: String,
                $meta: JSONObject,
            ) {{
                updateSliceAnnotationVersion(
                    datasetId: $dataset_id,
                    dataId: $data_id,
                    sliceId: $slice_id,
                    id: $id,
                    channel: $channel,
                    version: $version,
                    meta: $meta,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": update_slice_annotation_version_params,
    }

    DELETE_SLICE_ANNOTATION_VERSION = {
        "name": "deleteSliceAnnotationVersion",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $slice_id: ID!,
                $id: ID!,
            ) {{
                deleteSliceAnnotationVersion(
                    datasetId: $dataset_id,
                    dataId: $data_id,
                    sliceId: $slice_id,
                    id: $id,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": delete_slice_annotation_version_params,
    }

    CHANGE_DATA_STATUS = {
        "name": "changeDataStatus",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $slice_id: ID!,
                $status: DataSliceStatus!,
            ) {{
                changeDataStatus(
                    datasetId: $dataset_id,
                    dataId: $data_id,
                    sliceId: $slice_id,
                    status: $status,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": change_data_status_params,
    }

    CHANGE_DATA_LABELER = {
        "name": "changeDataLabeler",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $slice_id: ID!,
                $labeler: String,
            ) {{
                changeDataLabeler(
                    datasetId: $dataset_id,
                    dataId: $data_id,
                    sliceId: $slice_id,
                    labeler: $labeler,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": change_data_labeler_params,
    }

    CHANGE_DATA_REVIEWER = {
        "name": "changeDataReviewer",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $slice_id: ID!,
                $reviewer: String,
            ) {{
                changeDataReviewer(
                    datasetId: $dataset_id,
                    dataId: $data_id,
                    sliceId: $slice_id,
                    reviewer: $reviewer,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": change_data_reviewer_params,
    }

    UPDATE_DATA_SLICE = {
        "name": "updateDataSlice",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $slice_id: ID!,
                $meta: JSONObject!,
            ) {{
                updateDataSlice(
                    datasetId: $dataset_id,
                    dataId: $data_id,
                    sliceId: $slice_id,
                    meta: $meta,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": update_data_slice_params,
    }
    
    UPDATE_FRAMES = {
        "name": "updateFrames",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $data_id: ID!,
                $frames: [DataFrameInput!],
            ) {{
                updateFrames(
                    datasetId: $dataset_id,
                    dataId: $data_id,
                    frames: $frames,
                ) {{
                    {Schemas.DATA}
                }}
            }}
        ''',
        "variables": update_frames_params,
    }
