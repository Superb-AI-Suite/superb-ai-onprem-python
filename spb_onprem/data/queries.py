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
        annotation {
            versions {
                id
                content {
                    id
                }
                meta
            }
        }
        predictions {
            setId
            content {
                id
            }
            meta
        }
        meta {
            key
            type
            value
        }
        systemMeta {
            key
            type
            value
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
                $datasetId: ID!,
                $id: ID!,
                $key: String,
                $meta: [DataMetaInput!],
                $systemMeta: [DataMetaInput!]
            ) {{
            updateData(
                datasetId: $datasetId,
                id: $id,
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
                }}
            }}
        ''',
        "variables": get_data_list_params
    }

    REMOVE_FROM_SLICE = {
        "name": "removeDataFromSlice",
        "query": f'''
            mutation (
                $dataset_id: ID!,
                $slice_id: ID!,
                $data_id: ID!,
            ) {{
                removeDataFromSlice(
                    datasetId: $dataset_id,
                    sliceId: $slice_id,
                    id: $data_id,
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
                $slice_id: ID!,
                $data_id: ID!,
            ) {{
                addDataToSlice(
                    datasetId: $dataset_id,
                    sliceId: $slice_id,
                    id: $data_id,
                ) {{
                    {Schemas.DATA}
                }}
            }}
            )
        ''',
        "variables": insert_data_to_slice_params,
    }

    DELETE = {
        "name": "deleteData",
        "query": '''
            mutation (
                $id: ID!,
                $dataset_id: ID!
            ) {
                deleteData(
                    id: $id,
                    datasetId: $dataset_id
                )
            }
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
