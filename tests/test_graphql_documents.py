"""Every GraphQL document the SDK sends parses and validates against the platform schema.

The schema is a copy of zenith ``tmp/schema-public.gql`` in ``tests/fixtures``:
branch ``feat/fde-237-deploy-definition-params-temp-main``, commit 31a05ce
(temp-main with FDE-221 GPU options and C38 deployment forms and expiry). It
replaced the copy from branch ``fde-85-model-task-type-vlm`` (commit a52f8ae),
which was older than temp-main. When the platform schema changes, copy the new
file over it unchanged; do not edit it by hand.
"""
import importlib
import pkgutil
import re
from pathlib import Path

import pytest

graphql = pytest.importorskip("graphql")  # graphql-core, a test-only dependency (MIT)

import spb_onprem  # noqa: E402

SCHEMA_FILE = Path(__file__).parent / "fixtures" / "zenith-schema-public.gql"


def _documents():
    for module in pkgutil.iter_modules(spb_onprem.__path__):
        if not module.ispkg:
            continue
        try:
            queries = importlib.import_module(f"spb_onprem.{module.name}.queries")
        except ModuleNotFoundError:
            continue
        holder = getattr(queries, "Queries", None)
        for key, value in vars(holder or object).items():
            if isinstance(value, dict) and isinstance(value.get("query"), str):
                yield f"{module.name}.{key}", value


DOCUMENTS = sorted(_documents(), key=lambda item: item[0])


@pytest.fixture(scope="module")
def schema():
    return graphql.build_schema(SCHEMA_FILE.read_text())


@pytest.mark.parametrize("name,query", DOCUMENTS, ids=[name for name, _ in DOCUMENTS])
def test_document_is_valid(schema, name, query):
    document = graphql.parse(query["query"])
    errors = graphql.validate(schema, document)
    assert not errors, f"{name}: " + "; ".join(error.message for error in errors)
    # The response is read by this name, so the document must select it.
    operation = document.definitions[0]
    selected = {selection.name.value for selection in operation.selection_set.selections}
    assert query["name"] in selected, f"{name}: name {query['name']!r} is not selected ({sorted(selected)})"


def test_all_documents_are_checked():
    assert len(DOCUMENTS) >= 80


#: Operations only the platform's own components call (sidecar, DAGs) through the system API.
#: The SDK is a public client; it must never send them.
SYSTEM_ONLY_OPERATIONS = {
    "bindModelDeployDefinition",
    "issueModelDeploymentRuntimeCredentials",
    "registerModelDeploymentRuntime",
    "heartbeatModelDeployment",
    "confirmModelDeploymentRemoved",
    "finishModelDeployment",
    "modelDeploymentRuntimeStates",
    "deleteDatasetModelDeployDefinitions",
    "beginModelDeploymentDeletion",
}


@pytest.mark.parametrize("name,query", DOCUMENTS, ids=[name for name, _ in DOCUMENTS])
def test_no_system_only_operation(name, query):
    document = graphql.parse(query["query"])
    fields = {
        selection.name.value
        for definition in document.definitions
        for selection in definition.selection_set.selections
    }
    assert not fields & SYSTEM_ONLY_OPERATIONS, f"{name} calls system-only {sorted(fields & SYSTEM_ONLY_OPERATIONS)}"
    for operation in SYSTEM_ONLY_OPERATIONS:  # as a whole word: unbindModelDeployDefinition is public
        assert not re.search(rf"\b{operation}\b", query["query"]), f"{name} mentions system-only {operation}"
