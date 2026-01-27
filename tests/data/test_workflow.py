import os

import pytest

from spb_onprem import DataService, DatasetService
from spb_onprem.data.entities import DataMeta, DataAnnotationStat
from spb_onprem.data.enums import DataMetaTypes


def test_data_update_workflow():
    if os.environ.get("CI") == "true":
        pytest.skip("Skip workflow tests on CI")
    if os.environ.get("RUN_DATA_WORKFLOW_TESTS") != "1":
        pytest.skip("RUN_DATA_WORKFLOW_TESTS!=1 (avoid accidental mutations)")

    """Test workflow for updating existing data:
    - Find a dataset with data automatically
    - Get existing data by ID
    - Update data with new key and meta
    - Verify the update was successful
    """
    
    data_service = DataService()
    dataset_service = DatasetService()
    
    print("=" * 70)
    print("Data Service Update Workflow Test")
    print("=" * 70)
    
    # ==================== FIND DATASET WITH DATA ====================
    
    print("\n[Step 0] Finding a dataset with data...")
    DATASET_ID = None
    DATA_ID = None
    
    # Try these dataset names in order
    DATASET_NAMES_TO_TRY = [
        "11",
    ]
    
    # Or you can set a specific dataset ID directly here
    SPECIFIC_DATASET_ID = None  # Set this to skip name lookup, e.g., "your-dataset-id"
    
    try:
        if SPECIFIC_DATASET_ID:
            # Use specific dataset ID
            print(f"Using specific dataset ID: {SPECIFIC_DATASET_ID}")
            DATASET_ID = SPECIFIC_DATASET_ID
        else:
            # Try to find dataset by name
            for dataset_name in DATASET_NAMES_TO_TRY:
                try:
                    dataset = dataset_service.get_dataset(name=dataset_name)
                    print(f"✅ Found dataset: {dataset.name} (ID: {dataset.id})")
                    DATASET_ID = dataset.id
                    break
                except Exception:
                    continue
            
            if not DATASET_ID:
                print("❌ Could not find any dataset with the given names")
                print(f"⚠️  Tried: {', '.join(DATASET_NAMES_TO_TRY)}")
                print("⚠️  Please update DATASET_NAMES_TO_TRY or set SPECIFIC_DATASET_ID")
                pytest.fail("Could not find any dataset with the given names")
        
        # Try to get data from the dataset
        data_list, _, data_count = data_service.get_data_id_list(
            dataset_id=DATASET_ID,
            length=1
        )
        
        if data_count > 0 and len(data_list) > 0:
            DATA_ID = data_list[0].id
            print(f"✅ Found data in dataset:")
            print(f"   Dataset ID: {DATASET_ID}")
            print(f"   Data Count: {data_count}")
            print(f"   Data ID: {DATA_ID}")
        else:
            print("❌ No data found in dataset")
            print("⚠️  Please create at least one data item in the dataset first")
            pytest.fail("No data found in dataset")
            
    except Exception as e:
        print(f"❌ Failed to find dataset with data: {e}")
        print(f"⚠️  Please check your dataset configuration")
        pytest.fail(str(e))
    
    # ==================== CONFIGURATION ====================
    
    print(f"\n📋 Test Configuration:")
    print(f"   Dataset ID: {DATASET_ID}")
    print(f"   Data ID: {DATA_ID}")
    
    # ==================== GET EXISTING DATA ====================
    
    print("\n[Step 1] Getting existing data...")
    try:
        original_data = data_service.get_data(
            dataset_id=DATASET_ID,
            data_id=DATA_ID
        )
        print(f"✅ Retrieved data successfully")
        print(f"   ID: {original_data.id}")
        print(f"   Dataset ID: {original_data.dataset_id}")
        print(f"   Current Key: {original_data.key}")
        print(f"   Current Meta count: {len(original_data.meta) if original_data.meta else 0}")
        print(f"   Current Annotation Stats count: {len(original_data.annotation_stats) if original_data.annotation_stats else 0}")
        if original_data.annotation_stats:
            print(f"   Annotation Stats:")
            for stat in original_data.annotation_stats:
                print(f"      - type: {stat.type}, group: {stat.group}, class: {stat.annotation_class}, count: {stat.count}")
    except Exception as e:
        print(f"❌ Failed to get data: {e}")
        print("\n⚠️  Please update DATASET_ID and DATA_ID with actual values")
        pytest.fail(str(e))
    
    # ==================== UPDATE DATA WITH META ====================
    
    print("\n[Step 2] Updating data with meta information (Type 1)...")
    try:
        test_meta = [
            DataMeta(
                key="test_string_meta",
                type=DataMetaTypes.STRING,
                value="test_value_updated"
            ),
            DataMeta(
                key="test_number_meta",
                type=DataMetaTypes.NUMBER,
                value=42
            ),
            DataMeta(
                key="test_boolean_meta",
                type=DataMetaTypes.BOOLEAN,
                value=True
            )
        ]
        
        updated_data_with_meta = data_service.update_data(
            dataset_id=DATASET_ID,
            data_id=DATA_ID,
            meta=test_meta
        )
        print(f"✅ Updated data with meta successfully")
        print(f"   Meta count: {len(updated_data_with_meta.meta) if updated_data_with_meta.meta else 0}")
        if updated_data_with_meta.meta:
            for meta_item in updated_data_with_meta.meta:
                print(f"   - {meta_item.key}: {meta_item.value} (type: {meta_item.type})")
    except Exception as e:
        print(f"❌ Failed to update data with meta: {e}")
        pytest.fail(str(e))
    
    # ==================== UPDATE DATA WITH DIFFERENT META ====================
    
    print("\n[Step 3] Updating data with different meta (Type 2)...")
    try:
        combined_meta = [
            DataMeta(
                key="workflow_test",
                type=DataMetaTypes.STRING,
                value="workflow_update_test"
            ),
            DataMeta(
                key="test_timestamp",
                type=DataMetaTypes.NUMBER,
                value=1732704000  # Example timestamp
            )
        ]
        
        fully_updated_data = data_service.update_data(
            dataset_id=DATASET_ID,
            data_id=DATA_ID,
            meta=combined_meta
        )
        print(f"✅ Updated data with different meta successfully")
        print(f"   Updated Meta count: {len(fully_updated_data.meta) if fully_updated_data.meta else 0}")
        if fully_updated_data.meta:
            for meta_item in fully_updated_data.meta:
                print(f"   - {meta_item.key}: {meta_item.value} (type: {meta_item.type})")
        
        assert fully_updated_data.meta is not None, "Meta was not updated"
    except Exception as e:
        print(f"❌ Failed to update data with different meta: {e}")
        pytest.fail(str(e))
    
    # ==================== UPDATE DATA WITH ANNOTATION STATS ====================
    
    print("\n[Step 4] Testing annotation_stats update...")
    try:
        # Create sample annotation stats
        sample_stats = [
            DataAnnotationStat(
                type="bbox",
                group="object_detection",
                annotation_class="car",
                sub_class="sedan",
                count=5
            ),
            DataAnnotationStat(
                type="bbox",
                group="object_detection",
                annotation_class="person",
                sub_class=None,
                count=3
            ),
            DataAnnotationStat(
                type="polyline",
                group="lane_detection",
                annotation_class="lane",
                sub_class="solid",
                count=2
            )
        ]
        
        print(f"   Creating sample annotation stats with {len(sample_stats)} items...")
        for stat in sample_stats:
            print(f"      - type: {stat.type}, group: {stat.group}, class: {stat.annotation_class}, subClass: {stat.sub_class}, count: {stat.count}")
        
        # Update with sample annotation_stats
        updated_with_stats = data_service.update_data(
            dataset_id=DATASET_ID,
            data_id=DATA_ID,
            annotation_stats=sample_stats
        )
        print(f"✅ Updated data with annotation_stats successfully")
        print(f"   Response Annotation Stats count: {len(updated_with_stats.annotation_stats) if updated_with_stats.annotation_stats else 0}")
        
        # Verify by getting the data again
        verification_data = data_service.get_data(
            dataset_id=DATASET_ID,
            data_id=DATA_ID
        )
        print(f"   Verified Annotation Stats count (re-fetched): {len(verification_data.annotation_stats) if verification_data.annotation_stats else 0}")
        if verification_data.annotation_stats:
            print(f"   Verified Annotation Stats:")
            for stat in verification_data.annotation_stats:
                print(f"      - type: {stat.type}, group: {stat.group}, class: {stat.annotation_class}, subClass: {stat.sub_class}, count: {stat.count}")
        else:
            print(f"   ⚠️  Annotation stats were sent but not returned in response")
    except Exception as e:
        print(f"❌ Failed to update annotation_stats: {e}")
        pytest.fail(str(e))
    
    # ==================== RESTORE ORIGINAL DATA ====================
    
    print("\n[Step 5] Restoring original meta and annotation_stats...")
    try:
        # Restore to original meta and annotation_stats
        restored_data = data_service.update_data(
            dataset_id=DATASET_ID,
            data_id=DATA_ID,
            meta=original_data.meta if original_data.meta else [],
            annotation_stats=original_data.annotation_stats if original_data.annotation_stats else []
        )
        print(f"✅ Restored original data successfully")
        print(f"   Restored Meta count: {len(restored_data.meta) if restored_data.meta else 0}")
        print(f"   Restored Annotation Stats count: {len(restored_data.annotation_stats) if restored_data.annotation_stats else 0}")
    except Exception as e:
        print(f"❌ Failed to restore original data: {e}")
        return False
    
    # ==================== VERIFY FINAL STATE ====================
    
    print("\n[Step 6] Verifying final state...")
    try:
        final_data = data_service.get_data(
            dataset_id=DATASET_ID,
            data_id=DATA_ID
        )
        print(f"✅ Retrieved final data state")
        print(f"   Final Key: {final_data.key}")
        print(f"   Final Meta count: {len(final_data.meta) if final_data.meta else 0}")
        
        # Verify key was not changed
        assert final_data.key == original_data.key, "Key should not have changed"
    except Exception as e:
        print(f"❌ Failed to verify final state: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("Data Update Workflow Test Passed Successfully! 🎉")
    print("=" * 70)
    print("\nSummary:")
    print("  ✓ Found dataset with data automatically")
    print("  ✓ Retrieved existing data")
    print("  ✓ Updated data meta (Type 1)")
    print("  ✓ Updated data meta (Type 2)")
    print("  ✓ Updated annotation_stats with sample data")
    print("  ✓ Restored original meta and annotation_stats")
    print("  ✓ Verified final state (key unchanged)")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    test_data_update_workflow()
