from .params import (
    create_dataset_vlm_settings_params,
    create_slice_vlm_settings_params,
    dataset_vlm_settings_params,
    delete_dataset_vlm_settings_params,
    delete_slice_vlm_settings_params,
    slice_vlm_settings_params,
    update_dataset_vlm_settings_params,
    update_slice_vlm_settings_params,
)


class Schemas:
    DATASET_VLM_SETTINGS = '''
        datasetId
        settings
        createdAt
        createdBy
        updatedAt
        updatedBy
    '''

    SLICE_VLM_SETTINGS = '''
        datasetId
        sliceId
        settings
        createdAt
        createdBy
        updatedAt
        updatedBy
    '''


class Queries:
    GET_DATASET_VLM_SETTINGS = {
        "name": "datasetVLMSettings",
        "query": f'''
            query DatasetVLMSettings($datasetId: ID!) {{
                datasetVLMSettings(datasetId: $datasetId) {{
                    {Schemas.DATASET_VLM_SETTINGS}
                }}
            }}
        ''',
        "variables": dataset_vlm_settings_params,
    }

    CREATE_DATASET_VLM_SETTINGS = {
        "name": "createDatasetVLMSettings",
        "query": f'''
            mutation CreateDatasetVLMSettings($datasetId: ID!, $settings: JSONObject!) {{
                createDatasetVLMSettings(datasetId: $datasetId, settings: $settings) {{
                    {Schemas.DATASET_VLM_SETTINGS}
                }}
            }}
        ''',
        "variables": create_dataset_vlm_settings_params,
    }

    UPDATE_DATASET_VLM_SETTINGS = {
        "name": "updateDatasetVLMSettings",
        "query": f'''
            mutation UpdateDatasetVLMSettings(
                $datasetId: ID!,
                $settings: JSONObject!,
                $expectedUpdatedAt: DateTime
            ) {{
                updateDatasetVLMSettings(
                    datasetId: $datasetId,
                    settings: $settings,
                    expectedUpdatedAt: $expectedUpdatedAt
                ) {{
                    {Schemas.DATASET_VLM_SETTINGS}
                }}
            }}
        ''',
        "variables": update_dataset_vlm_settings_params,
    }

    DELETE_DATASET_VLM_SETTINGS = {
        "name": "deleteDatasetVLMSettings",
        "query": '''
            mutation DeleteDatasetVLMSettings($datasetId: ID!, $expectedUpdatedAt: DateTime) {
                deleteDatasetVLMSettings(datasetId: $datasetId, expectedUpdatedAt: $expectedUpdatedAt)
            }
        ''',
        "variables": delete_dataset_vlm_settings_params,
    }

    GET_SLICE_VLM_SETTINGS = {
        "name": "sliceVLMSettings",
        "query": f'''
            query SliceVLMSettings($datasetId: ID!, $sliceId: ID!) {{
                sliceVLMSettings(datasetId: $datasetId, sliceId: $sliceId) {{
                    {Schemas.SLICE_VLM_SETTINGS}
                }}
            }}
        ''',
        "variables": slice_vlm_settings_params,
    }

    CREATE_SLICE_VLM_SETTINGS = {
        "name": "createSliceVLMSettings",
        "query": f'''
            mutation CreateSliceVLMSettings($datasetId: ID!, $sliceId: ID!, $settings: JSONObject!) {{
                createSliceVLMSettings(datasetId: $datasetId, sliceId: $sliceId, settings: $settings) {{
                    {Schemas.SLICE_VLM_SETTINGS}
                }}
            }}
        ''',
        "variables": create_slice_vlm_settings_params,
    }

    UPDATE_SLICE_VLM_SETTINGS = {
        "name": "updateSliceVLMSettings",
        "query": f'''
            mutation UpdateSliceVLMSettings(
                $datasetId: ID!,
                $sliceId: ID!,
                $settings: JSONObject!,
                $expectedUpdatedAt: DateTime
            ) {{
                updateSliceVLMSettings(
                    datasetId: $datasetId,
                    sliceId: $sliceId,
                    settings: $settings,
                    expectedUpdatedAt: $expectedUpdatedAt
                ) {{
                    {Schemas.SLICE_VLM_SETTINGS}
                }}
            }}
        ''',
        "variables": update_slice_vlm_settings_params,
    }

    DELETE_SLICE_VLM_SETTINGS = {
        "name": "deleteSliceVLMSettings",
        "query": '''
            mutation DeleteSliceVLMSettings($datasetId: ID!, $sliceId: ID!, $expectedUpdatedAt: DateTime) {
                deleteSliceVLMSettings(
                    datasetId: $datasetId,
                    sliceId: $sliceId,
                    expectedUpdatedAt: $expectedUpdatedAt
                )
            }
        ''',
        "variables": delete_slice_vlm_settings_params,
    }
