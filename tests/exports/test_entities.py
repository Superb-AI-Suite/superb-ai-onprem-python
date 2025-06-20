import pytest
from spb_onprem.exports.entities import Export
from spb_onprem.data.params import DataListFilter, DataFilterOptions


class TestExport:
    def test_export_creation_minimal(self):
        # Given
        export_data = {
            "id": "test_export_id",
            "datasetId": "test_dataset_id"
        }
        
        # When
        export = Export.model_validate(export_data)
        
        # Then
        assert export.id == "test_export_id"
        assert export.dataset_id == "test_dataset_id"
        assert export.name is None
        assert export.data_filter is None
        assert export.location is None
        assert export.data_count is None
        assert export.annotation_count is None
        assert export.frame_count is None
        assert export.meta is None
        assert export.created_at is None
        assert export.created_by is None
        assert export.updated_at is None
        assert export.updated_by is None
        assert export.completed_at is None
    
    def test_export_creation_full(self):
        # Given
        export_data = {
            "id": "test_export_id",
            "datasetId": "test_dataset_id",
            "name": "test_export_name",
            "dataFilter": {"must": {"keyContains": "test"}},
            "location": "s3://test-bucket/exports/",
            "dataCount": 100,
            "annotationCount": 50,
            "frameCount": 25,
            "meta": {"created_by": "test_user", "version": 1},
            "createdAt": "2024-01-01T00:00:00Z",
            "createdBy": "test_user",
            "updatedAt": "2024-01-01T12:00:00Z",
            "updatedBy": "test_user",
            "completedAt": "2024-01-01T13:00:00Z"
        }
        
        # When
        export = Export.model_validate(export_data)
        
        # Then
        assert export.id == "test_export_id"
        assert export.dataset_id == "test_dataset_id"
        assert export.name == "test_export_name"
        assert isinstance(export.data_filter, DataListFilter)
        assert export.data_filter.must_filter.key_contains == "test"
        assert export.location == "s3://test-bucket/exports/"
        assert export.data_count == 100
        assert export.annotation_count == 50
        assert export.frame_count == 25
        assert export.meta == {"created_by": "test_user", "version": 1}
        assert export.created_at == "2024-01-01T00:00:00Z"
        assert export.created_by == "test_user"
        assert export.updated_at == "2024-01-01T12:00:00Z"
        assert export.updated_by == "test_user"
        assert export.completed_at == "2024-01-01T13:00:00Z"
    
    def test_export_field_aliases(self):
        # Given
        export_data = {
            "id": "test_export_id",
            "datasetId": "test_dataset_id",
            "dataFilter": {"must": {"keyContains": "filter"}},
            "dataCount": 100,
            "annotationCount": 50,
            "frameCount": 25,
            "createdAt": "2024-01-01T00:00:00Z",
            "createdBy": "test_user",
            "updatedAt": "2024-01-01T12:00:00Z",
            "updatedBy": "test_user",
            "completedAt": "2024-01-01T13:00:00Z"
        }
        
        # When
        export = Export.model_validate(export_data)
        
        # Then - Test that aliases work correctly
        assert export.dataset_id == "test_dataset_id"  # datasetId -> dataset_id
        assert isinstance(export.data_filter, DataListFilter)
        assert export.data_filter.must_filter.key_contains == "filter"
        assert export.data_count == 100  # dataCount -> data_count
        assert export.annotation_count == 50  # annotationCount -> annotation_count
        assert export.frame_count == 25  # frameCount -> frame_count
        assert export.created_at == "2024-01-01T00:00:00Z"  # createdAt -> created_at
        assert export.created_by == "test_user"  # createdBy -> created_by
        assert export.updated_at == "2024-01-01T12:00:00Z"  # updatedAt -> updated_at
        assert export.updated_by == "test_user"  # updatedBy -> updated_by
        assert export.completed_at == "2024-01-01T13:00:00Z"  # completedAt -> completed_at
    
    def test_export_model_dump_with_aliases(self):
        # Given - Create export with DataListFilter
        data_filter = DataListFilter(
            must_filter=DataFilterOptions(key_contains="filter")
        )
        
        export = Export(
            id="test_export_id",
            dataset_id="test_dataset_id",
            name="test_export",
            data_filter=data_filter,
            location="s3://test-bucket/",
            data_count=100,
            annotation_count=50,
            frame_count=25,
            meta={"test": "meta"},
            created_at="2024-01-01T00:00:00Z",
            created_by="test_user",
            updated_at="2024-01-01T12:00:00Z",
            updated_by="test_user",
            completed_at="2024-01-01T13:00:00Z"
        )
        
        # When
        dumped = export.model_dump(by_alias=True, exclude_unset=True)
        
        # Then - Test that field names are properly aliased in output
        assert dumped["id"] == "test_export_id"
        assert dumped["datasetId"] == "test_dataset_id"
        assert dumped["name"] == "test_export"
        assert "dataFilter" in dumped
        assert dumped["dataFilter"]["must"]["keyContains"] == "filter"
        assert dumped["location"] == "s3://test-bucket/"
        assert dumped["dataCount"] == 100
        assert dumped["annotationCount"] == 50
        assert dumped["frameCount"] == 25
        assert dumped["meta"] == {"test": "meta"}
        assert dumped["createdAt"] == "2024-01-01T00:00:00Z"
        assert dumped["createdBy"] == "test_user"
        assert dumped["updatedAt"] == "2024-01-01T12:00:00Z"
        assert dumped["updatedBy"] == "test_user"
        assert dumped["completedAt"] == "2024-01-01T13:00:00Z"
    
    def test_export_required_fields_validation(self):
        # Given - Missing required fields
        export_data = {}
        
        # When/Then - Should raise validation error for missing required fields
        with pytest.raises(Exception):  # ValidationError from pydantic
            Export.model_validate(export_data)
    
    def test_export_required_dataset_id_validation(self):
        # Given - Missing dataset_id
        export_data = {
            "id": "test_export_id"
        }
        
        # When/Then - Should raise validation error for missing dataset_id
        with pytest.raises(Exception):  # ValidationError from pydantic
            Export.model_validate(export_data)
    
    def test_export_optional_fields_none(self):
        # Given
        export_data = {
            "id": "test_export_id",
            "datasetId": "test_dataset_id",
            "name": None,
            "dataFilter": None,
            "location": None,
            "dataCount": None,
            "annotationCount": None,
            "frameCount": None,
            "meta": None,
            "createdAt": None,
            "createdBy": None,
            "updatedAt": None,
            "updatedBy": None,
            "completedAt": None
        }
        
        # When
        export = Export.model_validate(export_data)
        
        # Then - All optional fields should be None
        assert export.name is None
        assert export.data_filter is None
        assert export.location is None
        assert export.data_count is None
        assert export.annotation_count is None
        assert export.frame_count is None
        assert export.meta is None
        assert export.created_at is None
        assert export.created_by is None
        assert export.updated_at is None
        assert export.updated_by is None
        assert export.completed_at is None
    
    def test_export_equality(self):
        # Given
        export1 = Export(
            id="test_export_id",
            dataset_id="test_dataset_id",
            name="test_export"
        )
        export2 = Export(
            id="test_export_id",
            dataset_id="test_dataset_id",
            name="test_export"
        )
        export3 = Export(
            id="different_export_id",
            dataset_id="test_dataset_id",
            name="test_export"
        )
        
        # When/Then
        assert export1 == export2  # Same data should be equal
        assert export1 != export3  # Different data should not be equal
    
    def test_export_string_representation(self):
        # Given
        export = Export(
            id="test_export_id",
            dataset_id="test_dataset_id",
            name="test_export"
        )
        
        # When
        str_repr = str(export)
        
        # Then
        assert "test_export_id" in str_repr
        assert "test_dataset_id" in str_repr 