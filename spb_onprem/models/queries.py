from .params import (
    get_model_params,
    get_models_params,
    create_model_params,
    update_model_params,
    delete_model_params,
)


class Schemas:
    TRAINING_REPORT = """
        id
        name
        modelId
        contentId
        description
        createdAt
        updatedAt
        createdBy
        updatedBy
    """

    MODEL = f"""
        datasetId
        id
        name
        description
        status
        taskType
        customDagId
        totalDataCount
        trainDataCount
        validationDataCount
        trainingParameters
        trainingReport {{
            {TRAINING_REPORT}
        }}
        trainSliceId
        validationSliceId
        completedAt
        isPinned
        scoreKey
        scoreValue
        scoreUnit
        createdAt
        updatedAt
        createdBy
        updatedBy
    """


class Queries:
    GET = {
        "name": "model",
        "query": f"""
            query Query(
                $dataset_id: ID!,
                $model_id: ID,
                $name: String,
            ) {{
                model(
                    datasetId: $dataset_id,
                    modelId: $model_id,
                    name: $name,
                ) {{
                    {Schemas.MODEL}
                }}
            }}
        """,
        "variables": get_model_params,
    }

    GET_LIST = {
        "name": "models",
        "query": f"""
            query Query(
                $dataset_id: ID!,
                $filter: ModelFilter,
                $order_by: ModelOrderBy,
                $cursor: String,
                $length: Int,
            ) {{
                models(
                    datasetId: $dataset_id,
                    filter: $filter,
                    orderBy: $order_by,
                    cursor: $cursor,
                    length: $length,
                ) {{
                    models {{
                        {Schemas.MODEL}
                    }}
                    next
                    totalCount
                }}
            }}
        """,
        "variables": get_models_params,
    }

    CREATE = {
        "name": "createModel",
        "query": f"""
            mutation createModel(
                $dataset_id: ID!,
                $name: String!,
                $description: String,
                $task_type: ModelTaskType!,
                $custom_dag_id: String,
                $total_data_count: Int,
                $train_data_count: Int,
                $validation_data_count: Int,
                $training_parameters: JSONObject,
                $train_slice_id: ID,
                $validation_slice_id: ID,
                $is_pinned: Boolean,
                $score_key: String,
                $score_value: Float,
                $score_unit: String,
            ) {{
                createModel(
                    datasetId: $dataset_id,
                    name: $name,
                    description: $description,
                    taskType: $task_type,
                    customDagId: $custom_dag_id,
                    totalDataCount: $total_data_count,
                    trainDataCount: $train_data_count,
                    validationDataCount: $validation_data_count,
                    trainingParameters: $training_parameters,
                    trainSliceId: $train_slice_id,
                    validationSliceId: $validation_slice_id,
                    isPinned: $is_pinned,
                    scoreKey: $score_key,
                    scoreValue: $score_value,
                    scoreUnit: $score_unit,
                ) {{
                    {Schemas.MODEL}
                }}
            }}
        """,
        "variables": create_model_params,
    }

    UPDATE = {
        "name": "updateModel",
        "query": f"""
            mutation updateModel(
                $dataset_id: ID!,
                $model_id: ID!,
                $name: String,
                $description: String,
                $status: ModelStatus,
                $task_type: ModelTaskType,
                $custom_dag_id: String,
                $total_data_count: Int,
                $train_data_count: Int,
                $validation_data_count: Int,
                $training_parameters: JSONObject,
                $train_slice_id: ID,
                $validation_slice_id: ID,
                $is_pinned: Boolean,
                $score_key: String,
                $score_value: Float,
                $score_unit: String,
            ) {{
                updateModel(
                    datasetId: $dataset_id,
                    modelId: $model_id,
                    name: $name,
                    description: $description,
                    status: $status,
                    taskType: $task_type,
                    customDagId: $custom_dag_id,
                    totalDataCount: $total_data_count,
                    trainDataCount: $train_data_count,
                    validationDataCount: $validation_data_count,
                    trainingParameters: $training_parameters,
                    trainSliceId: $train_slice_id,
                    validationSliceId: $validation_slice_id,
                    isPinned: $is_pinned,
                    scoreKey: $score_key,
                    scoreValue: $score_value,
                    scoreUnit: $score_unit,
                ) {{
                    {Schemas.MODEL}
                }}
            }}
        """,
        "variables": update_model_params,
    }

    DELETE = {
        "name": "deleteModel",
        "query": """
            mutation deleteModel(
                $dataset_id: ID!,
                $model_id: ID!,
            ) {
                deleteModel(
                    datasetId: $dataset_id,
                    modelId: $model_id,
                )
            }
        """,
        "variables": delete_model_params,
    }
