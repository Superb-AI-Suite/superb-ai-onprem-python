import pytest
from datetime import datetime

from spb_onprem.exports.params.create_export import create_export_params
from spb_onprem.exports.params.update_export import update_export_params
from spb_onprem.exports.params.export import get_export_params
from spb_onprem.exports.params.delete_export import delete_export_params
from spb_onprem.exports.params.exports import get_exports_params, ExportFilter, ExportFilterOptions
from spb_onprem.exceptions import BadParameterError
from spb_onprem.base_types import Undefined


class TestCreateExportParams:
    def test_create_export_params_minimal(self):
        # Given
        dataset_id = "test_dataset_id"
        
        # When
        params = create_export_params(dataset_id=dataset_id)
        
        # Then
        assert params["dataset_id"] == dataset_id
        assert "location" not in params
        assert "name" not in params
        assert "data_filter" not in params
        assert "meta" not in params
    
    def test_create_export_params_full(self):
        # Given
        dataset_id = "test_dataset_id"
        location = "s3://test-bucket/exports/"
        name = "test_export"
        data_filter = {"must": {"keyContains": "test"}}
        data_count = 100
        frame_count = 50
        annotation_count = 25
        meta = {"created_by": "test_user"}
        
        # When
        params = create_export_params(
            dataset_id=dataset_id,
            location=location,
            name=name,
            data_filter=data_filter,
            data_count=data_count,
            frame_count=frame_count,
            annotation_count=annotation_count,
            meta=meta
        )
        
        # Then
        assert params["dataset_id"] == dataset_id
        assert params["location"] == location
        assert params["name"] == name
        assert params["data_filter"] == data_filter
        assert params["data_count"] == data_count
        assert params["frame_count"] == frame_count
        assert params["annotation_count"] == annotation_count
        assert params["meta"] == meta
    
    def test_create_export_params_missing_dataset_id(self):
        # Given
        dataset_id = None
        
        # When/Then
        with pytest.raises(BadParameterError) as exc_info:
            create_export_params(dataset_id=dataset_id)
        assert str(exc_info.value) == "Dataset ID is required"


class TestUpdateExportParams:
    def test_update_export_params_minimal(self):
        # Given
        dataset_id = "test_dataset_id"
        export_id = "test_export_id"
        
        # When
        params = update_export_params(
            dataset_id=dataset_id,
            export_id=export_id
        )
        
        # Then
        assert params["dataset_id"] == dataset_id
        assert params["export_id"] == export_id
        assert "location" not in params
        assert "name" not in params
        assert "data_filter" not in params
        assert "meta" not in params
    
    def test_update_export_params_full(self):
        # Given
        dataset_id = "test_dataset_id"
        export_id = "test_export_id"
        location = "s3://test-bucket/updated/"
        name = "updated_export"
        data_filter = {"must": {"updated": True}}
        data_count = 200
        frame_count = 100
        annotation_count = 50
        meta = {"updated_by": "test_user"}
        completed_at = datetime(2024, 1, 1, 12, 0, 0)
        
        # When
        params = update_export_params(
            dataset_id=dataset_id,
            export_id=export_id,
            location=location,
            name=name,
            data_filter=data_filter,
            data_count=data_count,
            frame_count=frame_count,
            annotation_count=annotation_count,
            meta=meta,
            completed_at=completed_at
        )
        
        # Then
        assert params["dataset_id"] == dataset_id
        assert params["export_id"] == export_id
        assert params["location"] == location
        assert params["name"] == name
        assert params["data_filter"] == data_filter
        assert params["data_count"] == data_count
        assert params["frame_count"] == frame_count
        assert params["annotation_count"] == annotation_count
        assert params["meta"] == meta
        assert params["completed_at"] == completed_at
    
    def test_update_export_params_missing_dataset_id(self):
        # Given
        dataset_id = None
        export_id = "test_export_id"
        
        # When/Then
        with pytest.raises(BadParameterError) as exc_info:
            update_export_params(dataset_id=dataset_id, export_id=export_id)
        assert str(exc_info.value) == "Dataset ID is required"
    
    def test_update_export_params_missing_export_id(self):
        # Given
        dataset_id = "test_dataset_id"
        export_id = None
        
        # When/Then
        with pytest.raises(BadParameterError) as exc_info:
            update_export_params(dataset_id=dataset_id, export_id=export_id)
        assert str(exc_info.value) == "Export ID is required"


