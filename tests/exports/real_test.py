from spb_onprem import (
    DatasetService,
    Dataset,
    ExportService,
    Export,
    ExportFilter,
    ExportFilterOptions,
)
from spb_onprem.data.params import DataListFilter, DataFilterOptions
from spb_onprem.data.enums import DataType


def test_export_service():
    # Initialize services
    dataset_service = DatasetService()
    dataset = dataset_service.get_dataset(
        dataset_id="01JPM6NR1APMBXJNC0YW72S1FN"
    )

    print(f"Dataset: {dataset}")
    
    export_service = ExportService()
    
    # Test 1: Create an export with DataListFilter
    print("\n=== Creating Export ===")
    data_filter = DataListFilter(
        must_filter=DataFilterOptions(key_contains="validation")
    )
    
    new_export = export_service.create_export(
        dataset_id=dataset.id,
        name="SDK Test Export",
        data_filter=data_filter,
        meta={
            "created_by": "sdk_test",
            "purpose": "real_test"
        }
    )
    print(f"Created export: {new_export}")
    
    # Test 2: Get exports with pagination
    print("\n=== Getting Exports ===")
    cursor = None
    all_exports = []
    while True:
        exports, cursor, total_count = export_service.get_exports(
            dataset_id=dataset.id,
            cursor=cursor,
            length=10
        )
        all_exports.extend(exports)
        print(f"Fetched {len(exports)} exports, total: {total_count}")
        
        if cursor is None:
            break
    
    print(f"Total exports found: {len(all_exports)}")
    
    # Test 3: Get exports with filter
    print("\n=== Getting Exports with Filter ===")
    export_filter = ExportFilter(
        must_filter=ExportFilterOptions(
            name_contains="SDK Test"
        )
    )
    
    filtered_exports, _, filtered_count = export_service.get_exports(
        dataset_id=dataset.id,
        export_filter=export_filter,
        length=50
    )
    print(f"Filtered exports: {len(filtered_exports)}, total: {filtered_count}")
    
    # Test 4: Get specific export
    if all_exports:
        print("\n=== Getting Specific Export ===")
        specific_export = export_service.get_export(
            dataset_id=dataset.id,
            export_id=all_exports[0].id
        )
        print(f"Specific export: {specific_export}")
    
    # Test 5: Update the created export with complex DataListFilter
    print("\n=== Updating Export ===")
    complex_data_filter = DataListFilter(
        must_filter=DataFilterOptions(
            key_contains="validation",
            type_in=[DataType.SUPERB_IMAGE]
        ),
        not_filter=DataFilterOptions(
            key_contains="test"
        )
    )
    
    updated_export = export_service.update_export(
        dataset_id=dataset.id,
        export_id=new_export.id,
        name="SDK Test Export - Updated",
        data_filter=complex_data_filter,
        meta={
            "created_by": "sdk_test",
            "purpose": "real_test",
            "updated": True,
            "status": "completed"
        }
    )
    print(f"Updated export: {updated_export}")
    
    # Test 6: Delete the created export
    print("\n=== Deleting Export ===")
    delete_result = export_service.delete_export(
        dataset_id=dataset.id,
        export_id=new_export.id
    )
    print(f"Delete result: {delete_result}")
    
    # Test 7: Verify deletion
    print("\n=== Verifying Deletion ===")
    try:
        deleted_export = export_service.get_export(
            dataset_id=dataset.id,
            export_id=new_export.id
        )
        print(f"Export still exists: {deleted_export}")
    except Exception as e:
        print(f"Export successfully deleted (expected error): {e}")


if __name__ == "__main__":
    test_export_service() 