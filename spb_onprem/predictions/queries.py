from .params import (
    get_prediction_sets_params,
    get_prediction_set_params,
    delete_prediction_set_params,
    delete_prediction_from_data_params,
    create_prediction_set_params,
    update_prediction_set_data_info_params,
)


class Queries:
    GET_PREDICTION_SETS = {
        "name": "getPredictionSets",
        "query": '''
            query GetPredictionSets($dataset_id: String!, $filter: PredictionSetFilter, $cursor: String, $length: Int) {
                predictionSets(datasetId: $dataset_id, filter: $filter, cursor: $cursor, length: $length) {
                    predictionSets {
                        id
                        name
                    }
                    next
                    totalCount
                }
            }
        ''',
        "variables": get_prediction_sets_params
    }
    
    GET_PREDICTION_SET = {
        "name": "getPredictionSet",
        "query": '''
            query GetPredictionSet($dataset_id: String!, $id: String!) {
                predictionSet(datasetId: $dataset_id, id: $id) {
                    id
                    name
                    annotationsContents
                    evaluationResultContent {
                        id
                    }
                }
            }
        ''',
        "variables": get_prediction_set_params
    }
    
    DELETE_PREDICTION_SET = {
        "name": "deletePredictionSet",
        "query": '''
            mutation DeletePredictionSet($dataset_id: String!, $id: String!) {
                deletePredictionSet(datasetId: $dataset_id, id: $id)
            }
        ''',
        "variables": delete_prediction_set_params
    }
    
    DELETE_PREDICTION_FROM_DATA = {
        "name": "deletePredictionFromData",
        "query": '''
            mutation DeletePrediction($dataset_id: String!, $data_id: String!, $set_id: String!) {
                deletePrediction(datasetId: $dataset_id, dataId: $data_id, setId: $set_id)
            }
        ''',
        "variables": delete_prediction_from_data_params
    }
    
    CREATE_PREDICTION_SET = {
        "name": "createPredictionSet",
        "query": '''
            mutation CreatePredictionSet(
                $datasetId: ID!,
                $modelId: ID!,
                $name: String!,
                $description: String,
                $type: PredictionSetTypes!,
                $dataInfo: PredictionSetDataInfoInput
            ) {
                createPredictionSet(
                    datasetId: $datasetId,
                    modelId: $modelId,
                    name: $name,
                    description: $description,
                    type: $type,
                    dataInfo: $dataInfo
                ) {
                    id
                }
            }
        ''',
        "variables": create_prediction_set_params
    }
    
    UPDATE_PREDICTION_SET_DATA_INFO = {
        "name": "updatePredictionSet",
        "query": '''
            mutation UpdatePredictionSet(
                $datasetId: ID!,
                $updatePredictionSetId: ID!,
                $dataInfo: PredictionSetDataInfoInput
            ) {
                updatePredictionSet(
                    datasetId: $datasetId,
                    id: $updatePredictionSetId,
                    dataInfo: $dataInfo
                ) {
                    id
                }
            }
        ''',
        "variables": update_prediction_set_data_info_params
    }