class TestGetExportParams:
    def test_get_export_params(self):
        # Given
        dataset_id = "test_dataset_id"
        export_id = "test_export_id"
        
        # When
        params = get_export_params(dataset_id=dataset_id, export_id=export_id)
        
        # Then
        assert params["dataset_id"] == dataset_id
        assert params["export_id"] == export_id
    
    def test_get_export_params_missing_dataset_id(self):
        # Given
        dataset_id = None
        export_id = "test_export_id"
        
        # When/Then
        with pytest.raises(BadParameterError) as exc_info:
            get_export_params(dataset_id=dataset_id, export_id=export_id)
        assert str(exc_info.value) == "Dataset ID is required"
    
    def test_get_export_params_missing_export_id(self):
        # Given
        dataset_id = "test_dataset_id"
        export_id = None
        
        # When/Then
        with pytest.raises(BadParameterError) as exc_info:
            get_export_params(dataset_id=dataset_id, export_id=export_id)
        assert str(exc_info.value) == "Export ID is required"


class TestDeleteExportParams:
    def test_delete_export_params(self):
        # Given
        dataset_id = "test_dataset_id"
        export_id = "test_export_id"
        
        # When
        params = delete_export_params(dataset_id=dataset_id, export_id=export_id)
        
        # Then
        assert params["dataset_id"] == dataset_id
        assert params["export_id"] == export_id
    
    def test_delete_export_params_missing_dataset_id(self):
        # Given
        dataset_id = None
        export_id = "test_export_id"
        
        # When/Then
        with pytest.raises(BadParameterError) as exc_info:
            delete_export_params(dataset_id=dataset_id, export_id=export_id)
        assert str(exc_info.value) == "Dataset ID is required"
    
    def test_delete_export_params_missing_export_id(self):
        # Given
        dataset_id = "test_dataset_id"
        export_id = None
        
        # When/Then
        with pytest.raises(BadParameterError) as exc_info:
            delete_export_params(dataset_id=dataset_id, export_id=export_id)
        assert str(exc_info.value) == "Export ID is required"


class TestGetExportsParams:
    def test_get_exports_params_minimal(self):
        # Given
        dataset_id = "test_dataset_id"
        
        # When
        params = get_exports_params(dataset_id=dataset_id)
        
        # Then
        assert params["dataset_id"] == dataset_id
        assert params["length"] == 10
        assert "filter" not in params
        assert "cursor" not in params
    
    def test_get_exports_params_with_filter(self):
        # Given
        dataset_id = "test_dataset_id"
        export_filter = ExportFilter(
            must_filter=ExportFilterOptions(name="test_export"),
            not_filter=ExportFilterOptions(location_contains="temp")
        )
        cursor = "test_cursor"
        length = 20
        
        # When
        params = get_exports_params(
            dataset_id=dataset_id,
            export_filter=export_filter,
            cursor=cursor,
            length=length
        )
        
        # Then
        assert params["dataset_id"] == dataset_id
        assert params["length"] == length
        assert params["cursor"] == cursor
        assert "filter" in params
        assert params["filter"]["must"]["name"] == "test_export"
        assert params["filter"]["not"]["locationContains"] == "temp"
    
    def test_get_exports_params_missing_dataset_id(self):
        # Given
        dataset_id = None
        
        # When/Then
        with pytest.raises(BadParameterError) as exc_info:
            get_exports_params(dataset_id=dataset_id)
        assert str(exc_info.value) == "Dataset ID is required"


class TestExportFilterOptions:
    def test_export_filter_options_creation(self):
        # Given/When
        filter_options = ExportFilterOptions(
            id_in=["id1", "id2"],
            name_contains="test",
            name="exact_name",
            location_contains="bucket",
            location="s3://test-bucket/"
        )
        
        # Then
        assert filter_options.id_in == ["id1", "id2"]
        assert filter_options.name_contains == "test"
        assert filter_options.name == "exact_name"
        assert filter_options.location_contains == "bucket"
        assert filter_options.location == "s3://test-bucket/"
    
    def test_export_filter_options_aliases(self):
        # Given/When
        filter_options = ExportFilterOptions(
            id_in=["id1", "id2"],
            name_contains="test"
        )
        
        # Then
        dumped = filter_options.model_dump(by_alias=True)
        assert dumped["idIn"] == ["id1", "id2"]
        assert dumped["nameContains"] == "test"


class TestExportFilter:
    def test_export_filter_creation(self):
        # Given
        must_filter = ExportFilterOptions(name="test_export")
        not_filter = ExportFilterOptions(location_contains="temp")
        
        # When
        export_filter = ExportFilter(
            must_filter=must_filter,
            not_filter=not_filter
        )
        
        # Then
        assert export_filter.must_filter == must_filter
        assert export_filter.not_filter == not_filter
    
    def test_export_filter_aliases(self):
        # Given
        must_filter = ExportFilterOptions(name="test_export")
        not_filter = ExportFilterOptions(location_contains="temp")
        export_filter = ExportFilter(
            must_filter=must_filter,
            not_filter=not_filter
        )
        
        # When
        dumped = export_filter.model_dump(by_alias=True, exclude_unset=True)
        
        # Then
        assert "must" in dumped
        assert "not" in dumped
        assert dumped["must"]["name"] == "test_export"
        assert dumped["not"]["locationContains"] == "temp" 