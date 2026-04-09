class Schemas:
    WORKFLOW_BINDING_CONFIG = """
        type
        path
        nodeKey
        value
    """

    WORKFLOW_NODE_DEFINITION = """
        key
        nodeType
        jobType
        bindings
        requiredOutputs
        nextNodeKey
    """

    WORKFLOW_NODE_EXECUTION = """
        id
        workflowRunId
        nodeKey
        nodeType
        jobType
        sequenceNo
        status
        jobHistoryId
        inputSnapshot
        outputSnapshot
        errorReason
        startedAt
        completedAt
        createdAt
        updatedAt
    """

    WORKFLOW_DEFINITION = f"""
        id
        key
        name
        description
        version
        status
        startNodeKey
        triggerSchema
        nodes {{
            {WORKFLOW_NODE_DEFINITION}
        }}
        createdAt
        createdBy
        updatedAt
        updatedBy
    """

    WORKFLOW_RUN = f"""
        id
        workflowDefinitionId
        workflowKey
        workflowVersion
        status
        triggerInput
        datasetId
        startedBy
        currentNodeKey
        lastNodeExecutionId
        stopReason
        nodeExecutions {{
            {WORKFLOW_NODE_EXECUTION}
        }}
        startedAt
        completedAt
        createdAt
        updatedAt
    """


class Queries:
    """Workflow GraphQL operation placeholders.

    Sunrise workflow API contract is still being fixed in the parallel backend branch.
    Day 1 keeps the reusable field selections here so Day 2 can attach concrete
    query/mutation strings without reshaping the SDK module again.
    """

