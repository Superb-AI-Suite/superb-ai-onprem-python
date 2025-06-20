from spb_onprem.exports.params import (
    get_exports_params,
    get_export_params,
    create_export_params,
    delete_export_params,
    update_export_params,
)


class Schemas:
    """Schemas for exports queries
    """
    EXPORT = '''
        id
        datasetId
        name
        dataFilter
        location
        dataCount
        annotationCount
        frameCount
        meta
        createdAt
        createdBy
        updatedAt
        updatedBy
        completedAt
    '''

    EXPORT_PAGE = f'''
        exports {{
            {EXPORT}
        }}
        next
        totalCount
    '''


class Queries:
    '''
    Queries for exports
    '''

    GET_EXPORTS = {
        "name": "exports",
        "query": f'''
            query exports(
                $dataset_id: ID!,
                $filter: ExportFilter,
                $cursor: String,
                $length: Int
                $orderBy: ExportOrderBy
            ) {{
                exports(
                    datasetId: $dataset_id,
                    filter: $filter,
                    cursor: $cursor,
                    length: $length,
                    orderBy: $orderBy
                ) {{
                    {Schemas.EXPORT_PAGE}
                }}
            }}
        ''',
        "variables": get_exports_params
    }

    GET_EXPORT = {
        "name": "export",
        "query": f'''
            query export(
                $dataset_id: ID!,
                $export_id: ID!
            ) {{
                export(datasetId: $dataset_id, id: $export_id) {{
                    {Schemas.EXPORT}
                }}
            }}
        ''',
        "variables": get_export_params
    }

    CREATE_EXPORT = {
        "name": "createExport",
        "query": f'''
            mutation createExport(
                $dataset_id: ID!,
                $location: String,
                $name: String,
                $data_filter: JSONObject,
                $data_count: Int,
                $frame_count: Int,
                $annotation_count: Int,
                $meta: JSONObject
            ) {{
                createExport(
                    datasetId: $dataset_id,
                    location: $location,
                    name: $name,
                    dataFilter: $data_filter,
                    dataCount: $data_count,
                    frameCount: $frame_count,
                    annotationCount: $annotation_count,
                    meta: $meta
                ) {{
                    {Schemas.EXPORT}
                }}
            }}
        ''',
        "variables": create_export_params
    }
    
    UPDATE_EXPORT = {
        "name": "updateExport",
        "query": f'''
            mutation updateExport(
                $dataset_id: ID!,
                $export_id: ID!,
                $location: String,
                $name: String,
                $data_filter: JSONObject,
                $data_count: Int,
                $frame_count: Int,
                $annotation_count: Int,
                $meta: JSONObject,
                $completed_at: DateTime
            ) {{
                updateExport(
                    datasetId: $dataset_id,
                    id: $export_id,
                    location: $location,
                    name: $name,
                    dataFilter: $data_filter,
                    dataCount: $data_count,
                    frameCount: $frame_count,
                    annotationCount: $annotation_count,
                    meta: $meta,
                    completedAt: $completed_at
                ) {{    
                    {Schemas.EXPORT}
                }}
            }}
        ''',
        "variables": update_export_params
    }

    DELETE_EXPORT = {
        "name": "deleteExport",
        "query": '''
            mutation deleteExport(
                $dataset_id: ID!,
                $export_id: ID!
            ) {
                deleteExport(datasetId: $dataset_id, id: $export_id)
            }
        ''',
        "variables": delete_export_params
    }
