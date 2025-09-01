from .params import (
    get_models_params,
    delete_model_params,
)


class Queries:
    GET_MODELS = {
        "name": "getModels",
        "query": '''
            query GetModels($dataset_id: String!, $filter: ModelFilter, $cursor: String, $length: Int) {
                models(datasetId: $dataset_id, filter: $filter, cursor: $cursor, length: $length) {
                    models {
                        id
                        name
                    }
                    next
                    totalCount
                }
            }
        ''',
        "variables": get_models_params
    }
    
    DELETE_MODEL = {
        "name": "deleteModel",
        "query": '''
            mutation DeleteModel($dataset_id: String!, $id: String!) {
                deleteModel(datasetId: $dataset_id, id: $id)
            }
        ''',
        "variables": delete_model_params
    }