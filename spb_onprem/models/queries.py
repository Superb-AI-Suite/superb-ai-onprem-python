from .params import (
    get_model_params,
    get_models_params,
    create_model_params,
    update_model_params,
    delete_model_params,
    create_training_report_item_params,
    update_training_report_item_params,
    delete_training_report_item_params,
)


class Schemas:
    TRAINING_REPORT_ITEM = """
        id
        name
        type
        modelId
        contentId
        description
        createdAt
        updatedAt
        createdBy
        updatedBy
    """

    TRAINING_ANNOTATIONS = """
        trainCount
        validationCount
        className
        annotationType
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
            {TRAINING_REPORT_ITEM}
        }}
        trainingAnnotations {{
            {TRAINING_ANNOTATIONS}
        }}
        contents
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
                $contents: JSONObject,
                $training_annotations: [TrainingAnnotationsInput!],
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
                    contents: $contents,
                    trainingAnnotations: $training_annotations,
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
                $contents: JSONObject,
                $training_annotations: [TrainingAnnotationsInput!],
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
                    contents: $contents,
                    trainingAnnotations: $training_annotations,
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

    CREATE_TRAINING_REPORT = {
        "name": "createTrainingReportItem",
        "query": f"""
            mutation createTrainingReportItem(
                $dataset_id: ID!,
                $model_id: ID!,
                $name: String!,
                $type: AnalyticsReportItemType!,
                $content_id: ID,
                $description: String,
            ) {{
                createTrainingReportItem(
                    datasetId: $dataset_id,
                    modelId: $model_id,
                    name: $name,
                    type: $type,
                    contentId: $content_id,
                    description: $description,
                ) {{
                    {Schemas.MODEL}
                }}
            }}
        """,
        "variables": create_training_report_item_params,
    }

    UPDATE_TRAINING_REPORT = {
        "name": "updateTrainingReportItem",
        "query": f"""
            mutation updateTrainingReportItem(
                $dataset_id: ID!,
                $model_id: ID!,
                $training_report_id: ID!,
                $name: String,
                $type: AnalyticsReportItemType,
                $content_id: ID,
                $description: String,
            ) {{
                updateTrainingReportItem(
                    datasetId: $dataset_id,
                    modelId: $model_id,
                    trainingReportItemId: $training_report_id,
                    name: $name,
                    type: $type,
                    contentId: $content_id,
                    description: $description,
                ) {{
                    {Schemas.MODEL}
                }}
            }}
        """,
        "variables": update_training_report_item_params,
    }

    DELETE_TRAINING_REPORT = {
        "name": "deleteTrainingReportItem",
        "query": f"""
            mutation deleteTrainingReportItem(
                $dataset_id: ID!,
                $model_id: ID!,
                $training_report_id: ID!,
            ) {{
                deleteTrainingReportItem(
                    datasetId: $dataset_id,
                    modelId: $model_id,
                    trainingReportItemId: $training_report_id,
                ) {{
                    {Schemas.MODEL}
                }}
            }}
        """,
        "variables": delete_training_report_item_params,
    }

