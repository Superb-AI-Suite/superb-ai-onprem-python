from spb_onprem.models.queries import Schemas as ModelSchemas

from .params import (
    create_model_deploy_definition_params,
    create_model_deployment_params,
    model_deploy_definition_params,
    model_deploy_definitions_params,
    model_deployment_params,
    model_deployments_params,
    set_model_deploy_definition_pinned_params,
    set_model_deployment_pinned_params,
    start_model_deployment_params,
    unbind_model_deploy_definition_params,
    update_model_deployment_params,
)


class Schemas:
    RUNTIME = '''
        deploymentId
        generation
        namespace
        resourceName
        resourceUid
        image
        startScript
        gpuTypes
        gpuCount
        deployActivityHistoryId
        cleanupActivityHistoryId
        requestedAt
        registeredAt
        readyAt
        removedAt
        endStatus
        failureReason
    '''

    # Lists leave out ``runtime``: the platform loads it once per deployment.
    DEPLOYMENT = '''
        id
        datasetId
        definitionId
        modelId
        name
        description
        status
        lastHeartbeatAt
        expiresAt
        gpuTypes
        gpuCount
        isPinned
        startedAt
        invokeTimeoutSeconds
        createdAt
        createdBy
        updatedAt
        updatedBy
    '''

    DEPLOYMENT_WITH_RUNTIME = f'''
        {DEPLOYMENT}
        runtime {{
            {RUNTIME}
        }}
    '''

    DEFINITION = '''
        id
        name
        description
        datasetId
        isSystem
        isPinned
        serverImageName
        serverImageTag
        startScript
        createdAt
        createdBy
        updatedAt
        updatedBy
    '''

    # ``definitionId`` is selected only here, so model queries keep working on
    # platforms without deployment definitions.
    MODEL_WITH_DEFINITION = f'''
        {ModelSchemas.MODEL}
        definitionId
    '''


