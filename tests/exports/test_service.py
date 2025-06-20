import pytest
from unittest.mock import MagicMock, patch

from spb_onprem.exports.service import ExportService
from spb_onprem.exports.entities import Export
from spb_onprem.exports.params import ExportFilter
from spb_onprem.data.params import DataListFilter, DataFilterOptions
from spb_onprem.data.enums import DataType
from spb_onprem.base_types import Undefined


@pytest.fixture
def export_service():
    return ExportService()


class TestExportService:
    def test_create_export(self, export_service):
        # Given
        mock_response = {
            "id": "test_export_id",
            "datasetId": "test_dataset_id",
            "name": "test_export_name",
            "dataFilter": {"must": {"keyContains": "test"}},
            "location": "s3://test-bucket/exports/",
            "dataCount": 100,
            "frameCount": 50,
            "annotationCount": 25,
            "meta": {"created_by": "test_user"},
            "createdAt": "2024-01-01T00:00:00Z",
            "completedAt": None
        }
        export_service.request_gql = MagicMock(return_value=mock_response)
        
        # Create DataListFilter for data filtering
        data_filter = DataListFilter(
            must_filter=DataFilterOptions(key_contains="test")
        )
        
        # When
        export = export_service.create_export(
            dataset_id="test_dataset_id",
            name="test_export_name",
            data_filter=data_filter,
            meta={"created_by": "test_user"}
        )
        
        # Then
        assert isinstance(export, Export)
        assert export.id == "test_export_id"
        assert export.dataset_id == "test_dataset_id"
        assert export.name == "test_export_name"
        assert isinstance(export.data_filter, DataListFilter)
        assert export.data_filter.must_filter.key_contains == "test"
        assert export.meta == {"created_by": "test_user"}
    
    def test_create_export_minimal_params(self, export_service):
        # Given
        mock_response = {
            "id": "test_export_id",
            "datasetId": "test_dataset_id",
            "name": None,
            "dataFilter": None,
            "location": None,
            "dataCount": None,
            "frameCount": None,
            "annotationCount": None,
            "meta": None,
            "createdAt": "2024-01-01T00:00:00Z",
            "completedAt": None
        }
        export_service.request_gql = MagicMock(return_value=mock_response)
        
        # When
        export = export_service.create_export(dataset_id="test_dataset_id")
        
        # Then
        assert isinstance(export, Export)
        assert export.id == "test_export_id"
        assert export.dataset_id == "test_dataset_id"
        assert export.name is None
        assert export.data_filter is None
        assert export.meta is None
    
    def test_get_exports(self, export_service):
        # Given
        mock_response = {
            "exports": [
                {
                    "id": "test_export_id_1",
                    "datasetId": "test_dataset_id",
                    "name": "test_export_1",
                    "location": "s3://test-bucket/export1/",
                    "dataCount": 100,
                    "createdAt": "2024-01-01T00:00:00Z"
                },
                {
                    "id": "test_export_id_2",
                    "datasetId": "test_dataset_id",
                    "name": "test_export_2",
                    "location": "s3://test-bucket/export2/",
                    "dataCount": 200,
                    "createdAt": "2024-01-02T00:00:00Z"
                }
            ],
            "next": "next_cursor",
            "totalCount": 2
        }
        export_service.request_gql = MagicMock(return_value=mock_response)
        
        # When
        exports, next_cursor, total_count = export_service.get_exports(
            dataset_id="test_dataset_id",
            length=10
        )
        
        # Then
        assert len(exports) == 2
        assert all(isinstance(export, Export) for export in exports)
        assert exports[0].id == "test_export_id_1"
        assert exports[1].id == "test_export_id_2"
        assert next_cursor == "next_cursor"
        assert total_count == 2
    
    def test_get_exports_with_filter(self, export_service):
        # Given
        mock_response = {
            "exports": [
                {
                    "id": "test_export_id_1",
                    "datasetId": "test_dataset_id",
                    "name": "filtered_export",
                    "location": "s3://test-bucket/filtered/",
                    "dataCount": 50,
                    "createdAt": "2024-01-01T00:00:00Z"
                }
            ],
            "next": None,
            "totalCount": 1
        }
        export_service.request_gql = MagicMock(return_value=mock_response)
        
        export_filter = ExportFilter(
            must_filter={"name": "filtered_export"}
        )
        
        # When
        exports, next_cursor, total_count = export_service.get_exports(
            dataset_id="test_dataset_id",
            export_filter=export_filter,
            cursor="start_cursor",
            length=5
        )
        
        # Then
        assert len(exports) == 1
        assert exports[0].name == "filtered_export"
        assert next_cursor is None
        assert total_count == 1
    
    def test_get_export(self, export_service):
        # Given
        mock_response = {
            "id": "test_export_id",
            "datasetId": "test_dataset_id",
            "name": "single_export",
            "dataFilter": {"must": {"keyContains": "completed"}},
            "location": "s3://test-bucket/single/",
            "dataCount": 75,
            "frameCount": 30,
            "annotationCount": 15,
            "meta": {"processed": True},
            "createdAt": "2024-01-01T00:00:00Z",
            "completedAt": "2024-01-01T01:00:00Z"
        }
        export_service.request_gql = MagicMock(return_value=mock_response)
        
        # When
        export = export_service.get_export(
            dataset_id="test_dataset_id",
            export_id="test_export_id"
        )
        
        # Then
        assert isinstance(export, Export)
        assert export.id == "test_export_id"
        assert export.dataset_id == "test_dataset_id"
        assert export.name == "single_export"
        assert isinstance(export.data_filter, DataListFilter)
        assert export.data_filter.must_filter.key_contains == "completed"
        assert export.location == "s3://test-bucket/single/"
        assert export.data_count == 75
        assert export.frame_count == 30
        assert export.annotation_count == 15
        assert export.meta == {"processed": True}
        assert export.completed_at == "2024-01-01T01:00:00Z"
    
    def test_update_export(self, export_service):
        # Given
        mock_response = {
            "id": "test_export_id",
            "datasetId": "test_dataset_id",
            "name": "updated_export_name",
            "dataFilter": {"must": {"keyContains": "updated"}},
            "location": "s3://test-bucket/updated/",
            "dataCount": 150,
            "frameCount": 75,
            "annotationCount": 40,
            "meta": {"updated_by": "test_user", "version": 2},
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T12:00:00Z",
            "completedAt": "2024-01-01T13:00:00Z"
        }
        export_service.request_gql = MagicMock(return_value=mock_response)
        
        # Create DataListFilter for update
        data_filter = DataListFilter(
            must_filter=DataFilterOptions(key_contains="updated")
        )
        
        # When
        export = export_service.update_export(
            dataset_id="test_dataset_id",
            export_id="test_export_id",
            name="updated_export_name",
            location="s3://test-bucket/updated/",
            data_filter=data_filter,
            data_count=150,
            frame_count=75,
            annotation_count=40,
            meta={"updated_by": "test_user", "version": 2},
            completed_at="2024-01-01T13:00:00Z"
        )
        
        # Then
        assert isinstance(export, Export)
        assert export.id == "test_export_id"
        assert export.name == "updated_export_name"
        assert export.location == "s3://test-bucket/updated/"
        assert isinstance(export.data_filter, DataListFilter)
        assert export.data_filter.must_filter.key_contains == "updated"
        assert export.data_count == 150
        assert export.frame_count == 75
        assert export.annotation_count == 40
        assert export.meta == {"updated_by": "test_user", "version": 2}
        assert export.completed_at == "2024-01-01T13:00:00Z"
    
    def test_update_export_partial(self, export_service):
        # Given
        mock_response = {
            "id": "test_export_id",
            "datasetId": "test_dataset_id",
            "name": "partially_updated_export",
            "dataFilter": None,
            "location": None,
            "dataCount": None,
            "frameCount": None,
            "annotationCount": None,
            "meta": {"partial_update": True},
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T12:00:00Z",
            "completedAt": None
        }
        export_service.request_gql = MagicMock(return_value=mock_response)
        
        # When
        export = export_service.update_export(
            dataset_id="test_dataset_id",
            export_id="test_export_id",
            name="partially_updated_export",
            meta={"partial_update": True}
        )
        
        # Then
        assert isinstance(export, Export)
        assert export.id == "test_export_id"
        assert export.name == "partially_updated_export"
        assert export.meta == {"partial_update": True}
    
    def test_delete_export(self, export_service):
        # Given
        mock_response = True
        export_service.request_gql = MagicMock(return_value=mock_response)
        
        # When
        result = export_service.delete_export(
            dataset_id="test_dataset_id",
            export_id="test_export_id"
        )
        
        # Then
        assert result is True
    
    def test_delete_export_failed(self, export_service):
        # Given
        mock_response = False
        export_service.request_gql = MagicMock(return_value=mock_response)
        
        # When
        result = export_service.delete_export(
            dataset_id="test_dataset_id",
            export_id="non_existent_export_id"
        )
        
        # Then
        assert result is False
    
    def test_delete_export_none_response(self, export_service):
        # Given
        mock_response = None
        export_service.request_gql = MagicMock(return_value=mock_response)
        
        # When
        result = export_service.delete_export(
            dataset_id="test_dataset_id",
            export_id="test_export_id"
        )
        
        # Then
        assert result is None
    
    def test_create_export_with_complex_data_filter(self, export_service):
        # Given
        mock_response = {
            "id": "test_export_id",
            "datasetId": "test_dataset_id",
            "name": "complex_filter_export",
            "dataFilter": {"must": {"keyContains": "validation", "typeIn": ["SUPERB_IMAGE"]}, "not": {"keyContains": "test"}},
            "location": "s3://test-bucket/complex/",
            "dataCount": 200,
            "createdAt": "2024-01-01T00:00:00Z"
        }
        export_service.request_gql = MagicMock(return_value=mock_response)
        
        # Create complex DataListFilter
        data_filter = DataListFilter(
            must_filter=DataFilterOptions(
                key_contains="validation",
                type_in=[DataType.SUPERB_IMAGE]
            ),
            not_filter=DataFilterOptions(
                key_contains="test"
            )
        )
        
        # When
        export = export_service.create_export(
            dataset_id="test_dataset_id",
            name="complex_filter_export",
            data_filter=data_filter
        )
        
        # Then
        assert isinstance(export, Export)
        assert export.id == "test_export_id"
        assert export.name == "complex_filter_export"
        assert export.data_count == 200
        assert isinstance(export.data_filter, DataListFilter)
        assert export.data_filter.must_filter.key_contains == "validation"
        assert export.data_filter.must_filter.type_in == [DataType.SUPERB_IMAGE]
        assert export.data_filter.not_filter.key_contains == "test"
    
    @patch('spb_onprem.exports.service.Queries')
    def test_create_export_query_call(self, mock_queries, export_service):
        # Given
        mock_response = {"id": "test_id", "datasetId": "test_dataset_id"}
        export_service.request_gql = MagicMock(return_value=mock_response)
        
        mock_variables_func = MagicMock(return_value={"dataset_id": "test_dataset_id"})
        mock_queries.CREATE_EXPORT = {"variables": mock_variables_func}
        
        # When
        export_service.create_export(dataset_id="test_dataset_id")
        
        # Then
        export_service.request_gql.assert_called_once()
        mock_variables_func.assert_called_once_with(
            dataset_id="test_dataset_id",
            name=Undefined,
            data_filter=Undefined,
            data_count=Undefined,
            frame_count=Undefined,
            annotation_count=Undefined,
            meta=Undefined
        )
    
    @patch('spb_onprem.exports.service.Queries')
    def test_get_exports_query_call(self, mock_queries, export_service):
        # Given
        mock_response = {"exports": [], "next": None, "totalCount": 0}
        export_service.request_gql = MagicMock(return_value=mock_response)
        
        mock_variables_func = MagicMock(return_value={"dataset_id": "test_dataset_id"})
        mock_queries.GET_EXPORTS = {"variables": mock_variables_func}
        
        # When
        export_service.get_exports(dataset_id="test_dataset_id", cursor="test_cursor", length=20)
        
        # Then
        export_service.request_gql.assert_called_once()
        mock_variables_func.assert_called_once_with(
            dataset_id="test_dataset_id",
            export_filter=None,
            cursor="test_cursor",
            length=20
        ) 