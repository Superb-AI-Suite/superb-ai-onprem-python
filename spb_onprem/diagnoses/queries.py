from .params import (
    get_diagnosis_params,
    get_diagnoses_params,
    create_diagnosis_params,
    update_diagnosis_params,
    delete_diagnosis_params,
    create_diagnosis_report_item_params,
    update_diagnosis_report_item_params,
    delete_diagnosis_report_item_params,
)


class Schemas:
    DIAGNOSIS_REPORT_ITEM = """
        id
        diagnosisId
        name
        type
        contentId
        description
        createdAt
        updatedAt
        createdBy
        updatedBy
    """

    DIAGNOSIS = f"""
        datasetId
        id
        name
        description
        status
        scoreKey
        scoreValue
        scoreUnit
        diagnosisParameters
        diagnosisReportItems {{
            {DIAGNOSIS_REPORT_ITEM}
        }}
        completedAt
        createdAt
        updatedAt
        createdBy
        updatedBy
    """


class Queries:
    GET = {
        "name": "diagnosis",
        "query": f"""
            query Query(
                $dataset_id: ID!,
                $diagnosis_id: ID,
                $name: String,
            ) {{
                diagnosis(
                    datasetId: $dataset_id,
                    diagnosisId: $diagnosis_id,
                    name: $name,
                ) {{
                    {Schemas.DIAGNOSIS}
                }}
            }}
        """,
        "variables": get_diagnosis_params,
    }

    GET_LIST = {
        "name": "diagnoses",
        "query": f"""
            query Query(
                $dataset_id: ID!,
                $filter: DiagnosisFilter,
                $order_by: DiagnosisOrderBy,
                $cursor: String,
                $length: Int,
            ) {{
                diagnoses(
                    datasetId: $dataset_id,
                    filter: $filter,
                    orderBy: $order_by,
                    cursor: $cursor,
                    length: $length,
                ) {{
                    diagnoses {{
                        {Schemas.DIAGNOSIS}
                    }}
                    next
                    totalCount
                }}
            }}
        """,
        "variables": get_diagnoses_params,
    }

    CREATE = {
        "name": "createDiagnosis",
        "query": f"""
            mutation createDiagnosis(
                $dataset_id: ID!,
                $name: String!,
                $description: String,
                $score_key: String,
                $score_value: Float,
                $score_unit: String,
                $diagnosis_parameters: JSONObject,
            ) {{
                createDiagnosis(
                    datasetId: $dataset_id,
                    name: $name,
                    description: $description,
                    scoreKey: $score_key,
                    scoreValue: $score_value,
                    scoreUnit: $score_unit,
                    diagnosisParameters: $diagnosis_parameters,
                ) {{
                    {Schemas.DIAGNOSIS}
                }}
            }}
        """,
        "variables": create_diagnosis_params,
    }

    UPDATE = {
        "name": "updateDiagnosis",
        "query": f"""
            mutation updateDiagnosis(
                $dataset_id: ID!,
                $diagnosis_id: ID!,
                $name: String,
                $description: String,
                $status: DiagnosisStatus,
                $score_key: String,
                $score_value: Float,
                $score_unit: String,
                $diagnosis_parameters: JSONObject,
            ) {{
                updateDiagnosis(
                    datasetId: $dataset_id,
                    diagnosisId: $diagnosis_id,
                    name: $name,
                    description: $description,
                    status: $status,
                    scoreKey: $score_key,
                    scoreValue: $score_value,
                    scoreUnit: $score_unit,
                    diagnosisParameters: $diagnosis_parameters,
                ) {{
                    {Schemas.DIAGNOSIS}
                }}
            }}
        """,
        "variables": update_diagnosis_params,
    }

    DELETE = {
        "name": "deleteDiagnosis",
        "query": """
            mutation deleteDiagnosis(
                $dataset_id: ID!,
                $diagnosis_id: ID!,
            ) {
                deleteDiagnosis(
                    datasetId: $dataset_id,
                    diagnosisId: $diagnosis_id,
                )
            }
        """,
        "variables": delete_diagnosis_params,
    }

    CREATE_REPORT_ITEM = {
        "name": "createDiagnosisReportItem",
        "query": f"""
            mutation createDiagnosisReportItem(
                $dataset_id: ID!,
                $diagnosis_id: ID!,
                $name: String!,
                $type: DiagnosisReportItemType!,
                $content_id: ID,
                $description: String,
            ) {{
                createDiagnosisReportItem(
                    datasetId: $dataset_id,
                    diagnosisId: $diagnosis_id,
                    name: $name,
                    type: $type,
                    contentId: $content_id,
                    description: $description,
                ) {{
                    {Schemas.DIAGNOSIS}
                }}
            }}
        """,
        "variables": create_diagnosis_report_item_params,
    }

    UPDATE_REPORT_ITEM = {
        "name": "updateDiagnosisReportItem",
        "query": f"""
            mutation updateDiagnosisReportItem(
                $dataset_id: ID!,
                $diagnosis_id: ID!,
                $diagnosis_report_item_id: ID!,
                $name: String,
                $type: DiagnosisReportItemType,
                $content_id: ID,
                $description: String,
            ) {{
                updateDiagnosisReportItem(
                    datasetId: $dataset_id,
                    diagnosisId: $diagnosis_id,
                    diagnosisReportItemId: $diagnosis_report_item_id,
                    name: $name,
                    type: $type,
                    contentId: $content_id,
                    description: $description,
                ) {{
                    {Schemas.DIAGNOSIS}
                }}
            }}
        """,
        "variables": update_diagnosis_report_item_params,
    }

    DELETE_REPORT_ITEM = {
        "name": "deleteDiagnosisReportItem",
        "query": f"""
            mutation deleteDiagnosisReportItem(
                $dataset_id: ID!,
                $diagnosis_id: ID!,
                $diagnosis_report_item_id: ID!,
            ) {{
                deleteDiagnosisReportItem(
                    datasetId: $dataset_id,
                    diagnosisId: $diagnosis_id,
                    diagnosisReportItemId: $diagnosis_report_item_id,
                ) {{
                    {Schemas.DIAGNOSIS}
                }}
            }}
        """,
        "variables": delete_diagnosis_report_item_params,
    }
