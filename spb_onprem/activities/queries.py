from spb_onprem.activities.params import (
    get_activities_params,
    get_activity_params,

    create_activity_params,
    update_activity_params,
    delete_activity_params,

    start_activity_params,
    update_activity_history_params,
    get_activity_history_params,
    get_activity_history_task_detail_params,
    get_activity_history_task_log_download_params,
    get_activity_history_task_log_params,
    get_activity_history_task_monitoring_params,
    get_activity_history_task_rendered_templates_params,
)

class Schemas:
    """Schemas for activities queries
    """
    ACTIVITY = '''
        id
        name
        description
        type
        datasetId
        progressSchema {
            key
            type
            required
            default
        }
        parameterSchema {
            key
            type
            required
            default
        }
        settings
        meta
        createdAt
        createdBy
        updatedAt
        updatedBy
    '''
    ACTIVITY_HISTORY = '''
        id
        jobId
        status
        datasetId
        parameters
        progress
        createdAt
        createdBy
        updatedAt
        updatedBy
        meta
    '''

    TASK_MONITORING = '''
        runType
        runId
        available
        runState
        rawRunState
        linkedRun {
            runType
            runId
        }
        nodes {
            id
            taskId
            label
            kind
            state
            instanceCount
            instances {
                id
                taskId
                label
                kind
                state
                rawState
                durationSeconds
                startedAt
                endedAt
                attempt
                taskRunIndex
            }
        }
        edges {
            id
            source
            target
        }
    '''

    TASK_DETAIL = '''
        availability
        taskId
        taskRunIndex
        label
        state
        rawState
        operator
        triggerRule
        startedAt
        endedAt
        durationSeconds
        attempt
        maxAttempts
        runtime {
            executor
            queue
            pool
            poolSlots
            hostname
            unixname
            pid
            priorityWeight
            queuedAt
            scheduledAt
            externalExecutorId
            kubernetes {
                podName
                namespace
                image
                containerName
                nodeName
                podPhase
            }
        }
    '''

    TASK_RENDERED_TEMPLATES = '''
        availability
        taskId
        taskRunIndex
        sections {
            key
            value
            valueType
        }
    '''

    TASK_LOG_CHUNK = '''
        availability
        taskId
        taskRunIndex
        attempt
        content
        nextCursor
        hasMore
        isComplete
        metadata {
            lineCount
            sizeBytes
            startedAt
            endedAt
        }
    '''

    TASK_LOG_DOWNLOAD = '''
        availability
        taskId
        taskRunIndex
        attempt
        content
        downloadFilename
        lineCount
        isTail
    '''

    ACTIVITY_PAGE = f'''
        jobs {{
            {ACTIVITY}
        }}
        next
        totalCount
    '''