class Queries:
    # Deployments ------------------------------------------------------------
    GET_MODEL_DEPLOYMENT = {
        "name": "modelDeployment",
        "query": f'''
            query ModelDeployment($datasetId: ID!, $deploymentId: ID!) {{
                modelDeployment(datasetId: $datasetId, deploymentId: $deploymentId) {{
                    {Schemas.DEPLOYMENT_WITH_RUNTIME}
                }}
            }}
        ''',
        "variables": model_deployment_params,
    }

    GET_MODEL_DEPLOYMENTS = {
        "name": "modelDeployments",
        "query": f'''
            query ModelDeployments(
                $datasetId: ID!,
                $filter: ModelDeploymentFilter,
                $orderBy: ModelDeploymentOrder,
                $cursor: String,
                $length: Int
            ) {{
                modelDeployments(
                    datasetId: $datasetId,
                    filter: $filter,
                    orderBy: $orderBy,
                    cursor: $cursor,
                    length: $length
                ) {{
                    modelDeployments {{
                        {Schemas.DEPLOYMENT}
                    }}
                    next
                    totalCount
                }}
            }}
        ''',
        "variables": model_deployments_params,
    }

    GET_MODEL_DEPLOYMENT_RUNTIMES = {
        "name": "modelDeploymentRuntimes",
        "query": f'''
            query ModelDeploymentRuntimes($datasetId: ID!, $deploymentId: ID!) {{
                modelDeploymentRuntimes(datasetId: $datasetId, deploymentId: $deploymentId) {{
                    {Schemas.RUNTIME}
                }}
            }}
        ''',
        "variables": model_deployment_params,
    }

    CREATE_MODEL_DEPLOYMENT = {
        "name": "createModelDeployment",
        "query": f'''
            mutation CreateModelDeployment(
                $datasetId: ID!,
                $definitionId: ID!,
                $modelId: ID,
                $name: String!,
                $description: String,
                $expiresAt: DateTime,
                $gpuTypes: [String!],
                $gpuCount: Int,
                $invokeTimeoutSeconds: Int,
                $bindModelToDefinition: Boolean
            ) {{
                createModelDeployment(
                    datasetId: $datasetId,
                    definitionId: $definitionId,
                    modelId: $modelId,
                    name: $name,
                    description: $description,
                    expiresAt: $expiresAt,
                    gpuTypes: $gpuTypes,
                    gpuCount: $gpuCount,
                    invokeTimeoutSeconds: $invokeTimeoutSeconds,
                    bindModelToDefinition: $bindModelToDefinition
                ) {{
                    {Schemas.DEPLOYMENT_WITH_RUNTIME}
                }}
            }}
        ''',
        "variables": create_model_deployment_params,
    }

    UPDATE_MODEL_DEPLOYMENT = {
        "name": "updateModelDeployment",
        "query": f'''
            mutation UpdateModelDeployment(
                $datasetId: ID!,
                $deploymentId: ID!,
                $name: String,
                $description: String,
                $invokeTimeoutSeconds: Int
            ) {{
                updateModelDeployment(
                    datasetId: $datasetId,
                    deploymentId: $deploymentId,
                    name: $name,
                    description: $description,
                    invokeTimeoutSeconds: $invokeTimeoutSeconds
                ) {{
                    {Schemas.DEPLOYMENT_WITH_RUNTIME}
                }}
            }}
        ''',
        "variables": update_model_deployment_params,
    }

    STOP_MODEL_DEPLOYMENT = {
        "name": "stopModelDeployment",
        "query": f'''
            mutation StopModelDeployment($datasetId: ID!, $deploymentId: ID!) {{
                stopModelDeployment(datasetId: $datasetId, deploymentId: $deploymentId) {{
                    {Schemas.DEPLOYMENT_WITH_RUNTIME}
                }}
            }}
        ''',
        "variables": model_deployment_params,
    }

    START_MODEL_DEPLOYMENT = {
        "name": "startModelDeployment",
        "query": f'''
            mutation StartModelDeployment($datasetId: ID!, $deploymentId: ID!, $expiresAt: DateTime) {{
                startModelDeployment(datasetId: $datasetId, deploymentId: $deploymentId, expiresAt: $expiresAt) {{
                    {Schemas.DEPLOYMENT_WITH_RUNTIME}
                }}
            }}
        ''',
        "variables": start_model_deployment_params,
    }

    SET_MODEL_DEPLOYMENT_PINNED = {
        "name": "setModelDeploymentPinned",
        "query": f'''
            mutation SetModelDeploymentPinned($datasetId: ID!, $deploymentId: ID!, $isPinned: Boolean!) {{
                setModelDeploymentPinned(datasetId: $datasetId, deploymentId: $deploymentId, isPinned: $isPinned) {{
                    {Schemas.DEPLOYMENT}
                }}
            }}
        ''',
        "variables": set_model_deployment_pinned_params,
    }

    # Deployment definitions --------------------------------------------------------
    GET_MODEL_DEPLOY_DEFINITIONS = {
        "name": "modelDeployDefinitions",
        "query": f'''
            query ModelDeployDefinitions($datasetId: ID!) {{
                modelDeployDefinitions(datasetId: $datasetId) {{
                    {Schemas.DEFINITION}
                }}
            }}
        ''',
        "variables": model_deploy_definitions_params,
    }

    GET_MODEL_DEPLOY_DEFINITION = {
        "name": "modelDeployDefinition",
        "query": f'''
            query ModelDeployDefinition($datasetId: ID!, $definitionId: ID!) {{
                modelDeployDefinition(datasetId: $datasetId, definitionId: $definitionId) {{
                    {Schemas.DEFINITION}
                }}
            }}
        ''',
        "variables": model_deploy_definition_params,
    }

    GET_MODEL_DEPLOY_DEFINITION_USAGE = {
        "name": "modelDeployDefinitionUsage",
        "query": '''
            query ModelDeployDefinitionUsage($datasetId: ID!, $definitionId: ID!) {
                modelDeployDefinitionUsage(datasetId: $datasetId, definitionId: $definitionId) {
                    deploymentCount
                    modelCount
                }
            }
        ''',
        "variables": model_deploy_definition_params,
    }

    CREATE_MODEL_DEPLOY_DEFINITION = {
        "name": "createModelDeployDefinition",
        "query": f'''
            mutation CreateModelDeployDefinition($datasetId: ID!, $input: CreateModelDeployDefinitionInput!) {{
                createModelDeployDefinition(datasetId: $datasetId, input: $input) {{
                    {Schemas.DEFINITION}
                }}
            }}
        ''',
        "variables": create_model_deploy_definition_params,
    }

    DELETE_MODEL_DEPLOY_DEFINITION = {
        "name": "deleteModelDeployDefinition",
        "query": '''
            mutation DeleteModelDeployDefinition($datasetId: ID!, $definitionId: ID!) {
                deleteModelDeployDefinition(datasetId: $datasetId, definitionId: $definitionId) {
                    id
                    detachedDeploymentCount
                    unlinkedModelCount
                }
            }
        ''',
        "variables": model_deploy_definition_params,
    }

    SET_MODEL_DEPLOY_DEFINITION_PINNED = {
        "name": "setModelDeployDefinitionPinned",
        "query": f'''
            mutation SetModelDeployDefinitionPinned($datasetId: ID!, $definitionId: ID!, $isPinned: Boolean!) {{
                setModelDeployDefinitionPinned(datasetId: $datasetId, definitionId: $definitionId, isPinned: $isPinned) {{
                    {Schemas.DEFINITION}
                }}
            }}
        ''',
        "variables": set_model_deploy_definition_pinned_params,
    }

    UNBIND_MODEL_DEPLOY_DEFINITION = {
        "name": "unbindModelDeployDefinition",
        "query": f'''
            mutation UnbindModelDeployDefinition($datasetId: ID!, $modelId: ID!) {{
                unbindModelDeployDefinition(datasetId: $datasetId, modelId: $modelId) {{
                    {Schemas.MODEL_WITH_DEFINITION}
                }}
            }}
        ''',
        "variables": unbind_model_deploy_definition_params,
    }
