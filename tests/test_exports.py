"""Package exports and quiet services."""
import importlib
import pkgutil
from unittest.mock import Mock

import pytest

import spb_onprem
from spb_onprem import SliceService

PACKAGES = ["spb_onprem", "spb_onprem.entities"] + [
    f"spb_onprem.{module.name}" for module in pkgutil.iter_modules(spb_onprem.__path__) if module.ispkg
]


@pytest.mark.parametrize("name", PACKAGES)
def test_every_all_name_exists(name):
    """`from <package> import *` fails when __all__ names something that is not there."""
    module = importlib.import_module(name)
    missing = [item for item in getattr(module, "__all__", ()) if not hasattr(module, item)]
    assert missing == []


def test_star_import():
    namespace = {}
    exec("from spb_onprem import *", namespace)
    assert "DiagnosisService" in namespace
    assert "AnalyticsReportItemType" in namespace


def test_create_slice_prints_nothing(capsys):
    service = SliceService()
    service.request_gql = Mock(return_value={"id": "slice-1", "datasetId": "dataset-1", "name": "train"})

    created = service.create_slice(dataset_id="dataset-1", name="train")

    assert created.id == "slice-1"
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("name", [
    "ModelDeployDefinitionUsage", "ModelDeployDefinitionDeletion", "ModelDeploymentRuntimeEndStatus",
    "DeploymentInvokePart", "DeploymentInvokeError", "DeploymentInvokeForbiddenError",
    "DeploymentInvokeNotFoundError", "DeploymentInvokeConflictError", "DeploymentInvokeInvalidInputError",
])
def test_deployment_types_are_exported_at_the_top(name):
    """Return types and errors of public functions can be imported from spb_onprem."""
    assert name in spb_onprem.__all__ and hasattr(spb_onprem, name)
