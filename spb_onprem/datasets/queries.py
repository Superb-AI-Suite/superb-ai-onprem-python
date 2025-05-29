from spb_onprem.datasets.params import (
    dataset_params,
    datasets_params,
    create_dataset_params,
    update_dataset_params,
)

class Schemas:
    DATASET = '''
        id
        name
        description
        createdAt
        createdBy
        updatedAt
        updatedBy
    '''


class Queries():
    DATASET = {
        "name": "dataset",
        "query": f'''
            query Dataset(
                $name: String,
                $datasetId: ID
            ) {{
                dataset(
                    name: $name,
                    datasetId: $datasetId
                ) {{
                    {Schemas.DATASET}
                }}
            }}
        ''',
        "variables": dataset_params,
    }
    
    DATASETS = {
        "name": "datasets",
        "query": f'''
            query Datasets(
                $name: String,
                $datasetId: ID
            ) {{
                datasets(
                    name: $name,
                    id: $datasetId
                ) {{
                    {Schemas.DATASET}
                }}
            }}
        ''',
        "variables": datasets_params,
    }
    
    CREATE_DATASET = {
        "name": "createDataset",
        "query": f'''
        mutation CreateDataset($name: String!, $description: String) {{
            createDataset(name: $name, description: $description) {{
                {Schemas.DATASET}
            }}
        }}
        ''',
        "variables": create_dataset_params,
    }

    UPDATE_DATASET = {
        "name": "updateDataset",
        "query": f'''
            mutation UpdateDataset($updateDatasetId: ID!, $name: String, $description: String) {{
                updateDataset(id: $updateDatasetId, name: $name, description: $description) {{
                    {Schemas.DATASET}
                }}
            }}
        ''',
        "variables": update_dataset_params,
    }
