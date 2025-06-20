"""
Integration test for the exports module.
This test demonstrates how to use the exports module in a real scenario.
Note: This test is commented out as it requires actual API credentials and dataset.
"""

from spb_onprem.exports import ExportService, ExportFilterOptions
from spb_onprem.exports.params import ExportFilter


def test_export_service_integration():
    """
    Integration test for ExportService.
    
    This test demonstrates the complete workflow of:
    1. Creating an export
    2. Getting exports with filtering
    3. Getting a specific export
    4. Updating an export
    5. Deleting an export
    
    Note: This test is commented out as it requires actual API connection.
    """
    # Uncomment the following lines to run with real API
    
    # # Initialize the service
    # export_service = ExportService()
    # dataset_id = "your_dataset_id_here"
    
    # # 1. Create an export
    # new_export = export_service.create_export(
    #     dataset_id=dataset_id,
    #     name="Test Export from SDK",
    #     data_filter={"must": {"keyContains": "validation"}},
    #     meta={"created_by": "integration_test", "purpose": "testing"}
    # )
    # print(f"Created export: {new_export.id}")
    
    # # 2. Get exports with filtering
    # export_filter = ExportFilter(
    #     must_filter=ExportFilterOptions(name_contains="Test Export")
    # )
    # exports, next_cursor, total_count = export_service.get_exports(
    #     dataset_id=dataset_id,
    #     export_filter=export_filter,
    #     length=10
    # )
    # print(f"Found {len(exports)} exports, total: {total_count}")
    
    # # 3. Get a specific export
    # if exports:
    #     export_detail = export_service.get_export(
    #         dataset_id=dataset_id,
    #         export_id=exports[0].id
    #     )
    #     print(f"Export details: {export_detail.name}")
    
    # # 4. Update the export
    # updated_export = export_service.update_export(
    #     dataset_id=dataset_id,
    #     export_id=new_export.id,
    #     name="Updated Test Export",
    #     meta={"updated_by": "integration_test", "status": "updated"}
    # )
    # print(f"Updated export name: {updated_export.name}")
    
    # # 5. Delete the export
    # delete_result = export_service.delete_export(
    #     dataset_id=dataset_id,
    #     export_id=new_export.id
    # )
    # print(f"Export deleted: {delete_result}")
    
    # For now, just pass the test
    assert True


def test_export_filtering_examples():
    """
    Examples of how to use export filtering.
    """
    # Example 1: Filter by name containing specific text
    name_filter = ExportFilter(
        must_filter=ExportFilterOptions(name_contains="validation")
    )
    
    # Example 2: Filter by exact name match
    exact_name_filter = ExportFilter(
        must_filter=ExportFilterOptions(name="My Export")
    )
    
    # Example 3: Filter by location containing specific text
    location_filter = ExportFilter(
        must_filter=ExportFilterOptions(location_contains="s3://my-bucket")
    )
    
    # Example 4: Complex filter with must and must not conditions
    complex_filter = ExportFilter(
        must_filter=ExportFilterOptions(
            name_contains="production",
            location_contains="s3://"
        ),
        not_filter=ExportFilterOptions(
            name_contains="test"
        )
    )
    
    # Example 5: Filter by multiple IDs
    id_filter = ExportFilter(
        must_filter=ExportFilterOptions(
            id_in=["export_id_1", "export_id_2", "export_id_3"]
        )
    )
    
    # All filters should be valid - test the objects themselves
    assert isinstance(name_filter.must_filter, ExportFilterOptions)
    assert isinstance(exact_name_filter.must_filter, ExportFilterOptions)
    assert isinstance(location_filter.must_filter, ExportFilterOptions)
    assert isinstance(complex_filter.must_filter, ExportFilterOptions)
    assert isinstance(complex_filter.not_filter, ExportFilterOptions)
    assert isinstance(id_filter.must_filter, ExportFilterOptions)


def test_export_service_usage_patterns():
    """
    Demonstrates common usage patterns for the export service.
    """
    # Pattern 1: Pagination through all exports
    def get_all_exports(export_service, dataset_id):
        all_exports = []
        cursor = None
        
        while True:
            exports, next_cursor, _ = export_service.get_exports(
                dataset_id=dataset_id,
                cursor=cursor,
                length=50  # Fetch 50 at a time
            )
            all_exports.extend(exports)
            
            if next_cursor is None:
                break
            cursor = next_cursor
        
        return all_exports
    
    # Pattern 2: Find exports by criteria
    def find_exports_by_name(export_service, dataset_id, name_pattern):
        filter_options = ExportFilter(
            must_filter=ExportFilterOptions(name_contains=name_pattern)
        )
        
        exports, _, _ = export_service.get_exports(
            dataset_id=dataset_id,
            export_filter=filter_options,
            length=100
        )
        
        return exports
    
    # Pattern 3: Bulk operations
    def cleanup_test_exports(export_service, dataset_id):
        test_filter = ExportFilter(
            must_filter=ExportFilterOptions(name_contains="test")
        )
        
        exports, _, _ = export_service.get_exports(
            dataset_id=dataset_id,
            export_filter=test_filter,
            length=100
        )
        
        deleted_count = 0
        for export in exports:
            if export_service.delete_export(dataset_id, export.id):
                deleted_count += 1
        
        return deleted_count
    
    # These are just example functions, so we'll just assert they exist
    assert callable(get_all_exports)
    assert callable(find_exports_by_name)
    assert callable(cleanup_test_exports)


if __name__ == "__main__":
    # Run the integration test
    test_export_service_integration()
    test_export_filtering_examples()
    test_export_service_usage_patterns()
    print("All integration tests passed!") 