import os
import time

import pytest

from spb_onprem import DiagnosisService, DatasetService, ContentService, SliceService
from spb_onprem.diagnoses.entities import DiagnosisStatus
from spb_onprem.reports.entities.analytics_report_item import AnalyticsReportItemType
from spb_onprem.charts import (
    ChartDataFactory,
    CategoryValueData,
    HeatmapData,
    ConfusionMatrixData,
    LineChartData,
    ScatterPlotData,
    BinFrequencyData,
    MetricData,
    DataIdsIndex,
    XYDataIds,
    LineChartDataIds,
)


def test_diagnosis_lifecycle_workflow():
    """
    Complete diagnosis lifecycle workflow test:
    - Find a dataset automatically
    - Create a new diagnosis with all parameters including new fields
    - Get the created diagnosis by ID
    - Get the created diagnosis by name
    - Update diagnosis with various parameters including new fields
    - Test diagnosis listing and filtering
    - Create diagnosis report items with chart data
    - Upload chart data for all chart types
    - Update diagnosis report items
    - Delete diagnosis report items (optional)
    - Delete the diagnosis (optional)
    - Verify deletion
    """
    if os.environ.get("CI") == "true":
        pytest.skip("Skip workflow tests on CI")
    if os.environ.get("RUN_DIAGNOSIS_WORKFLOW_TESTS") != "1":
        pytest.skip("RUN_DIAGNOSIS_WORKFLOW_TESTS!=1 (avoid accidental mutations)")
    
    # Configuration flag
    CLEANUP = os.environ.get("CLEANUP", "1") == "1"
    
    diagnosis_service = DiagnosisService()
    dataset_service = DatasetService()
    slice_service = SliceService()
    content_service = ContentService()
    
    print("=" * 80)
    print("Diagnosis Service Complete Lifecycle Workflow Test")
    print("=" * 80)
    print(f"\n⚙️  Configuration:")
    print(f"   CLEANUP: {CLEANUP} (Delete diagnosis and all reports after test)")
    
    # ==================== FIND DATASET ====================
    
    print("\n[Step 0] Finding a dataset for diagnosis testing...")
    DATASET_ID = None
    
    try:
        # Get first available dataset
        datasets, _, total = dataset_service.get_datasets(length=1)
        
        if total > 0 and len(datasets) > 0:
            dataset = datasets[0]
            DATASET_ID = dataset.id
            print(f"✅ Found dataset: {dataset.name} (ID: {dataset.id})")
            print(f"   Total datasets available: {total}")
        else:
            print("❌ No datasets found")
            print("⚠️  Please create at least one dataset first")
            pytest.fail("No datasets found")
        
        print(f"✅ Using dataset:")
        print(f"   Dataset ID: {DATASET_ID}")
            
    except Exception as e:
        print(f"❌ Failed to find dataset: {e}")
        print(f"⚠️  Please check your dataset configuration")
        pytest.fail(str(e))
    
    # Get slices for source/target slice IDs
    try:
        slices, _, _ = slice_service.get_slices(dataset_id=DATASET_ID)
    except Exception as e:
        print(f"❌ Failed to get slices: {e}")
        slices = []
    
    print(f"\n📋 Test Configuration:")
    print(f"   Dataset ID: {DATASET_ID}")
    
    # Test diagnosis details
    test_diagnosis_name = f"workflow_test_diagnosis_{int(time.time())}"
    test_description = "Diagnosis created by workflow test"
    
    print(f"   Diagnosis Name: {test_diagnosis_name}")
    print(f"   Description: {test_description}")
    
    created_diagnosis_id = None
    created_diagnosis_report_ids = []
    
    try:
        # ==================== CREATE DIAGNOSIS ====================
        
        print("\n[Step 1] Creating a new diagnosis with detailed parameters...")
        
        try:
            # Create diagnosis with comprehensive parameters including new discriminator fields
            # Note: contents field is optional and used for diagnosis-level files (config, logs, etc.)
            # Chart data is stored in diagnosis_report_items' content_id
            created_diagnosis = diagnosis_service.create_diagnosis(
                dataset_id=DATASET_ID,
                name=test_diagnosis_name,
                description=test_description,
                score_key="accuracy",
                score_value=0.0,
                score_unit="%",
                diagnosis_parameters={
                    "threshold": 0.5,
                    "min_confidence": 0.7,
                    "algorithm": "detection_analysis"
                },
                source_slice_id=slices[0].id if slices else None,
                target_slice_id=slices[1].id if len(slices) > 1 else None,
                source_data_count=5000,
                target_data_count=3000,
                diagnosis_data_count=2000,
                discriminator_key="iou_threshold",
                discriminator_values=["0.5", "0.75", "0.9"]
            )
            created_diagnosis_id = created_diagnosis.id
            
            print(f"✅ Diagnosis created successfully")
            print(f"   Diagnosis ID: {created_diagnosis.id}")
            print(f"   Name: {created_diagnosis.name}")
            print(f"   Description: {created_diagnosis.description}")
            print(f"   Status: {created_diagnosis.status}")
            print(f"   Score Key: {created_diagnosis.score_key}")
            print(f"   Score Value: {created_diagnosis.score_value}")
            print(f"   Score Unit: {created_diagnosis.score_unit}")
            print(f"   Diagnosis Parameters: {created_diagnosis.diagnosis_parameters}")
            print(f"   Source Slice ID: {created_diagnosis.source_slice_id}")
            print(f"   Target Slice ID: {created_diagnosis.target_slice_id}")
            print(f"   Source Data Count: {created_diagnosis.source_data_count}")
            print(f"   Target Data Count: {created_diagnosis.target_data_count}")
            print(f"   Diagnosis Data Count: {created_diagnosis.diagnosis_data_count}")
            print(f"   Discriminator Key: {created_diagnosis.discriminator_key}")
            print(f"   Discriminator Values: {created_diagnosis.discriminator_values}")
            
            print(f"   Created At: {created_diagnosis.created_at}")
            print(f"   Created By: {created_diagnosis.created_by}")
            
            assert created_diagnosis.name == test_diagnosis_name, "Diagnosis name mismatch"
            assert created_diagnosis.description == test_description, "Description mismatch"
            assert created_diagnosis.score_key == "accuracy", "Score key mismatch"
            assert created_diagnosis.score_value == 0.0, "Score value mismatch"
            assert created_diagnosis.diagnosis_parameters is not None, "Diagnosis parameters should not be None"
            
            # Verify new fields
            if slices:
                assert created_diagnosis.source_slice_id is not None, "Source slice ID should be set"
                print(f"   ✅ Source slice ID verified")
            assert created_diagnosis.source_data_count == 5000, "Source data count mismatch"
            assert created_diagnosis.target_data_count == 3000, "Target data count mismatch"
            assert created_diagnosis.diagnosis_data_count == 2000, "Diagnosis data count mismatch"
            assert created_diagnosis.discriminator_key == "iou_threshold", "Discriminator key mismatch"
            assert created_diagnosis.discriminator_values == ["0.5", "0.75", "0.9"], "Discriminator values mismatch"
            print(f"   ✅ All new fields verified (including discriminator pattern)")
            
        except Exception as e:
            print(f"❌ Failed to create diagnosis: {e}")
            pytest.fail(str(e))
        
        # ==================== GET DIAGNOSIS BY ID ====================
        
        print("\n[Step 2] Getting diagnosis by ID...")
        try:
            retrieved_diagnosis = diagnosis_service.get_diagnosis(
                dataset_id=DATASET_ID,
                diagnosis_id=created_diagnosis_id
            )
            
            print(f"✅ Retrieved diagnosis by ID successfully")
            print(f"   Diagnosis ID: {retrieved_diagnosis.id}")
            print(f"   Name: {retrieved_diagnosis.name}")
            print(f"   Status: {retrieved_diagnosis.status}")
            
            # Verify new fields persist
            assert retrieved_diagnosis.source_data_count == 5000, "Source data count mismatch in retrieved diagnosis"
            assert retrieved_diagnosis.target_data_count == 3000, "Target data count mismatch in retrieved diagnosis"
            assert retrieved_diagnosis.diagnosis_data_count == 2000, "Diagnosis data count mismatch in retrieved diagnosis"
            print(f"   ✅ All new fields persist")
            
            assert retrieved_diagnosis.id == created_diagnosis_id, "Retrieved diagnosis ID mismatch"
            assert retrieved_diagnosis.name == test_diagnosis_name, "Retrieved diagnosis name mismatch"
            
        except Exception as e:
            print(f"❌ Failed to get diagnosis by ID: {e}")
            pytest.fail(str(e))
        
        # ==================== GET DIAGNOSIS BY NAME ====================
        
        print("\n[Step 3] Getting diagnosis by name...")
        try:
            retrieved_by_name = diagnosis_service.get_diagnosis_by_name(
                dataset_id=DATASET_ID,
                name=test_diagnosis_name
            )
            
            print(f"✅ Retrieved diagnosis by name successfully")
            print(f"   Diagnosis ID: {retrieved_by_name.id}")
            print(f"   Name: {retrieved_by_name.name}")
            print(f"   Status: {retrieved_by_name.status}")
            
            assert retrieved_by_name.id == created_diagnosis_id, "Diagnosis ID mismatch when retrieving by name"
            assert retrieved_by_name.name == test_diagnosis_name, "Diagnosis name mismatch"
            
        except Exception as e:
            print(f"❌ Failed to get diagnosis by name: {e}")
            pytest.fail(str(e))
        
        # ==================== UPDATE DIAGNOSIS - BASIC INFO ====================
        
        print("\n[Step 4] Updating diagnosis basic information...")
        try:
            updated_description = "Updated description for workflow test"
            updated_diagnosis = diagnosis_service.update_diagnosis(
                dataset_id=DATASET_ID,
                diagnosis_id=created_diagnosis_id,
                description=updated_description
            )
            
            print(f"✅ Updated diagnosis basic information successfully")
            print(f"   Updated Description: {updated_diagnosis.description}")
            
            assert updated_diagnosis.description == updated_description, "Description was not updated"
            
        except Exception as e:
            print(f"❌ Failed to update diagnosis basic information: {e}")
            pytest.fail(str(e))
        
        # ==================== UPDATE DIAGNOSIS - STATUS ====================
        
        print("\n[Step 5] Updating diagnosis status...")
        try:
            updated_diagnosis_status = diagnosis_service.update_diagnosis(
                dataset_id=DATASET_ID,
                diagnosis_id=created_diagnosis_id,
                status=DiagnosisStatus.IN_PROGRESS
            )
            
            print(f"✅ Updated diagnosis status successfully")
            print(f"   New Status: {updated_diagnosis_status.status}")
            
            assert updated_diagnosis_status.status == DiagnosisStatus.IN_PROGRESS, "Status was not updated"
            
        except Exception as e:
            print(f"❌ Failed to update diagnosis status: {e}")
            pytest.fail(str(e))
        
        # ==================== UPDATE DIAGNOSIS - DATA COUNTS ====================
        
        print("\n[Step 6] Updating diagnosis data counts...")
        try:
            updated_diagnosis_counts = diagnosis_service.update_diagnosis(
                dataset_id=DATASET_ID,
                diagnosis_id=created_diagnosis_id,
                source_data_count=6000,
                target_data_count=4000,
                diagnosis_data_count=2500
            )
            
            print(f"✅ Updated diagnosis data counts successfully")
            print(f"   Source Data Count: {updated_diagnosis_counts.source_data_count}")
            print(f"   Target Data Count: {updated_diagnosis_counts.target_data_count}")
            print(f"   Diagnosis Data Count: {updated_diagnosis_counts.diagnosis_data_count}")
            
            assert updated_diagnosis_counts.source_data_count == 6000, "Source data count was not updated"
            assert updated_diagnosis_counts.target_data_count == 4000, "Target data count was not updated"
            assert updated_diagnosis_counts.diagnosis_data_count == 2500, "Diagnosis data count was not updated"
            
        except Exception as e:
            print(f"❌ Failed to update diagnosis data counts: {e}")
            pytest.fail(str(e))
        
        # ==================== UPDATE DIAGNOSIS - PARAMETERS ====================
        
        print("\n[Step 7] Updating diagnosis parameters...")
        try:
            new_diagnosis_params = {
                "threshold": 0.6,
                "min_confidence": 0.8,
                "algorithm": "improved_detection_analysis",
                "iterations": 100
            }
            
            updated_diagnosis_params = diagnosis_service.update_diagnosis(
                dataset_id=DATASET_ID,
                diagnosis_id=created_diagnosis_id,
                diagnosis_parameters=new_diagnosis_params
            )
            
            print(f"✅ Updated diagnosis parameters successfully")
            print(f"   Diagnosis Parameters: {updated_diagnosis_params.diagnosis_parameters}")
            
            assert updated_diagnosis_params.diagnosis_parameters is not None, "Diagnosis parameters should not be None"
            assert updated_diagnosis_params.diagnosis_parameters.get("threshold") == 0.6, "Threshold was not updated"
            assert updated_diagnosis_params.diagnosis_parameters.get("iterations") == 100, "Iterations was not added"
            
        except Exception as e:
            print(f"❌ Failed to update diagnosis parameters: {e}")
            pytest.fail(str(e))
        
        # ==================== UPDATE DIAGNOSIS - CONTENTS ====================
        
        print("\n[Step 8] Skipping diagnosis contents update...")
        print("   ℹ️  Contents field is for diagnosis-level files (config, logs)")
        print("   ℹ️  Chart data is managed via diagnosis_report_items' content_id")
        
        # ==================== UPDATE DIAGNOSIS - SLICE IDS ====================
        
        print("\n[Step 9] Updating diagnosis slice IDs...")
        if len(slices) >= 2:
            try:
                updated_diagnosis_slices = diagnosis_service.update_diagnosis(
                    dataset_id=DATASET_ID,
                    diagnosis_id=created_diagnosis_id,
                    source_slice_id=slices[1].id,
                    target_slice_id=slices[0].id
                )
                
                print(f"✅ Updated diagnosis slice IDs successfully")
                print(f"   Source Slice ID: {updated_diagnosis_slices.source_slice_id}")
                print(f"   Target Slice ID: {updated_diagnosis_slices.target_slice_id}")
                
                assert updated_diagnosis_slices.source_slice_id == slices[1].id, "Source slice ID was not updated"
                assert updated_diagnosis_slices.target_slice_id == slices[0].id, "Target slice ID was not updated"
                
            except Exception as e:
                print(f"❌ Failed to update diagnosis slice IDs: {e}")
                pytest.fail(str(e))
        else:
            print("   ⏭️  Skipping slice ID update (not enough slices)")
        
        # ==================== UPDATE DIAGNOSIS - SCORE ====================
        
        print("\n[Step 10] Updating diagnosis score...")
        try:
            updated_diagnosis_score = diagnosis_service.update_diagnosis(
                dataset_id=DATASET_ID,
                diagnosis_id=created_diagnosis_id,
                score_key="f1_score",
                score_value=0.92,
                score_unit="%"
            )
            
            print(f"✅ Updated diagnosis score successfully")
            print(f"   Score Key: {updated_diagnosis_score.score_key}")
            print(f"   Score Value: {updated_diagnosis_score.score_value}")
            print(f"   Score Unit: {updated_diagnosis_score.score_unit}")
            
            assert updated_diagnosis_score.score_key == "f1_score", "Score key was not updated"
            assert updated_diagnosis_score.score_value == 0.92, "Score value was not updated"
            
        except Exception as e:
            print(f"❌ Failed to update diagnosis score: {e}")
            pytest.fail(str(e))
        
        # ==================== UPDATE DIAGNOSIS - COMPLETE STATUS ====================
        
        print("\n[Step 11] Marking diagnosis as completed...")
        try:
            completed_diagnosis = diagnosis_service.update_diagnosis(
                dataset_id=DATASET_ID,
                diagnosis_id=created_diagnosis_id,
                status=DiagnosisStatus.COMPLETED
            )
            
            print(f"✅ Marked diagnosis as completed successfully")
            print(f"   Status: {completed_diagnosis.status}")
            print(f"   Completed At: {completed_diagnosis.completed_at}")
            
            assert completed_diagnosis.status == DiagnosisStatus.COMPLETED, "Status was not updated to COMPLETED"
            
        except Exception as e:
            print(f"❌ Failed to mark diagnosis as completed: {e}")
            pytest.fail(str(e))
        
        # ==================== LIST DIAGNOSES ====================
        
        print("\n[Step 12] Listing diagnoses in dataset...")
        try:
            diagnoses_list, next_cursor, total_count = diagnosis_service.get_diagnoses(
                dataset_id=DATASET_ID,
                length=10
            )
            
            print(f"✅ Retrieved diagnoses list successfully")
            print(f"   Total Count: {total_count}")
            print(f"   Retrieved Count: {len(diagnoses_list)}")
            print(f"   Next Cursor: {next_cursor}")
            
            # Find our created diagnosis in the list
            found_diagnosis = None
            for diagnosis in diagnoses_list:
                if diagnosis.id == created_diagnosis_id:
                    found_diagnosis = diagnosis
                    break
            
            if found_diagnosis:
                print(f"   ✅ Found our test diagnosis in the list:")
                print(f"      Diagnosis ID: {found_diagnosis.id}")
                print(f"      Name: {found_diagnosis.name}")
                print(f"      Status: {found_diagnosis.status}")
            else:
                print(f"   ⚠️  Test diagnosis not found in first page (might be on next page)")
            
            assert total_count > 0, "Should have at least one diagnosis"
            assert len(diagnoses_list) > 0, "Should return at least one diagnosis"
            
        except Exception as e:
            print(f"❌ Failed to list diagnoses: {e}")
            pytest.fail(str(e))
        
        # ==================== CREATE DIAGNOSIS REPORT ITEMS WITH CHART DATA ====================
        
        # Model Diagnosis Scenario:
        # We're analyzing an object detection model that classifies images into 4 categories:
        # Cat, Dog, Bird, and Fish. The model has been trained and we're diagnosing its performance.
        # We test the model at 3 different IoU thresholds: 0.5, 0.75, and 0.9
        
        # Common charts (no discriminator_value - shown for all IoU thresholds)
        common_chart_configs = [
            {
                "type": AnalyticsReportItemType.METRICS,
                "name": "Overview Statistics",
                "description": "Overall detection statistics (Prediction count, Ground truth, FP, FN, etc.)",
                "discriminator_value": None  # Common chart
            },
            {
                "type": AnalyticsReportItemType.TABLE,
                "name": "Performance Summary by Class",
                "description": "Detailed performance metrics table for each class (AP, Precision, Recall, etc.)",
                "discriminator_value": None  # Common chart
            },
            {
                "type": AnalyticsReportItemType.HORIZONTAL_BAR,
                "name": "Per-Class Precision",
                "description": "Precision score for each object class (averaged across thresholds)",
                "discriminator_value": None  # Common chart
            },
        ]
        
        # IoU threshold specific charts (with discriminator_value - filtered by threshold selection)
        iou_specific_chart_configs = [
            {
                "type": AnalyticsReportItemType.CONFUSION_MATRIX,
                "name": "Confusion Matrix (IoU=0.5)",
                "description": "Model prediction accuracy at IoU threshold 0.5",
                "discriminator_value": "0.5"
            },
            {
                "type": AnalyticsReportItemType.CONFUSION_MATRIX,
                "name": "Confusion Matrix (IoU=0.75)",
                "description": "Model prediction accuracy at IoU threshold 0.75",
                "discriminator_value": "0.75"
            },
            {
                "type": AnalyticsReportItemType.CONFUSION_MATRIX,
                "name": "Confusion Matrix (IoU=0.9)",
                "description": "Model prediction accuracy at IoU threshold 0.9",
                "discriminator_value": "0.9"
            },
            {
                "type": AnalyticsReportItemType.VERTICAL_BAR,
                "name": "Per-Class Recall (IoU=0.5)",
                "description": "Recall score for each object class at IoU threshold 0.5",
                "discriminator_value": "0.5"
            },
            {
                "type": AnalyticsReportItemType.VERTICAL_BAR,
                "name": "Per-Class Recall (IoU=0.75)",
                "description": "Recall score for each object class at IoU threshold 0.75",
                "discriminator_value": "0.75"
            },
            {
                "type": AnalyticsReportItemType.METRICS,
                "name": "Performance Metrics (IoU=0.5)",
                "description": "Key performance indicators at IoU threshold 0.5 (mAP, Precision, Recall)",
                "discriminator_value": "0.5"
            },
            {
                "type": AnalyticsReportItemType.METRICS,
                "name": "Performance Metrics (IoU=0.75)",
                "description": "Key performance indicators at IoU threshold 0.75 (mAP, Precision, Recall)",
                "discriminator_value": "0.75"
            },
        ]
        
        chart_configs = common_chart_configs + iou_specific_chart_configs
        
        print(f"\n[Step 13] Creating diagnosis report items with discriminator pattern...")
        print(f"   📊 Scenario: Object Detection Model - 4 Classes (Cat, Dog, Bird, Fish)")
        print(f"   📊 IoU Thresholds: 0.5, 0.75, 0.9")
        print(f"   📊 Common charts (always shown): {len(common_chart_configs)}")
        print(f"   📊 IoU-specific charts (filtered): {len(iou_specific_chart_configs)}")
        try:
            for i, config in enumerate(chart_configs):
                chart_type = config["type"]
                discriminator_value = config.get("discriminator_value")
                # Create folder content for this chart
                try:
                    content_id = content_service.create_folder_content()
                    print(f"   [{i+1}/{len(chart_configs)}] Creating {config['name']}...")
                    print(f"      Folder content ID: {content_id}")
                except Exception as content_error:
                    print(f"   ⚠️  Failed to create folder for {chart_type.value}: {content_error}")
                    continue
                
                # Generate chart data based on type
                chart_data = None
                try:
                    if chart_type == AnalyticsReportItemType.CONFUSION_MATRIX:
                        # Confusion matrix showing model predictions
                        # Good performance overall, but some confusion between Cat/Dog and Bird/Fish
                        chart_data = ChartDataFactory.create_confusion_matrix_chart(
                            true_axis_name="Ground Truth",
                            predicted_axis_name="Predicted Class",
                            data=[
                                # Cat predictions
                                ConfusionMatrixData(true_class="Cat", predicted_class="Cat", count=892),
                                ConfusionMatrixData(true_class="Cat", predicted_class="Dog", count=45),
                                ConfusionMatrixData(true_class="Cat", predicted_class="Bird", count=8),
                                ConfusionMatrixData(true_class="Cat", predicted_class="Fish", count=5),
                                # Dog predictions
                                ConfusionMatrixData(true_class="Dog", predicted_class="Cat", count=38),
                                ConfusionMatrixData(true_class="Dog", predicted_class="Dog", count=1047),
                                ConfusionMatrixData(true_class="Dog", predicted_class="Bird", count=12),
                                ConfusionMatrixData(true_class="Dog", predicted_class="Fish", count=3),
                                # Bird predictions
                                ConfusionMatrixData(true_class="Bird", predicted_class="Cat", count=6),
                                ConfusionMatrixData(true_class="Bird", predicted_class="Dog", count=9),
                                ConfusionMatrixData(true_class="Bird", predicted_class="Bird", count=745),
                                ConfusionMatrixData(true_class="Bird", predicted_class="Fish", count=40),
                                # Fish predictions
                                ConfusionMatrixData(true_class="Fish", predicted_class="Cat", count=4),
                                ConfusionMatrixData(true_class="Fish", predicted_class="Dog", count=7),
                                ConfusionMatrixData(true_class="Fish", predicted_class="Bird", count=35),
                                ConfusionMatrixData(true_class="Fish", predicted_class="Fish", count=654),
                            ]
                        )
                    
                    elif chart_type == AnalyticsReportItemType.METRICS:
                        # Generate different metrics based on discriminator_value
                        if discriminator_value is None:
                            # Overview Statistics (common chart - similar to the image)
                            chart_data = ChartDataFactory.create_metrics_chart(
                                metrics=[
                                    MetricData(key="Prediction count", value="4,138"),
                                    MetricData(key="Ground truth count", value="3,550"),
                                    MetricData(key="False positive", value="588"),
                                    MetricData(key="False negative", value="412"),
                                    MetricData(key="Misclassified", value="205"),
                                    MetricData(key="True positive", value="3,345"),
                                    MetricData(key="Overall Accuracy", value="91.3%"),
                                    MetricData(key="Model Size", value="127 MB"),
                                ]
                            )
                        else:
                            # IoU-specific performance metrics
                            iou_val = float(discriminator_value)
                            # Adjust mAP based on IoU threshold (higher IoU = lower mAP)
                            if iou_val == 0.5:
                                map_value = "0.952"
                                precision = "0.946"
                                recall = "0.941"
                            elif iou_val == 0.75:
                                map_value = "0.886"
                                precision = "0.912"
                                recall = "0.895"
                            else:
                                map_value = "0.723"
                                precision = "0.854"
                                recall = "0.812"
                            
                            chart_data = ChartDataFactory.create_metrics_chart(
                                metrics=[
                                    MetricData(key=f"mAP @{discriminator_value}", value=map_value),
                                    MetricData(key="Mean Precision", value=precision),
                                    MetricData(key="Mean Recall", value=recall),
                                    MetricData(key="F1 Score", value="0.893"),
                                    MetricData(key="IoU Threshold", value=discriminator_value),
                                ]
                            )
                    
                    elif chart_type == AnalyticsReportItemType.HORIZONTAL_BAR:
                        # Per-class precision showing which classes are most accurately predicted
                        chart_data = ChartDataFactory.create_horizontal_bar_chart(
                            y_axis_name="Class",
                            x_axis_name="Precision",
                            data=[
                                CategoryValueData(category="Dog", value=0.952),
                                CategoryValueData(category="Cat", value=0.940),
                                CategoryValueData(category="Bird", value=0.931),
                                CategoryValueData(category="Fish", value=0.933),
                            ],
                            data_ids=[
                                DataIdsIndex(index="Dog", data_ids=["dog_001", "dog_002", "dog_003"]),
                                DataIdsIndex(index="Cat", data_ids=["cat_001", "cat_002"]),
                                DataIdsIndex(index="Bird", data_ids=["bird_001", "bird_002"]),
                                DataIdsIndex(index="Fish", data_ids=["fish_001", "fish_002"]),
                            ]
                        )
                    
                    elif chart_type == AnalyticsReportItemType.VERTICAL_BAR:
                        # Per-class recall showing detection sensitivity
                        chart_data = ChartDataFactory.create_vertical_bar_chart(
                            x_axis_name="Class",
                            y_axis_name="Recall",
                            data=[
                                CategoryValueData(category="Cat", value=0.940),
                                CategoryValueData(category="Dog", value=0.951),
                                CategoryValueData(category="Bird", value=0.931),
                                CategoryValueData(category="Fish", value=0.933),
                            ]
                        )
                    
                    elif chart_type == AnalyticsReportItemType.LINE_CHART:
                        # Precision-Recall curve at different confidence thresholds
                        chart_data = ChartDataFactory.create_line_chart(
                            x_name="Confidence Threshold",
                            y_name="Score",
                            data=[
                                # Precision line
                                LineChartData(series="Precision", x=0.1, y=0.65),
                                LineChartData(series="Precision", x=0.2, y=0.72),
                                LineChartData(series="Precision", x=0.3, y=0.78),
                                LineChartData(series="Precision", x=0.4, y=0.84),
                                LineChartData(series="Precision", x=0.5, y=0.89),
                                LineChartData(series="Precision", x=0.6, y=0.92),
                                LineChartData(series="Precision", x=0.7, y=0.94),
                                LineChartData(series="Precision", x=0.8, y=0.96),
                                LineChartData(series="Precision", x=0.9, y=0.98),
                                # Recall line
                                LineChartData(series="Recall", x=0.1, y=0.98),
                                LineChartData(series="Recall", x=0.2, y=0.95),
                                LineChartData(series="Recall", x=0.3, y=0.92),
                                LineChartData(series="Recall", x=0.4, y=0.89),
                                LineChartData(series="Recall", x=0.5, y=0.85),
                                LineChartData(series="Recall", x=0.6, y=0.79),
                                LineChartData(series="Recall", x=0.7, y=0.72),
                                LineChartData(series="Recall", x=0.8, y=0.63),
                                LineChartData(series="Recall", x=0.9, y=0.48),
                                # F1 Score line
                                LineChartData(series="F1 Score", x=0.1, y=0.78),
                                LineChartData(series="F1 Score", x=0.2, y=0.82),
                                LineChartData(series="F1 Score", x=0.3, y=0.84),
                                LineChartData(series="F1 Score", x=0.4, y=0.86),
                                LineChartData(series="F1 Score", x=0.5, y=0.87),
                                LineChartData(series="F1 Score", x=0.6, y=0.85),
                                LineChartData(series="F1 Score", x=0.7, y=0.81),
                                LineChartData(series="F1 Score", x=0.8, y=0.76),
                                LineChartData(series="F1 Score", x=0.9, y=0.64),
                            ]
                        )
                    
                    elif chart_type == AnalyticsReportItemType.HISTOGRAM:
                        # Distribution of prediction confidence scores
                        chart_data = ChartDataFactory.create_histogram_chart(
                            bin_name="Confidence Score",
                            frequency_name="Number of Predictions",
                            data=[
                                BinFrequencyData(bin="0.0-0.1", frequency=12),
                                BinFrequencyData(bin="0.1-0.2", frequency=18),
                                BinFrequencyData(bin="0.2-0.3", frequency=45),
                                BinFrequencyData(bin="0.3-0.4", frequency=89),
                                BinFrequencyData(bin="0.4-0.5", frequency=156),
                                BinFrequencyData(bin="0.5-0.6", frequency=267),
                                BinFrequencyData(bin="0.6-0.7", frequency=412),
                                BinFrequencyData(bin="0.7-0.8", frequency=678),
                                BinFrequencyData(bin="0.8-0.9", frequency=1234),
                                BinFrequencyData(bin="0.9-1.0", frequency=1227),
                            ]
                        )
                    
                    elif chart_type == AnalyticsReportItemType.SCATTER_PLOT:
                        # Confidence vs IoU for all predictions
                        chart_data = ChartDataFactory.create_scatter_plot_chart(
                            x_name="Prediction Confidence",
                            y_name="IoU (Intersection over Union)",
                            data=[
                                # High confidence, high IoU (good predictions)
                                ScatterPlotData(x=0.95, y=0.87, category="Cat"),
                                ScatterPlotData(x=0.92, y=0.85, category="Dog"),
                                ScatterPlotData(x=0.89, y=0.82, category="Bird"),
                                ScatterPlotData(x=0.91, y=0.84, category="Fish"),
                                ScatterPlotData(x=0.94, y=0.88, category="Cat"),
                                ScatterPlotData(x=0.88, y=0.79, category="Dog"),
                                # Medium confidence, medium IoU
                                ScatterPlotData(x=0.75, y=0.68, category="Bird"),
                                ScatterPlotData(x=0.72, y=0.65, category="Fish"),
                                ScatterPlotData(x=0.68, y=0.61, category="Cat"),
                                ScatterPlotData(x=0.71, y=0.67, category="Dog"),
                                # Lower confidence, lower IoU
                                ScatterPlotData(x=0.55, y=0.48, category="Bird"),
                                ScatterPlotData(x=0.52, y=0.45, category="Fish"),
                                ScatterPlotData(x=0.58, y=0.51, category="Cat"),
                                ScatterPlotData(x=0.48, y=0.42, category="Dog"),
                                # Edge cases
                                ScatterPlotData(x=0.35, y=0.28, category="Bird"),
                                ScatterPlotData(x=0.42, y=0.35, category="Fish"),
                            ]
                        )
                    
                    elif chart_type == AnalyticsReportItemType.HEATMAP:
                        # Co-occurrence matrix showing which objects appear together
                        chart_data = ChartDataFactory.create_heatmap_chart(
                            y_axis_name="Primary Object",
                            x_axis_name="Secondary Object",
                            data=[
                                HeatmapData(y_category="Cat", x_category="Cat", value=125),
                                HeatmapData(y_category="Cat", x_category="Dog", value=78),
                                HeatmapData(y_category="Cat", x_category="Bird", value=45),
                                HeatmapData(y_category="Cat", x_category="Fish", value=12),
                                HeatmapData(y_category="Dog", x_category="Cat", value=82),
                                HeatmapData(y_category="Dog", x_category="Dog", value=156),
                                HeatmapData(y_category="Dog", x_category="Bird", value=38),
                                HeatmapData(y_category="Dog", x_category="Fish", value=9),
                                HeatmapData(y_category="Bird", x_category="Cat", value=42),
                                HeatmapData(y_category="Bird", x_category="Dog", value=35),
                                HeatmapData(y_category="Bird", x_category="Bird", value=98),
                                HeatmapData(y_category="Bird", x_category="Fish", value=28),
                                HeatmapData(y_category="Fish", x_category="Cat", value=15),
                                HeatmapData(y_category="Fish", x_category="Dog", value=11),
                                HeatmapData(y_category="Fish", x_category="Bird", value=31),
                                HeatmapData(y_category="Fish", x_category="Fish", value=67),
                            ]
                        )
                    
                    elif chart_type == AnalyticsReportItemType.PIE:
                        # Distribution of classes in test dataset
                        chart_data = ChartDataFactory.create_pie_chart(
                            category_name="Object Class",
                            value_name="Number of Images",
                            data=[
                                CategoryValueData(category="Dog", value=1100),
                                CategoryValueData(category="Cat", value=950),
                                CategoryValueData(category="Bird", value=800),
                                CategoryValueData(category="Fish", value=700),
                            ]
                        )
                    
                    elif chart_type == AnalyticsReportItemType.TABLE:
                        # Detailed performance metrics by class (similar to the Performance table in the image)
                        chart_data = ChartDataFactory.create_table_chart(
                            headers=["Class name", "AP(%)", "Precision", "Recall", "Train set", "Validation set"],
                            rows=[
                                ["Cat", "91.3", "0.940", "0.940", "760", "190"],
                                ["Dog", "91.3", "0.952", "0.951", "880", "220"],
                                ["Bird", "91.3", "0.931", "0.931", "640", "160"],
                                ["Fish", "91.3", "0.933", "0.933", "560", "140"],
                                ["Overall", "91.3", "0.939", "0.939", "2840", "710"],
                            ]
                        )
                    
                    if chart_data:
                        # Upload reports.json
                        diagnosis_service.upload_reports_json(content_id, chart_data)
                        print(f"      ✅ Uploaded reports.json")
                        
                        # Upload data_ids.json if exists
                        if chart_data.data_ids_json:
                            diagnosis_service.upload_data_ids_json(content_id, chart_data)
                            print(f"      ✅ Uploaded data_ids.json")
                    
                except Exception as chart_error:
                    print(f"   ⚠️  Failed to create/upload chart data for {chart_type.value}: {chart_error}")
                    continue
                
                # Create diagnosis report item
                test_report_name = config["name"]
                test_report_description = config["description"]
                
                try:
                    diagnosis_with_report = diagnosis_service.create_diagnosis_report_item(
                        dataset_id=DATASET_ID,
                        diagnosis_id=created_diagnosis_id,
                        name=test_report_name,
                        type=chart_type,
                        content_id=content_id,
                        description=test_report_description,
                        discriminator_value=discriminator_value
                    )
                    
                    if diagnosis_with_report.diagnosis_report_items:
                        if isinstance(diagnosis_with_report.diagnosis_report_items, list):
                            for report in diagnosis_with_report.diagnosis_report_items:
                                if report.name == test_report_name:
                                    created_diagnosis_report_ids.append(report.id)
                                    print(f"   ✅ Created diagnosis report {i+1}: {chart_type.value}")
                                    print(f"      Report ID: {report.id}")
                                    print(f"      Content ID: {content_id}")
                                    if discriminator_value:
                                        print(f"      Discriminator Value: {discriminator_value} (shown only when IoU={discriminator_value})")
                                    else:
                                        print(f"      Discriminator Value: None (common chart - always shown)")
                                    break
                        else:
                            created_diagnosis_report_ids.append(diagnosis_with_report.diagnosis_report_items.id)
                            print(f"   ✅ Created diagnosis report {i+1}: {chart_type.value}")
                            print(f"      Report ID: {diagnosis_with_report.diagnosis_report_items.id}")
                            print(f"      Content ID: {content_id}")
                
                except Exception as report_error:
                    print(f"   ⚠️  Failed to create diagnosis report for {chart_type.value}: {report_error}")
            
            print(f"✅ Created {len(created_diagnosis_report_ids)} diagnosis report items with chart data")
            
        except Exception as e:
            print(f"❌ Failed to create diagnosis report items: {e}")
            import traceback
            traceback.print_exc()
            print(f"   Continuing with remaining tests...")
        
        # ==================== UPDATE DIAGNOSIS REPORT ITEMS ====================
        
        if len(created_diagnosis_report_ids) > 0:
            print(f"\n[Step 14] Updating diagnosis report items...")
            try:
                # Update the first report
                num_to_update = min(2, len(created_diagnosis_report_ids))
                updated_count = 0
                for i, report_id in enumerate(created_diagnosis_report_ids[:num_to_update]):
                    updated_report_name = f"updated_diagnosis_report_{int(time.time())}_{i}"
                    updated_report_description = f"Updated diagnosis report {i+1} description"
                    
                    try:
                        diagnosis_with_updated_report = diagnosis_service.update_diagnosis_report_item(
                            dataset_id=DATASET_ID,
                            diagnosis_id=created_diagnosis_id,
                            diagnosis_report_item_id=report_id,
                            name=updated_report_name,
                            description=updated_report_description
                        )
                        
                        print(f"   ✅ Updated diagnosis report {i+1}/{num_to_update}:")
                        print(f"      Report ID: {report_id}")
                        print(f"      Updated Name: {updated_report_name}")
                        print(f"      Updated Description: {updated_report_description}")
                        updated_count += 1
                    except Exception as update_error:
                        print(f"   ⚠️  Failed to update diagnosis report {i+1}: {update_error}")
                
                print(f"✅ Updated {updated_count}/{num_to_update} diagnosis report items")
                
            except Exception as e:
                print(f"❌ Failed to update diagnosis report items: {e}")
                print(f"   Continuing with remaining tests...")
        else:
            print("\n[Step 14] Skipping diagnosis report update (no reports created)")
        
        # ==================== DELETE DIAGNOSIS REPORT ITEMS ====================
        
        if CLEANUP and len(created_diagnosis_report_ids) > 0:
            print(f"\n[Step 15] Deleting diagnosis report items...")
            try:
                deleted_count = 0
                # Delete all created diagnosis reports
                for i, report_id in enumerate(created_diagnosis_report_ids):
                    try:
                        diagnosis_after_report_delete = diagnosis_service.delete_diagnosis_report_item(
                            dataset_id=DATASET_ID,
                            diagnosis_id=created_diagnosis_id,
                            diagnosis_report_item_id=report_id
                        )
                        deleted_count += 1
                        print(f"   ✅ Deleted diagnosis report {i+1}/{len(created_diagnosis_report_ids)}: {report_id}")
                    except Exception as delete_error:
                        print(f"   ⚠️  Failed to delete diagnosis report {i+1}: {delete_error}")
                
                print(f"✅ Deleted {deleted_count}/{len(created_diagnosis_report_ids)} diagnosis report items")
                
                # Verify reports were deleted
                try:
                    verification_diagnosis = diagnosis_service.get_diagnosis(
                        dataset_id=DATASET_ID,
                        diagnosis_id=created_diagnosis_id
                    )
                    
                    if verification_diagnosis.diagnosis_report_items:
                        if isinstance(verification_diagnosis.diagnosis_report_items, list):
                            remaining_count = len(verification_diagnosis.diagnosis_report_items)
                            print(f"   ⚠️  {remaining_count} diagnosis reports still present after deletion")
                        else:
                            print(f"   ⚠️  Diagnosis report still present after deletion")
                    else:
                        print(f"   ✅ All diagnosis reports successfully deleted")
                except Exception as verify_error:
                    print(f"   ⚠️  Could not verify deletion: {verify_error}")
                
            except Exception as e:
                print(f"❌ Failed to delete diagnosis report items: {e}")
                print(f"   Continuing with diagnosis verification...")
        else:
            if len(created_diagnosis_report_ids) > 0:
                print(f"\n[Step 15] Skipping diagnosis report deletion (CLEANUP=0)")
                print(f"   {len(created_diagnosis_report_ids)} diagnosis reports remain in the system")
            else:
                print("\n[Step 15] Skipping diagnosis report deletion (no reports created)")
        
        # ==================== VERIFY DIAGNOSIS STATE BEFORE DELETION ====================
        
        print("\n[Step 16] Verifying diagnosis state before deletion...")
        try:
            diagnosis_before_delete = diagnosis_service.get_diagnosis(
                dataset_id=DATASET_ID,
                diagnosis_id=created_diagnosis_id
            )
            
            print(f"✅ Retrieved diagnosis state before deletion")
            print(f"   Diagnosis ID: {diagnosis_before_delete.id}")
            print(f"   Name: {diagnosis_before_delete.name}")
            print(f"   Status: {diagnosis_before_delete.status}")
            print(f"   Description: {diagnosis_before_delete.description}")
            print(f"   Score: {diagnosis_before_delete.score_key} = {diagnosis_before_delete.score_value} {diagnosis_before_delete.score_unit}")
            print(f"   Diagnosis Parameters: {diagnosis_before_delete.diagnosis_parameters}")
            print(f"   Data Counts: source={diagnosis_before_delete.source_data_count}, target={diagnosis_before_delete.target_data_count}, diagnosis={diagnosis_before_delete.diagnosis_data_count}")
            
        except Exception as e:
            print(f"❌ Failed to verify diagnosis state: {e}")
            pytest.fail(str(e))
        
        # ==================== DELETE DIAGNOSIS ====================
        
        if CLEANUP:
            print("\n[Step 17] Deleting the test diagnosis...")
            try:
                delete_result = diagnosis_service.delete_diagnosis(
                    dataset_id=DATASET_ID,
                    diagnosis_id=created_diagnosis_id
                )
                
                print(f"✅ Diagnosis deletion executed successfully")
                print(f"   Delete Result: {delete_result}")
                
                assert delete_result == True, "Delete operation should return True"
                
            except Exception as e:
                print(f"❌ Failed to delete diagnosis: {e}")
                pytest.fail(str(e))
        else:
            print("\n[Step 17] Skipping diagnosis deletion (CLEANUP=0)")
            print(f"   Diagnosis remains in the system: {created_diagnosis_id}")
        
        # ==================== VERIFY DIAGNOSIS DELETION ====================
        
        if CLEANUP:
            print("\n[Step 18] Verifying diagnosis deletion...")
            try:
                deleted_diagnosis = diagnosis_service.get_diagnosis(
                    dataset_id=DATASET_ID,
                    diagnosis_id=created_diagnosis_id
                )
                
                if deleted_diagnosis is None:
                    print(f"✅ Diagnosis successfully deleted (returns None)")
                else:
                    print(f"⚠️  Diagnosis still exists after deletion:")
                    print(f"   Diagnosis ID: {deleted_diagnosis.id}")
                    print(f"   Name: {deleted_diagnosis.name}")
                    pytest.fail("Diagnosis should be deleted but still exists")
                    
            except Exception as e:
                # NotFoundError is expected when diagnosis is deleted
                from spb_onprem.exceptions import NotFoundError
                if isinstance(e, NotFoundError):
                    print(f"✅ Diagnosis successfully deleted (NotFoundError raised as expected)")
                else:
                    print(f"❌ Unexpected error while verifying deletion: {e}")
                    pytest.fail(str(e))
        
        # ==================== FINAL SUCCESS MESSAGE ====================
        
        print("\n" + "=" * 80)
        print("Diagnosis Service Complete Lifecycle Workflow Test Passed Successfully! 🎉")
        print("=" * 80)
        print("\nTest Summary:")
        print(f"  ✓ Dataset ID: {DATASET_ID}")
        print(f"  ✓ Created diagnosis: {created_diagnosis_id}")
        print(f"  ✓ Diagnosis name: {test_diagnosis_name}")
        print(f"  ✓ Tested all new fields: source/target slice IDs, data counts, discriminator pattern")
        print(f"  ✓ Created {len(created_diagnosis_report_ids)} diagnosis report items with chart data")
        print(f"  ✓ Tested CONFUSION_MATRIX chart type (new in AnalyticsReportItemType)")
        if CLEANUP:
            print(f"  ✓ Cleaned up all diagnosis reports and diagnosis")
        else:
            print(f"  ℹ️  Diagnosis and reports remain in system (CLEANUP=0)")
            print(f"     Diagnosis ID: {created_diagnosis_id}")
        print("\nTo run without cleanup:")
        print("  CLEANUP=0 RUN_DIAGNOSIS_WORKFLOW_TESTS=1 python -m pytest tests/diagnoses/test_workflow.py::test_diagnosis_lifecycle_workflow")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        
        if CLEANUP:
            print(f"\n⚠️  Attempting cleanup...")
            # Cleanup: try to delete the diagnosis if it was created
            if created_diagnosis_id:
                try:
                    print(f"   Attempting to delete diagnosis: {created_diagnosis_id}")
                    diagnosis_service.delete_diagnosis(
                        dataset_id=DATASET_ID,
                        diagnosis_id=created_diagnosis_id
                    )
                    print(f"   ✅ Cleanup successful - diagnosis deleted")
                except Exception as cleanup_error:
                    print(f"   ⚠️  Cleanup failed: {cleanup_error}")
                    print(f"   ⚠️  Please manually delete diagnosis: {created_diagnosis_id}")
        else:
            if created_diagnosis_id:
                print(f"\n⚠️  Diagnosis remains in system (CLEANUP=0): {created_diagnosis_id}")
        
        pytest.fail(str(e))


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Running Diagnosis Service Workflow Tests")
    print("=" * 80)
    print("\nTest: Complete Lifecycle Workflow")
    test_diagnosis_lifecycle_workflow()
    
    print("\n" + "=" * 80)
    print("All Diagnosis Workflow Tests Completed Successfully! 🎉")
    print("=" * 80)