class Queries:
    '''
    Queries for activities
    '''

    GET_ACTIVITIES = {
        "name": "jobs",
        "query": f'''
            query jobs(
                $filter: JobFilter,
                $cursor: String,
                $length: Int
                $orderBy: JobOrderBy
            ) {{
                jobs(
                    filter: $filter,
                    cursor: $cursor,
                    length: $length,
                    orderBy: $orderBy
                ) {{
                    {Schemas.ACTIVITY_PAGE}
                }}
            }}
        ''',
        "variables": get_activities_params,
    }

    GET_ACTIVITY = {
        "name": "job",
        "query": f'''
            query job(
                $name: String,
                $id: ID
            ) {{
                job(name: $name, id: $id) {{
                    {Schemas.ACTIVITY}
                }}
            }}
        ''',
        "variables": get_activity_params,
    }

    GET_ACTIVITY_HISTORY = {
        "name": "jobHistory",
        "query": f'''
            query jobHistory(
                $dataset_id: ID,
                $job_history_id: ID!
            ) {{
                jobHistory(datasetId: $dataset_id, id: $job_history_id) {{
                    {Schemas.ACTIVITY_HISTORY}
                }}
            }}
        ''',
        "variables": get_activity_history_params,
    }

    GET_ACTIVITY_HISTORY_TASK_MONITORING = {
        "name": "jobHistoryTaskMonitoring",
        "query": f'''
            query jobHistoryTaskMonitoring(
                $input: JobHistoryTaskMonitoringInput!
            ) {{
                jobHistoryTaskMonitoring(input: $input) {{
                    {Schemas.TASK_MONITORING}
                }}
            }}
        ''',
        "variables": get_activity_history_task_monitoring_params,
    }

    GET_ACTIVITY_HISTORY_TASK_DETAIL = {
        "name": "jobHistoryTaskDetail",
        "query": f'''
            query jobHistoryTaskDetail(
                $input: JobHistoryTaskDetailInput!
            ) {{
                jobHistoryTaskDetail(input: $input) {{
                    {Schemas.TASK_DETAIL}
                }}
            }}
        ''',
        "variables": get_activity_history_task_detail_params,
    }

    GET_ACTIVITY_HISTORY_TASK_RENDERED_TEMPLATES = {
        "name": "jobHistoryTaskRenderedTemplates",
        "query": f'''
            query jobHistoryTaskRenderedTemplates(
                $input: JobHistoryTaskRenderedTemplatesInput!
            ) {{
                jobHistoryTaskRenderedTemplates(input: $input) {{
                    {Schemas.TASK_RENDERED_TEMPLATES}
                }}
            }}
        ''',
        "variables": get_activity_history_task_rendered_templates_params,
    }

    GET_ACTIVITY_HISTORY_TASK_LOG = {
        "name": "jobHistoryTaskLog",
        "query": f'''
            query jobHistoryTaskLog(
                $input: JobHistoryTaskLogInput!
            ) {{
                jobHistoryTaskLog(input: $input) {{
                    {Schemas.TASK_LOG_CHUNK}
                }}
            }}
        ''',
        "variables": get_activity_history_task_log_params,
    }

    GET_ACTIVITY_HISTORY_TASK_LOG_DOWNLOAD = {
        "name": "jobHistoryTaskLogDownload",
        "query": f'''
            query jobHistoryTaskLogDownload(
                $input: JobHistoryTaskLogDownloadInput!
            ) {{
                jobHistoryTaskLogDownload(input: $input) {{
                    {Schemas.TASK_LOG_DOWNLOAD}
                }}
            }}
        ''',
        "variables": get_activity_history_task_log_download_params,
    }

    CREATE_ACTIVITY = {
        "name": "createJob",
        "query": f'''
            mutation createJob(
                $datasetId: ID,
                $type: String!,
                $name: String!,
                $description: String,
                
                $progressSchema: [JobProgressSchemaInput!],
                $parameterSchema: [JobParameterSchemaInput!],
                $settings: JSONObject,
                $meta: JSONObject
            ) {{
                createJob(
                    datasetId: $datasetId,
                    type: $type,
                    name: $name,
                    description: $description,
                    progressSchema: $progressSchema,
                    parameterSchema: $parameterSchema,
                    settings: $settings,
                    meta: $meta
                ) {{
                    {Schemas.ACTIVITY}
                }}
            }}
        ''',
        "variables": create_activity_params,
    }

    UPDATE_ACTIVITY = {
        "name": "updateJob",
        "query": f'''
            mutation updateJob(
                $id: ID!,
                $type: String,
                $name: String,
                $description: String,
                $progressSchema: [JobProgressSchemaInput!],
                $parameterSchema: [JobParameterSchemaInput!],
                $settings: JSONObject,
                $meta: JSONObject
            ) {{
                updateJob(
                    id: $id,
                    type: $type,
                    name: $name,
                    description: $description,
                    progressSchema: $progressSchema,
                    parameterSchema: $parameterSchema,
                    settings: $settings,
                    meta: $meta
                ) {{
                    {Schemas.ACTIVITY}
                }}
            }}
        ''',
        "variables": update_activity_params,
    }

    DELETE_ACTIVITY = {
        "name": "deleteJob",
        "query": '''
            mutation deleteJob(
                $id: ID!
            ) {
                deleteJob(id: $id)
            }
        ''',
        "variables": delete_activity_params,
    }

    START_ACTIVITY = {
        "name": "startJob",
        "query": f'''
            mutation startJob(
                $id: ID,
                $jobType: String,

                $datasetId: ID,
                $parameters: JSONObject,
                $progress: JSONObject,
                $meta: JSONObject
            ) {{
                startJob(
                    id: $id,
                    jobType: $jobType,
                    datasetId: $datasetId,
                    parameters: $parameters,
                    progress: $progress,
                    meta: $meta
                ) {{
                    {Schemas.ACTIVITY_HISTORY}
                }}
            }}
        ''',
        "variables": start_activity_params,
    }

    UPDATE_ACTIVITY_HISTORY = {
        "name": "updateJobHistory",
        "query": f'''
            mutation updateJobHistory(
                $id: ID!,
                $status: JobStatus,
                $progress: JSONObject,
                $meta: JSONObject
            ) {{
                updateJobHistory(
                    id: $id,
                    status: $status,
                    progress: $progress,
                    meta: $meta
                ) {{
                    {Schemas.ACTIVITY_HISTORY}
                }}
            }}
        ''',
        "variables": update_activity_history_params,
    }
