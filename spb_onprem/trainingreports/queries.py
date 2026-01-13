from spb_onprem.models.queries import Schemas as ModelSchemas

from .params import (
    create_training_report_params,
    update_training_report_params,
    delete_training_report_params,
)


class Queries:
    CREATE = {
        "name": "createTrainingReport",
        "query": f"""
            mutation createTrainingReport(
                $dataset_id: ID!,
                $model_id: ID!,
                $name: String!,
                $content_id: ID!,
                $description: String,
            ) {{
                createTrainingReport(
                    datasetId: $dataset_id,
                    modelId: $model_id,
                    name: $name,
                    contentId: $content_id,
                    description: $description,
                ) {{
                    {ModelSchemas.MODEL}
                }}
            }}
        """,
        "variables": create_training_report_params,
    }

    UPDATE = {
        "name": "updateTrainingReport",
        "query": f"""
            mutation updateTrainingReport(
                $dataset_id: ID!,
                $model_id: ID!,
                $training_report_id: ID!,
                $name: String,
                $content_id: ID,
                $description: String,
            ) {{
                updateTrainingReport(
                    datasetId: $dataset_id,
                    modelId: $model_id,
                    trainingReportId: $training_report_id,
                    name: $name,
                    contentId: $content_id,
                    description: $description,
                ) {{
                    {ModelSchemas.MODEL}
                }}
            }}
        """,
        "variables": update_training_report_params,
    }

    DELETE = {
        "name": "deleteTrainingReport",
        "query": f"""
            mutation deleteTrainingReport(
                $dataset_id: ID!,
                $model_id: ID!,
                $training_report_id: ID!,
            ) {{
                deleteTrainingReport(
                    datasetId: $dataset_id,
                    modelId: $model_id,
                    trainingReportId: $training_report_id,
                ) {{
                    {ModelSchemas.MODEL}
                }}
            }}
        """,
        "variables": delete_training_report_params,
    }
