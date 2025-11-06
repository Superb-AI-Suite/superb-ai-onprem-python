from spb_onprem.reports.params import (
    analytics_report_params,
    analytics_reports_params,
    create_analytics_report_params,
    update_analytics_report_params,
    delete_analytics_report_params,
    create_analytics_report_item_params,
    update_analytics_report_item_params,
    delete_analytics_report_item_params,
)


class Schemas:
    ANALYTICS_REPORT_ITEM = '''
        id
        type
        title
        description
        content {
            id
        }
        meta
        createdAt
        createdBy
        updatedAt
        updatedBy
    '''
    
    ANALYTICS_REPORT = '''
        datasetId
        id
        title
        description
        meta
        createdAt
        updatedAt
        createdBy
        updatedBy
        items {
            id
            type
            title
            description
            content {
                id
            }
            meta
            createdAt
            createdBy
            updatedAt
            updatedBy
        }
    '''


class Queries():
    ANALYTICS_REPORT = {
        "name": "analyticsReport",
        "query": f'''
            query AnalyticsReport(
                $reportId: ID!,
                $datasetId: String!
            ) {{
                analyticsReport(
                    reportId: $reportId,
                    datasetId: $datasetId
                ) {{
                    {Schemas.ANALYTICS_REPORT}
                }}
            }}
        ''',
        "variables": analytics_report_params,
    }
    
    ANALYTICS_REPORTS = {
        "name": "analyticsReports",
        "query": f'''
            query AnalyticsReports(
                $datasetId: ID!,
                $filter: AnalyticsReportFilter,
                $cursor: String,
                $length: Int,
                $orderBy: AnalyticsReportOrderBy
            ) {{
                analyticsReports(
                    datasetId: $datasetId,
                    filter: $filter,
                    cursor: $cursor,
                    length: $length,
                    orderBy: $orderBy
                ) {{
                    analyticsReports {{
                        {Schemas.ANALYTICS_REPORT}
                    }}
                    next
                    totalCount
                }}
            }}
        ''',
        "variables": analytics_reports_params,
    }
    
    CREATE_ANALYTICS_REPORT = {
        "name": "createAnalyticsReport",
        "query": f'''
            mutation CreateAnalyticsReport(
                $datasetId: ID!,
                $title: String,
                $description: String,
                $meta: JSONObject
            ) {{
                createAnalyticsReport(
                    datasetId: $datasetId,
                    title: $title,
                    description: $description,
                    meta: $meta
                ) {{
                    {Schemas.ANALYTICS_REPORT}
                }}
            }}
        ''',
        "variables": create_analytics_report_params,
    }
    
    UPDATE_ANALYTICS_REPORT = {
        "name": "updateAnalyticsReport",
        "query": f'''
            mutation UpdateAnalyticsReport(
                $datasetId: ID!,
                $reportId: ID!,
                $title: String,
                $description: String,
                $meta: JSONObject
            ) {{
                updateAnalyticsReport(
                    datasetId: $datasetId,
                    reportId: $reportId,
                    title: $title,
                    description: $description,
                    meta: $meta
                ) {{
                    {Schemas.ANALYTICS_REPORT}
                }}
            }}
        ''',
        "variables": update_analytics_report_params,
    }
    
    DELETE_ANALYTICS_REPORT = {
        "name": "deleteAnalyticsReport",
        "query": '''
            mutation DeleteAnalyticsReport(
                $reportId: String!,
                $datasetId: String!
            ) {
                deleteAnalyticsReport(
                    reportId: $reportId,
                    datasetId: $datasetId
                )
            }
        ''',
        "variables": delete_analytics_report_params,
    }
    
    CREATE_ANALYTICS_REPORT_ITEM = {
        "name": "createAnalyticsReportItem",
        "query": f'''
            mutation CreateAnalyticsReportItem(
                $datasetId: ID!,
                $reportId: ID!,
                $type: AnalyticsReportItemType!,
                $title: String,
                $description: String,
                $contentId: String,
                $meta: JSONObject
            ) {{
                createAnalyticsReportItem(
                    datasetId: $datasetId,
                    reportId: $reportId,
                    type: $type,
                    title: $title,
                    description: $description,
                    contentId: $contentId,
                    meta: $meta
                ) {{
                    {Schemas.ANALYTICS_REPORT_ITEM}
                }}
            }}
        ''',
        "variables": create_analytics_report_item_params,
    }
    
    UPDATE_ANALYTICS_REPORT_ITEM = {
        "name": "updateAnalyticsReportItem",
        "query": f'''
            mutation UpdateAnalyticsReportItem(
                $datasetId: ID!,
                $reportId: ID!,
                $itemId: ID!,
                $title: String,
                $description: String,
                $contentId: String,
                $meta: JSONObject
            ) {{
                updateAnalyticsReportItem(
                    datasetId: $datasetId,
                    reportId: $reportId,
                    itemId: $itemId,
                    title: $title,
                    description: $description,
                    contentId: $contentId,
                    meta: $meta
                ) {{
                    {Schemas.ANALYTICS_REPORT_ITEM}
                }}
            }}
        ''',
        "variables": update_analytics_report_item_params,
    }
    
    DELETE_ANALYTICS_REPORT_ITEM = {
        "name": "deleteAnalyticsReportItem",
        "query": '''
            mutation DeleteAnalyticsReportItem(
                $itemId: String!,
                $reportId: String!,
                $datasetId: String!
            ) {
                deleteAnalyticsReportItem(
                    itemId: $itemId,
                    reportId: $reportId,
                    datasetId: $datasetId
                )
            }
        ''',
        "variables": delete_analytics_report_item_params,
    }
