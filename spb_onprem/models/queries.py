from spb_onprem.models.params import (
    models_params,
    model_params,
    create_model_params,
    update_model_params,
    pin_model_params,
    unpin_model_params,
    delete_model_params,
)


class Schemas:
    MODEL_TRAIN_CLASS = '''
        class
        annotationType
        ap
        trainingAnnotationsCount
        validationAnnotationsCount
    '''
    
    MODEL = '''
        id
        datasetId
        baselineModel
        name
        description
        trainingClasses {
            class
            annotationType
            ap
            trainingAnnotationsCount
            validationAnnotationsCount
        }
        trainingDataCount
        validationDataCount
        isPinned
        isTrained
        trainedAt
        modelContent {
            id
            downloadURL
        }
        createdBy
        createdAt
        updatedBy
        updatedAt
        meta
        trainingSlices {
            id
            datasetId
            name
            description
            isPinned
            createdAt
            createdBy
            updatedAt
            updatedBy
        }
        validationSlices {
            id
            datasetId
            name
            description
            isPinned
            createdAt
            createdBy
            updatedAt
            updatedBy
        }
    '''


class Queries():
    MODELS = {
        "name": "models",
        "query": f'''
            query Models(
                $datasetId: ID!,
                $filter: ModelFilter,
                $cursor: String,
                $length: Int
            ) {{
                models(
                    datasetId: $datasetId,
                    filter: $filter,
                    cursor: $cursor,
                    length: $length
                ) {{
                    models {{
                        {Schemas.MODEL}
                    }}
                    next
                    totalCount
                }}
            }}
        ''',
        "variables": models_params,
    }
    
    MODEL = {
        "name": "model",
        "query": f'''
            query Model(
                $datasetId: ID!,
                $modelId: ID!
            ) {{
                model(
                    datasetId: $datasetId,
                    id: $modelId
                ) {{
                    {Schemas.MODEL}
                }}
            }}
        ''',
        "variables": model_params,
    }
    
    CREATE_MODEL = {
        "name": "createModel",
        "query": f'''
            mutation CreateModel(
                $datasetId: ID!,
                $name: String!,
                $description: String,
                $baselineModel: String!,
                $trainingClasses: [ModelTrainClassInput!],
                $trainingSliceIds: [ID!]!,
                $validationSliceIds: [ID!]!,
                $modelContentId: String,
                $isTrained: Boolean,
                $trainedAt: DateTime,
                $isPinned: Boolean,
                $meta: JSONObject
            ) {{
                createModel(
                    datasetId: $datasetId,
                    name: $name,
                    description: $description,
                    baselineModel: $baselineModel,
                    trainingClasses: $trainingClasses,
                    trainingSliceIds: $trainingSliceIds,
                    validationSliceIds: $validationSliceIds,
                    modelContentId: $modelContentId,
                    isTrained: $isTrained,
                    trainedAt: $trainedAt,
                    isPinned: $isPinned,
                    meta: $meta
                ) {{
                    {Schemas.MODEL}
                }}
            }}
        ''',
        "variables": create_model_params,
    }
    
    UPDATE_MODEL = {
        "name": "updateModel",
        "query": f'''
            mutation UpdateModel(
                $datasetId: ID!,
                $id: ID!,
                $name: String,
                $description: String,
                $trainingClasses: [ModelTrainClassInput!],
                $modelContentId: String,
                $isTrained: Boolean,
                $trainedAt: DateTime,
                $meta: JSONObject
            ) {{
                updateModel(
                    datasetId: $datasetId,
                    id: $id,
                    name: $name,
                    description: $description,
                    trainingClasses: $trainingClasses,
                    modelContentId: $modelContentId,
                    isTrained: $isTrained,
                    trainedAt: $trainedAt,
                    meta: $meta
                ) {{
                    {Schemas.MODEL}
                }}
            }}
        ''',
        "variables": update_model_params,
    }
    
    PIN_MODEL = {
        "name": "pinModel",
        "query": f'''
            mutation PinModel(
                $datasetId: ID!,
                $id: ID!
            ) {{
                pinModel(
                    datasetId: $datasetId,
                    id: $id
                ) {{
                    {Schemas.MODEL}
                }}
            }}
        ''',
        "variables": pin_model_params,
    }
    
    UNPIN_MODEL = {
        "name": "unpinModel",
        "query": f'''
            mutation UnpinModel(
                $datasetId: ID!,
                $id: ID!
            ) {{
                unpinModel(
                    datasetId: $datasetId,
                    id: $id
                ) {{
                    {Schemas.MODEL}
                }}
            }}
        ''',
        "variables": unpin_model_params,
    }
    
    DELETE_MODEL = {
        "name": "deleteModel",
        "query": '''
            mutation DeleteModel(
                $datasetId: ID!,
                $id: ID!
            ) {
                deleteModel(
                    datasetId: $datasetId,
                    id: $id
                )
            }
        ''',
        "variables": delete_model_params,
    }
