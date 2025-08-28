from spb_onprem.slices.params import (
    slices_params,
    slice_params,
    create_slice_params,
    update_slice_params,
    delete_slice_params,
)


class Schemas:
    """Schemas for slices queries
    """
    SLICE_PAGE= '''
        slices {
            id
            name
        }
        next
        totalCount
    '''
    
    SLICE = '''
        id
        datasetId
        name
        description
        isPinned
        createdAt
        createdBy
        updatedAt
        updatedBy
    '''


class Queries:
    '''
    Queries for slices
    '''

    GET_SLICES = {
        "name": "slices",
        "query": f'''
            query slices(
                $dataset_id: String!,
                $filter: SliceFilter,
                $cursor: String,
                $length: Int
            ) {{
                slices(
                    datasetId: $dataset_id,
                    filter: $filter,
                    cursor: $cursor,
                    length: $length
                ) {{
                    {Schemas.SLICE_PAGE}
                }}
            }}
        ''',
        "variables": slices_params,
    }
    
    GET_SLICE = {
        "name": "slice",
        "query": f'''
            query slice(
                $dataset_id: String!,
                $id: ID
                $name: String
            ) {{
                slice(
                    datasetId: $dataset_id,
                    id: $id
                    name: $name
                ) {{
                    {Schemas.SLICE}
                }}
            }}
        ''',
        "variables": slice_params,
    }
    
    CREATE_SLICE = {
        "name": "createSlice",
        "query": f'''
            mutation createSlice(
                $dataset_id: String!,
                $name: String!,
                $description: String
            ) {{
                createSlice(
                    datasetId: $dataset_id,
                    name: $name,
                    description: $description
                ) {{
                    {Schemas.SLICE}
                }}
            }}
        ''',
        "variables": create_slice_params,
    }
    
    UPDATE_SLICE = {
        "name": "updateSlice",
        "query": f'''
            mutation updateSlice(
                $dataset_id: String!,
                $id: ID!,
                $name: String,
                $description: String
            ) {{
                updateSlice(
                    datasetId: $dataset_id,
                    id: $id,
                    name: $name,
                    description: $description
                ) {{
                    {Schemas.SLICE}
                }}
            }}
        ''',
        "variables": update_slice_params,
    }

    DELETE_SLICE = {
        "name": "deleteSlice",
        "query": '''
            mutation deleteSlice(
                $dataset_id: String!,
                $id: ID!
            ) {
                deleteSlice(datasetId: $dataset_id, id: $id)
            }
        ''',
        "variables": delete_slice_params,
    }
