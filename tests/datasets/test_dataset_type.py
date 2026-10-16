import pytest
from unittest.mock import Mock

from spb_onprem import DatasetType as TopLevelDatasetType
from spb_onprem.datasets import DatasetType
from spb_onprem.datasets.entities import Dataset
from spb_onprem.datasets.params import create_dataset_params
from spb_onprem.datasets.queries import Queries, Schemas
from spb_onprem.datasets.service import DatasetService
from spb_onprem.exceptions import BadParameterError


class TestDatasetTypeEnum:
    def test_vlm_value(self):
        assert DatasetType.VLM.value == "VLM"
        assert DatasetType("VLM") is DatasetType.VLM

    def test_only_vlm_member(self):
        assert [t.value for t in DatasetType] == ["VLM"]

    def test_exported_from_top_level(self):
        assert TopLevelDatasetType is DatasetType


class TestCreateDatasetParamsType:
    def test_type_omitted_is_not_sent(self):
        assert create_dataset_params(name="ds") == {"name": "ds"}

    def test_type_none_is_not_sent(self):
        assert create_dataset_params(name="ds", type=None) == {"name": "ds"}

    def test_type_vlm_enum(self):
        params = create_dataset_params(name="ds", description="d", type=DatasetType.VLM)
        assert params == {"name": "ds", "description": "d", "type": "VLM"}

    def test_type_vlm_string(self):
        assert create_dataset_params(name="ds", type="VLM")["type"] == "VLM"

    def test_type_unknown_raises(self):
        with pytest.raises(BadParameterError, match="Unknown dataset type"):
            create_dataset_params(name="ds", type="CV")


class TestCreateDatasetServiceType:
    def setup_method(self):
        self.dataset_service = DatasetService()
        self.dataset_service.request_gql = Mock()
        self.dataset_service.request_gql.return_value = {
            "id": "dataset-1",
            "name": "ds",
            "type": "VLM",
        }

    def test_create_dataset_passes_type_variable(self):
        result = self.dataset_service.create_dataset(name="ds", type=DatasetType.VLM)

        query, variables = self.dataset_service.request_gql.call_args[0]
        assert query is Queries.CREATE_DATASET
        assert variables == {"name": "ds", "type": "VLM"}
        assert result.type is DatasetType.VLM

    def test_create_dataset_without_type_keeps_cv_variables(self):
        self.dataset_service.request_gql.return_value = {"id": "dataset-2", "name": "ds", "type": None}

        result = self.dataset_service.create_dataset(name="ds", description="d")

        _, variables = self.dataset_service.request_gql.call_args[0]
        assert variables == {"name": "ds", "description": "d"}
        assert "type" not in variables
        assert result.type is None

    def test_create_dataset_mutation_declares_type(self):
        mutation = Queries.CREATE_DATASET["query"]
        assert "$type: DatasetType" in mutation
        assert "type: $type" in mutation


class TestDatasetEntityType:
    def test_parse_vlm(self):
        dataset = Dataset.model_validate({"id": "d1", "name": "n", "type": "VLM"})
        assert dataset.type is DatasetType.VLM

    def test_parse_null_type_is_cv(self):
        assert Dataset.model_validate({"id": "d1", "type": None}).type is None

    def test_parse_missing_type_is_cv(self):
        assert Dataset.model_validate({"id": "d1"}).type is None

    def test_schema_selects_type(self):
        fields = [line.strip() for line in Schemas.DATASET.splitlines()]
        assert "type" in fields
        assert Schemas.DATASET in Queries.DATASET["query"]
        assert Schemas.DATASET in Queries.DATASETS["query"]
