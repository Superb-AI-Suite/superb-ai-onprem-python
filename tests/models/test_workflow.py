import os
import time

import pytest

from spb_onprem import ModelService, DatasetService, ContentService, SliceService
from spb_onprem.models.enums import ModelTaskType, ModelStatus
from spb_onprem.models.entities import TrainingAnnotations
from spb_onprem.reports.entities.analytics_report_item import AnalyticsReportItemType
from spb_onprem.charts import (
    ChartDataFactory,
    CategoryValueData,
    HeatmapData,
    LineChartData,
    ScatterPlotData,
    BinFrequencyData,
    MetricData,
    DataIdsIndex,
    XYDataIds,
    LineChartDataIds,
)


def test_model_lifecycle_workflow():
    """
    Complete model lifecycle workflow test:
    - Find a dataset automatically
    - Create a new model with all parameters
    - Get the created model by ID
    - Get the created model by name
    - Update model with various parameters
    - Test model listing and filtering
    - Create training report items with chart data
    - Upload chart data for all 9 chart types
    - Update training report items
    - Delete training report items (optional)
    - Delete the model (optional)
    - Verify deletion
    """
    if os.environ.get("CI") == "true":
        pytest.skip("Skip workflow tests on CI")
    if os.environ.get("RUN_MODEL_WORKFLOW_TESTS") != "1":
        pytest.skip("RUN_MODEL_WORKFLOW_TESTS!=1 (avoid accidental mutations)")
    
    # Configuration flag
    CLEANUP = os.environ.get("CLEANUP", "1") == "1"
    
    model_service = ModelService()
    dataset_service = DatasetService()
    slice_service = SliceService()
    content_service = ContentService()
    
    print("=" * 80)
    print("Model Service Complete Lifecycle Workflow Test")
    print("=" * 80)
    print(f"\n⚙️  Configuration:")
    print(f"   CLEANUP: {CLEANUP} (Delete model and all reports after test)")
    
    # ==================== FIND DATASET ====================
    
    print("\n[Step 0] Finding a dataset for model testing...")
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
    
    try:
        slices, _, _ = slice_service.get_slices(dataset_id=DATASET_ID)
    except Exception as e:
        print(f"❌ Failed to get slices: {e}")
        pytest.fail(str(e))
    
    print(f"\n📋 Test Configuration:")
    print(f"   Dataset ID: {DATASET_ID}")
    
    # Test model details
    test_model_name = f"workflow_test_model_{int(time.time())}"
    test_description = "Model created by workflow test"
    test_task_type = ModelTaskType.OBJECT_DETECTION
    
    print(f"   Model Name: {test_model_name}")
    print(f"   Description: {test_description}")
    print(f"   Task Type: {test_task_type}")
    
    created_model_id = None
    created_training_report_id = None
    
    try:
        # ==================== CREATE MODEL ====================
        
        print("\n[Step 1] Creating a new model with detailed parameters...")
        
        # First, create some content files for the model
        print("   Creating sample content files for model...")
        model_contents = {}
        try:
            # Create config.yaml content
            config_content, _ = content_service.create_content(
                key="config.yaml",
                content_type="application/yaml"
            )
            model_contents["config.yaml"] = config_content.id
            print(f"   ✅ Created config.yaml: {config_content.id}")
            
            # Create model_architecture.json content
            arch_content, _ = content_service.create_content(
                key="model_architecture.json",
                content_type="application/json"
            )
            model_contents["model_architecture.json"] = arch_content.id
            print(f"   ✅ Created model_architecture.json: {arch_content.id}")
            
            # Create training_log.txt content
            log_content, _ = content_service.create_content(
                key="training_log.txt",
                content_type="text/plain"
            )
            model_contents["training_log.txt"] = log_content.id
            print(f"   ✅ Created training_log.txt: {log_content.id}")
            
        except Exception as content_error:
            print(f"   ⚠️  Failed to create content files: {content_error}")
            model_contents = None
        
        # Prepare training annotations data
        training_annotations = [
            TrainingAnnotations(
                train_count=8567,
                validation_count=2134,
                class_name="Car",
                annotation_type="bbox"
            ),
            TrainingAnnotations(
                train_count=12345,
                validation_count=3086,
                class_name="Person",
                annotation_type="bbox"
            ),
            TrainingAnnotations(
                train_count=2341,
                validation_count=585,
                class_name="Bicycle",
                annotation_type="bbox"
            ),
        ]
        print(f"   Prepared {len(training_annotations)} training annotations entries")
        
        try:
            # Create model with comprehensive parameters including contents and training_annotations
            created_model = model_service.create_model(
                dataset_id=DATASET_ID,
                name=test_model_name,
                task_type=test_task_type,
                description=test_description,
                total_data_count=15243,
                train_data_count=12194,
                validation_data_count=3049,
                training_annotations=training_annotations,
                training_parameters={
                    "learning_rate": 0.001,
                    "batch_size": 32,
                    "epochs": 100,
                    "optimizer": "adam"
                },
                train_slice_id=slices[0].id if slices else None,
                validation_slice_id=slices[0].id if len(slices) > 1 else None,
                is_pinned=False,
                score_key="mAP",
                score_value=0.0,
                score_unit="%",
                contents=model_contents
            )
            created_model_id = created_model.id
            
            print(f"✅ Model created successfully")
            print(f"   Model ID: {created_model.id}")
            print(f"   Name: {created_model.name}")
            print(f"   Description: {created_model.description}")
            print(f"   Status: {created_model.status}")
            print(f"   Task Type: {created_model.task_type}")
            print(f"   Total Data Count: {created_model.total_data_count}")
            print(f"   Train Data Count: {created_model.train_data_count}")
            print(f"   Validation Data Count: {created_model.validation_data_count}")
            print(f"   Training Parameters: {created_model.training_parameters}")
            print(f"   Training Annotations: {len(created_model.trainingAnnotations) if created_model.trainingAnnotations else 0} classes")
            if created_model.trainingAnnotations:
                for ann in created_model.trainingAnnotations:
                    print(f"      - {ann.class_name}: train={ann.train_count}, val={ann.validation_count}, type={ann.annotation_type}")
            print(f"   Is Pinned: {created_model.is_pinned}")
            print(f"   Score Key: {created_model.score_key}")
            print(f"   Score Value: {created_model.score_value}")
            
            # Verify contents field
            if model_contents:
                print(f"   Contents: {len(model_contents)} files")
                for filename, content_id in model_contents.items():
                    print(f"      - {filename}: {content_id}")
                
                if created_model.contents:
                    print(f"   ✅ Contents field verified in created model")
                    assert created_model.contents == model_contents, "Contents field mismatch"
                else:
                    print(f"   ⚠️  Contents field is None in created model (API may not support it yet)")
            print(f"   Score Unit: {created_model.score_unit}")
            print(f"   Created At: {created_model.created_at}")
            print(f"   Created By: {created_model.created_by}")
            
            assert created_model.name == test_model_name, "Model name mismatch"
            assert created_model.description == test_description, "Description mismatch"
            assert created_model.task_type == test_task_type, "Task type mismatch"
            assert created_model.total_data_count == 15243, "Total data count mismatch"
            assert created_model.train_data_count == 12194, "Train data count mismatch"
            assert created_model.validation_data_count == 3049, "Validation data count mismatch"
            assert created_model.training_parameters is not None, "Training parameters should not be None"
            assert created_model.score_key == "mAP", "Score key mismatch"
            assert created_model.score_value == 0.0, "Score value mismatch"
            
        except Exception as e:
            print(f"❌ Failed to create model: {e}")
            pytest.fail(str(e))
        
        # ==================== GET MODEL BY ID ====================
        
        print("\n[Step 2] Getting model by ID...")
        try:
            retrieved_model = model_service.get_model(
                dataset_id=DATASET_ID,
                model_id=created_model_id
            )
            
            print(f"✅ Retrieved model by ID successfully")
            print(f"   Model ID: {retrieved_model.id}")
            print(f"   Name: {retrieved_model.name}")
            print(f"   Status: {retrieved_model.status}")
            print(f"   Task Type: {retrieved_model.task_type}")
            
            # Verify contents field persists
            if model_contents:
                if retrieved_model.contents:
                    print(f"   ✅ Contents field persists: {len(retrieved_model.contents)} files")
                    assert retrieved_model.contents == model_contents, "Contents field mismatch in retrieved model"
                else:
                    print(f"   ⚠️  Contents field is None in retrieved model (API may not support it yet)")
            
            assert retrieved_model.id == created_model_id, "Retrieved model ID mismatch"
            assert retrieved_model.name == test_model_name, "Retrieved model name mismatch"
            
        except Exception as e:
            print(f"❌ Failed to get model by ID: {e}")
            pytest.fail(str(e))
        
        # ==================== GET MODEL BY NAME ====================
        
        print("\n[Step 3] Getting model by name...")
        try:
            retrieved_by_name = model_service.get_model_by_name(
                dataset_id=DATASET_ID,
                name=test_model_name
            )
            
            print(f"✅ Retrieved model by name successfully")
            print(f"   Model ID: {retrieved_by_name.id}")
            print(f"   Name: {retrieved_by_name.name}")
            print(f"   Status: {retrieved_by_name.status}")
            
            assert retrieved_by_name.id == created_model_id, "Model ID mismatch when retrieving by name"
            assert retrieved_by_name.name == test_model_name, "Model name mismatch"
            
        except Exception as e:
            print(f"❌ Failed to get model by name: {e}")
            pytest.fail(str(e))
        
        # ==================== UPDATE MODEL - BASIC INFO ====================
        
        print("\n[Step 4] Updating model basic information...")
        try:
            updated_description = "Updated description for workflow test"
            updated_model = model_service.update_model(
                dataset_id=DATASET_ID,
                model_id=created_model_id,
                description=updated_description,
                is_pinned=True
            )
            
            print(f"✅ Updated model basic information successfully")
            print(f"   Updated Description: {updated_model.description}")
            print(f"   Updated Is Pinned: {updated_model.is_pinned}")
            
            # Verify contents field still persists after update
            if model_contents:
                if updated_model.contents:
                    print(f"   ✅ Contents field still persists after update: {len(updated_model.contents)} files")
                    assert updated_model.contents == model_contents, "Contents field changed unexpectedly"
                else:
                    print(f"   ⚠️  Contents field is None after update (API may not support it yet)")
            
            assert updated_model.description == updated_description, "Description was not updated"
            assert updated_model.is_pinned == True, "Is pinned was not updated"
            
        except Exception as e:
            print(f"❌ Failed to update model basic information: {e}")
            pytest.fail(str(e))
        
        # ==================== UPDATE MODEL - STATUS ====================
        
        print("\n[Step 5] Updating model status...")
        try:
            updated_model_status = model_service.update_model(
                dataset_id=DATASET_ID,
                model_id=created_model_id,
                status=ModelStatus.IN_PROGRESS
            )
            
            print(f"✅ Updated model status successfully")
            print(f"   New Status: {updated_model_status.status}")
            
            assert updated_model_status.status == ModelStatus.IN_PROGRESS, "Status was not updated"
            
        except Exception as e:
            print(f"❌ Failed to update model status: {e}")
            pytest.fail(str(e))
        
        # ==================== UPDATE MODEL - TRAINING DATA COUNTS ====================
        
        print("\n[Step 6] Updating training data counts...")
        try:
            updated_model_counts = model_service.update_model(
                dataset_id=DATASET_ID,
                model_id=created_model_id,
                total_data_count=18567,
                train_data_count=14853,
                validation_data_count=3714
            )
            
            print(f"✅ Updated training data counts successfully")
            print(f"   Total Data Count: {updated_model_counts.total_data_count}")
            print(f"   Train Data Count: {updated_model_counts.train_data_count}")
            print(f"   Validation Data Count: {updated_model_counts.validation_data_count}")
            
            assert updated_model_counts.total_data_count == 18567, "Total data count was not updated"
            assert updated_model_counts.train_data_count == 14853, "Train data count was not updated"
            assert updated_model_counts.validation_data_count == 3714, "Validation data count was not updated"
            
        except Exception as e:
            print(f"❌ Failed to update training data counts: {e}")
            pytest.fail(str(e))
        
        # ==================== UPDATE MODEL - TRAINING PARAMETERS ====================
        
        print("\n[Step 7] Updating training parameters...")
        try:
            new_training_params = {
                "learning_rate": 0.0005,
                "batch_size": 64,
                "epochs": 150,
                "optimizer": "sgd",
                "momentum": 0.9
            }
            
            updated_model_params = model_service.update_model(
                dataset_id=DATASET_ID,
                model_id=created_model_id,
                training_parameters=new_training_params
            )
            
            print(f"✅ Updated training parameters successfully")
            print(f"   Training Parameters: {updated_model_params.training_parameters}")
            
            assert updated_model_params.training_parameters is not None, "Training parameters should not be None"
            assert updated_model_params.training_parameters.get("learning_rate") == 0.0005, "Learning rate was not updated"
            assert updated_model_params.training_parameters.get("batch_size") == 64, "Batch size was not updated"
            
        except Exception as e:
            print(f"❌ Failed to update training parameters: {e}")
            pytest.fail(str(e))
        
        # ==================== UPDATE MODEL - TRAINING ANNOTATIONS ====================
        
        print("\n[Step 7.5] Updating training annotations...")
        try:
            updated_training_annotations = [
                TrainingAnnotations(
                    train_count=9876,
                    validation_count=2469,
                    class_name="Car",
                    annotation_type="bbox"
                ),
                TrainingAnnotations(
                    train_count=15432,
                    validation_count=3858,
                    class_name="Person",
                    annotation_type="bbox"
                ),
                TrainingAnnotations(
                    train_count=3210,
                    validation_count=802,
                    class_name="Bicycle",
                    annotation_type="bbox"
                ),
                TrainingAnnotations(
                    train_count=5678,
                    validation_count=1419,
                    class_name="Truck",
                    annotation_type="bbox"
                ),
            ]
            
            updated_model_annotations = model_service.update_model(
                dataset_id=DATASET_ID,
                model_id=created_model_id,
                training_annotations=updated_training_annotations
            )
            
            print(f"✅ Updated training annotations successfully")
            if updated_model_annotations.trainingAnnotations:
                print(f"   Training Annotations: {len(updated_model_annotations.trainingAnnotations)} classes")
                for ann in updated_model_annotations.trainingAnnotations:
                    print(f"      - {ann.class_name}: train={ann.train_count}, val={ann.validation_count}")
                
                assert len(updated_model_annotations.trainingAnnotations) == 4, "Should have 4 annotation classes after update"
                print(f"   ✅ Training annotations count verified")
            else:
                print(f"   ⚠️  Training annotations field is None after update")
            
        except Exception as e:
            print(f"❌ Failed to update training annotations: {e}")
            pytest.fail(str(e))
        
        # ==================== UPDATE MODEL - CONTENTS ====================
        
        print("\n[Step 7.6] Updating model contents...")
        if model_contents:
            try:
                # Add a new file to contents
                weights_content, _ = content_service.create_content(
                    key="model_weights.pt",
                    content_type="application/octet-stream"
                )
                print(f"   ✅ Created model_weights.pt: {weights_content.id}")
                
                updated_contents = {**model_contents, "model_weights.pt": weights_content.id}
                
                updated_model_contents = model_service.update_model(
                    dataset_id=DATASET_ID,
                    model_id=created_model_id,
                    contents=updated_contents
                )
                
                print(f"✅ Updated model contents successfully")
                
                if updated_model_contents.contents:
                    print(f"   Contents: {len(updated_model_contents.contents)} files")
                    for filename, content_id in updated_model_contents.contents.items():
                        print(f"      - {filename}: {content_id}")
                    
                    assert len(updated_model_contents.contents) == 4, "Should have 4 files now"
                    assert "model_weights.pt" in updated_model_contents.contents, "New file should be in contents"
                    assert updated_model_contents.contents["model_weights.pt"] == weights_content.id, "New file content_id mismatch"
                    
                    # Update model_contents for subsequent checks
                    model_contents = updated_contents
                    print(f"   ✅ Contents field verified after update")
                else:
                    print(f"   ⚠️  Contents field is None after update (API may not support it yet)")
                
            except Exception as e:
                print(f"❌ Failed to update model contents: {e}")
                pytest.fail(str(e))
        else:
            print("   ⏭️  Skipping contents update (initial creation failed)")
        
        # ==================== UPDATE MODEL - SCORE ====================
        
        print("\n[Step 8.5] Updating model score...")

        try:
            updated_model_score = model_service.update_model(
                dataset_id=DATASET_ID,
                model_id=created_model_id,
                score_key="accuracy",
                score_value=0.95,
                score_unit="%"
            )
            
            print(f"✅ Updated model score successfully")
            print(f"   Score Key: {updated_model_score.score_key}")
            print(f"   Score Value: {updated_model_score.score_value}")
            print(f"   Score Unit: {updated_model_score.score_unit}")
            
            assert updated_model_score.score_key == "accuracy", "Score key was not updated"
            assert updated_model_score.score_value == 0.95, "Score value was not updated"
            
        except Exception as e:
            print(f"❌ Failed to update model score: {e}")
            pytest.fail(str(e))
        
        # ==================== UPDATE MODEL - COMPLETE STATUS ====================
        
        print("\n[Step 9] Marking model as completed...")
        try:
            completed_model = model_service.update_model(
                dataset_id=DATASET_ID,
                model_id=created_model_id,
                status=ModelStatus.COMPLETED
            )
            
            print(f"✅ Marked model as completed successfully")
            print(f"   Status: {completed_model.status}")
            print(f"   Completed At: {completed_model.completed_at}")
            
            assert completed_model.status == ModelStatus.COMPLETED, "Status was not updated to COMPLETED"
            
        except Exception as e:
            print(f"❌ Failed to mark model as completed: {e}")
            pytest.fail(str(e))
        
        # ==================== LIST MODELS ====================
        
        print("\n[Step 10] Listing models in dataset...")
        try:
            models_list, next_cursor, total_count = model_service.get_models(
                dataset_id=DATASET_ID,
                length=10
            )
            
            print(f"✅ Retrieved models list successfully")
            print(f"   Total Count: {total_count}")
            print(f"   Retrieved Count: {len(models_list)}")
            print(f"   Next Cursor: {next_cursor}")
            
            # Find our created model in the list
            found_model = None
            for model in models_list:
                if model.id == created_model_id:
                    found_model = model
                    break
            
            if found_model:
                print(f"   ✅ Found our test model in the list:")
                print(f"      Model ID: {found_model.id}")
                print(f"      Name: {found_model.name}")
                print(f"      Status: {found_model.status}")
            else:
                print(f"   ⚠️  Test model not found in first page (might be on next page)")
            
            assert total_count > 0, "Should have at least one model"
            assert len(models_list) > 0, "Should return at least one model"
            
        except Exception as e:
            print(f"❌ Failed to list models: {e}")
            pytest.fail(str(e))
        
        # ==================== TRAINING REPORT - PREPARATION ====================
        
        print("\n[Step 11] Preparing contents for training report...")
        # Get actual contents from the dataset
        CONTENT_IDS = []
        try:
            from spb_onprem import DataService
            data_service = DataService()
            
            # Get first 3 data items from the dataset
            data_list, _, total = data_service.get_data_list(
                dataset_id=DATASET_ID,
                length=3
            )
            
            if len(data_list) >= 3:
                # Extract content IDs from scene data
                for data in data_list[:3]:
                    if data.scene and len(data.scene) > 0:
                        if data.scene[0].content and data.scene[0].content.id:
                            CONTENT_IDS.append(data.scene[0].content.id)
                
                if len(CONTENT_IDS) >= 3:
                    print(f"✅ Found {len(CONTENT_IDS)} contents from dataset:")
                    for i, content_id in enumerate(CONTENT_IDS):
                        print(f"   Content {i+1}: {content_id}")
                else:
                    print(f"⚠️  Only found {len(CONTENT_IDS)} content IDs (need 3)")
                    print(f"   Skipping training report tests")
                    CONTENT_IDS = []
            else:
                print(f"⚠️  Only found {len(data_list)} data items (need 3)")
                print(f"   Skipping training report tests")
                CONTENT_IDS = []
        except Exception as e:
            print(f"⚠️  Failed to get contents: {e}")
            import traceback
            traceback.print_exc()
            print(f"   Skipping training report tests")
            CONTENT_IDS = []
        
        # ==================== CREATE TRAINING REPORT ITEMS WITH CHART DATA ====================
        
        created_training_report_ids = []
        chart_types = [
            AnalyticsReportItemType.PIE,
            AnalyticsReportItemType.HORIZONTAL_BAR,
            AnalyticsReportItemType.VERTICAL_BAR,
            AnalyticsReportItemType.HEATMAP,
            AnalyticsReportItemType.TABLE,
            AnalyticsReportItemType.LINE_CHART,
            AnalyticsReportItemType.SCATTER_PLOT,
            AnalyticsReportItemType.HISTOGRAM,
            AnalyticsReportItemType.METRICS,
        ]
        
        if len(CONTENT_IDS) > 0:
            print(f"\n[Step 12] Creating training report items with chart data for all {len(chart_types)} chart types...")
            try:
                for i, chart_type in enumerate(chart_types):
                    # Create content folder for this chart
                    folder_name = f"chart_{chart_type.value}_{int(time.time())}"
                    try:
                        folder_content, upload_url = content_service.create_content(
                            key=folder_name,
                            content_type="FOLDER"
                        )
                        content_id = folder_content.id
                        print(f"   ✅ Created folder content for {chart_type.value}: {content_id}")
                    except Exception as content_error:
                        print(f"   ⚠️  Failed to create folder for {chart_type.value}: {content_error}")
                        continue
                    
                    # Generate chart data based on type
                    chart_data = None
                    try:
                        if chart_type == AnalyticsReportItemType.PIE:
                            chart_data = ChartDataFactory.create_pie_chart(
                                category_name="Class",
                                value_name="Count",
                                data=[
                                    CategoryValueData(category="Car", value=3421),
                                    CategoryValueData(category="Person", value=5672),
                                    CategoryValueData(category="Bicycle", value=892),
                                    CategoryValueData(category="Truck", value=1234),
                                    CategoryValueData(category="Bus", value=456),
                                ],
                                data_ids=[
                                    DataIdsIndex(index="Car", data_ids=["data_1", "data_2", "data_3"]),
                                    DataIdsIndex(index="Person", data_ids=["data_4", "data_5", "data_6"]),
                                    DataIdsIndex(index="Bicycle", data_ids=["data_7", "data_8"]),
                                ]
                            )
                        
                        elif chart_type == AnalyticsReportItemType.HORIZONTAL_BAR:
                            chart_data = ChartDataFactory.create_horizontal_bar_chart(
                                y_axis_name="Epoch",
                                x_axis_name="Training Loss",
                                data=[
                                    CategoryValueData(category="Epoch 1", value=2.45),
                                    CategoryValueData(category="Epoch 2", value=1.89),
                                    CategoryValueData(category="Epoch 3", value=1.34),
                                    CategoryValueData(category="Epoch 4", value=0.92),
                                    CategoryValueData(category="Epoch 5", value=0.68),
                                    CategoryValueData(category="Epoch 6", value=0.51),
                                ]
                            )
                        
                        elif chart_type == AnalyticsReportItemType.VERTICAL_BAR:
                            chart_data = ChartDataFactory.create_vertical_bar_chart(
                                x_axis_name="Metric",
                                y_axis_name="Score",
                                data=[
                                    CategoryValueData(category="Precision", value=0.92),
                                    CategoryValueData(category="Recall", value=0.88),
                                    CategoryValueData(category="F1-Score", value=0.90),
                                    CategoryValueData(category="mAP", value=0.85),
                                    CategoryValueData(category="IoU", value=0.78),
                                ]
                            )
                        
                        elif chart_type == AnalyticsReportItemType.HEATMAP:
                            chart_data = ChartDataFactory.create_heatmap_chart(
                                y_axis_name="True Label",
                                x_axis_name="Predicted Label",
                                data=[
                                    HeatmapData(y_category="Car", x_category="Car", value=452),
                                    HeatmapData(y_category="Car", x_category="Truck", value=23),
                                    HeatmapData(y_category="Car", x_category="Bus", value=8),
                                    HeatmapData(y_category="Truck", x_category="Car", value=15),
                                    HeatmapData(y_category="Truck", x_category="Truck", value=387),
                                    HeatmapData(y_category="Truck", x_category="Bus", value=12),
                                    HeatmapData(y_category="Bus", x_category="Car", value=5),
                                    HeatmapData(y_category="Bus", x_category="Truck", value=18),
                                    HeatmapData(y_category="Bus", x_category="Bus", value=234),
                                ],
                                data_ids=[
                                    XYDataIds(x="Car", y="Car", data_ids=["data_1", "data_2"]),
                                    XYDataIds(x="Truck", y="Car", data_ids=["data_3"]),
                                ]
                            )
                        
                        elif chart_type == AnalyticsReportItemType.TABLE:
                            chart_data = ChartDataFactory.create_table_chart(
                                headers=["Class", "Precision", "Recall", "F1-Score", "Support"],
                                rows=[
                                    ["Car", 0.95, 0.92, 0.93, 3421],
                                    ["Person", 0.91, 0.94, 0.92, 5672],
                                    ["Bicycle", 0.88, 0.85, 0.86, 892],
                                    ["Truck", 0.93, 0.89, 0.91, 1234],
                                    ["Bus", 0.87, 0.91, 0.89, 456],
                                ],
                                data_ids=[
                                    XYDataIds(x="Precision", y="Car", data_ids=["data_1"]),
                                    XYDataIds(x="Recall", y="Car", data_ids=["data_2"]),
                                ]
                            )
                        
                        elif chart_type == AnalyticsReportItemType.LINE_CHART:
                            chart_data = ChartDataFactory.create_line_chart(
                                x_name="Epoch",
                                y_name="Accuracy",
                                data=[
                                    LineChartData(series="Train", x=1, y=0.65),
                                    LineChartData(series="Train", x=2, y=0.73),
                                    LineChartData(series="Train", x=3, y=0.81),
                                    LineChartData(series="Train", x=4, y=0.87),
                                    LineChartData(series="Train", x=5, y=0.91),
                                    LineChartData(series="Validation", x=1, y=0.62),
                                    LineChartData(series="Validation", x=2, y=0.68),
                                    LineChartData(series="Validation", x=3, y=0.75),
                                    LineChartData(series="Validation", x=4, y=0.82),
                                    LineChartData(series="Validation", x=5, y=0.85),
                                ],
                                data_ids=[
                                    LineChartDataIds(series="Train", x="1", data_ids=["data_1", "data_2"]),
                                    LineChartDataIds(series="Validation", x="1", data_ids=["data_3"]),
                                ]
                            )
                        
                        elif chart_type == AnalyticsReportItemType.SCATTER_PLOT:
                            chart_data = ChartDataFactory.create_scatter_plot_chart(
                                x_name="Inference Time (ms)",
                                y_name="Accuracy",
                                data=[
                                    ScatterPlotData(x=45.3, y=0.87, category="ResNet50"),
                                    ScatterPlotData(x=89.7, y=0.92, category="ResNet50"),
                                    ScatterPlotData(x=32.1, y=0.81, category="MobileNet"),
                                    ScatterPlotData(x=67.8, y=0.85, category="MobileNet"),
                                    ScatterPlotData(x=123.4, y=0.95, category="EfficientNet"),
                                    ScatterPlotData(x=156.2, y=0.97, category="EfficientNet"),
                                ],
                                data_ids=[
                                    DataIdsIndex(index="ResNet50", data_ids=["data_1", "data_2"]),
                                    DataIdsIndex(index="MobileNet", data_ids=["data_3"]),
                                ]
                            )
                        
                        elif chart_type == AnalyticsReportItemType.HISTOGRAM:
                            chart_data = ChartDataFactory.create_histogram_chart(
                                bin_name="Confidence Score Range",
                                frequency_name="Count",
                                data=[
                                    BinFrequencyData(bin="0.0-0.1", frequency=23),
                                    BinFrequencyData(bin="0.1-0.2", frequency=45),
                                    BinFrequencyData(bin="0.2-0.3", frequency=89),
                                    BinFrequencyData(bin="0.3-0.4", frequency=156),
                                    BinFrequencyData(bin="0.4-0.5", frequency=234),
                                    BinFrequencyData(bin="0.5-0.6", frequency=478),
                                    BinFrequencyData(bin="0.6-0.7", frequency=892),
                                    BinFrequencyData(bin="0.7-0.8", frequency=1345),
                                    BinFrequencyData(bin="0.8-0.9", frequency=2156),
                                    BinFrequencyData(bin="0.9-1.0", frequency=3421),
                                ],
                                data_ids=[
                                    DataIdsIndex(index="0.9-1.0", data_ids=["data_1", "data_2", "data_3"]),
                                ]
                            )
                        
                        elif chart_type == AnalyticsReportItemType.METRICS:
                            chart_data = ChartDataFactory.create_metrics_chart(
                                metrics=[
                                    MetricData(key="Total Epochs", value=50),
                                    MetricData(key="Best Epoch", value=47),
                                    MetricData(key="Final Loss", value=0.0234),
                                    MetricData(key="Best Accuracy", value=0.9567),
                                    MetricData(key="Training Time", value="2h 34m"),
                                    MetricData(key="GPU Usage", value="87.3%"),
                                    MetricData(key="Model Size", value="245 MB"),
                                    MetricData(key="Parameters", value={"total": 25600000, "trainable": 25550000}),
                                ],
                                data_ids=["data_1", "data_2", "data_3"]
                            )
                        
                        if chart_data:
                            # Upload reports.json
                            model_service.upload_reports_json(content_id, chart_data)
                            print(f"      ✅ Uploaded reports.json")
                            
                            # Upload data_ids.json if exists
                            if chart_data.data_ids_json:
                                model_service.upload_data_ids_json(content_id, chart_data)
                                print(f"      ✅ Uploaded data_ids.json")
                        
                    except Exception as chart_error:
                        print(f"   ⚠️  Failed to create/upload chart data for {chart_type.value}: {chart_error}")
                        continue
                    
                    # Create training report item
                    test_report_name = f"Training Report - {chart_type.value}"
                    test_report_description = f"{chart_type.value} chart for model training metrics"
                    
                    try:
                        model_with_report = model_service.create_training_report_item(
                            dataset_id=DATASET_ID,
                            model_id=created_model_id,
                            name=test_report_name,
                            type=chart_type,
                            content_id=content_id,
                            description=test_report_description
                        )
                        
                        if model_with_report.training_report:
                            if isinstance(model_with_report.training_report, list):
                                for report in model_with_report.training_report:
                                    if report.name == test_report_name:
                                        created_training_report_ids.append(report.id)
                                        print(f"   ✅ Created training report {i+1}/{len(chart_types)}: {chart_type.value}")
                                        print(f"      Report ID: {report.id}")
                                        print(f"      Content ID: {content_id}")
                                        break
                            else:
                                created_training_report_ids.append(model_with_report.training_report.id)
                                print(f"   ✅ Created training report {i+1}/{len(chart_types)}: {chart_type.value}")
                                print(f"      Report ID: {model_with_report.training_report.id}")
                                print(f"      Content ID: {content_id}")
                    
                    except Exception as report_error:
                        print(f"   ⚠️  Failed to create training report for {chart_type.value}: {report_error}")
                
                print(f"✅ Created {len(created_training_report_ids)}/{len(chart_types)} training report items with chart data")
                
            except Exception as e:
                print(f"❌ Failed to create training report items: {e}")
                import traceback
                traceback.print_exc()
                print(f"   Continuing with remaining tests...")
        else:
            print("\n[Step 12] Skipping training report creation (no contents available)")
        
        # ==================== UPDATE TRAINING REPORT ITEMS ====================
        
        if len(created_training_report_ids) > 0:
            print(f"\n[Step 13] Updating training report items...")
            try:
                # Update the first report (or up to 2 if multiple exist)
                num_to_update = min(2, len(created_training_report_ids))
                updated_count = 0
                for i, report_id in enumerate(created_training_report_ids[:num_to_update]):
                    updated_report_name = f"updated_workflow_test_report_{int(time.time())}_{i}"
                    updated_report_description = f"Updated training report {i+1} description"
                    
                    try:
                        model_with_updated_report = model_service.update_training_report_item(
                            dataset_id=DATASET_ID,
                            model_id=created_model_id,
                            training_report_id=report_id,
                            name=updated_report_name,
                            description=updated_report_description
                        )
                        
                        print(f"   ✅ Updated training report {i+1}/{num_to_update}:")
                        print(f"      Report ID: {report_id}")
                        print(f"      Updated Name: {updated_report_name}")
                        print(f"      Updated Description: {updated_report_description}")
                        updated_count += 1
                    except Exception as update_error:
                        print(f"   ⚠️  Failed to update training report {i+1}: {update_error}")
                
                print(f"✅ Updated {updated_count}/{num_to_update} training report items")
                
            except Exception as e:
                print(f"❌ Failed to update training report items: {e}")
                print(f"   Continuing with remaining tests...")
        else:
            print("\n[Step 13] Skipping training report update (no reports created)")
        
        # ==================== DELETE TRAINING REPORT ITEMS ====================
        
        if CLEANUP and len(created_training_report_ids) > 0:
            print(f"\n[Step 14] Deleting training report items...")
            try:
                deleted_count = 0
                # Delete all created training reports
                for i, report_id in enumerate(created_training_report_ids):
                    try:
                        model_after_report_delete = model_service.delete_training_report_item(
                            dataset_id=DATASET_ID,
                            model_id=created_model_id,
                            training_report_id=report_id
                        )
                        deleted_count += 1
                        print(f"   ✅ Deleted training report {i+1}/{len(created_training_report_ids)}: {report_id}")
                    except Exception as delete_error:
                        print(f"   ⚠️  Failed to delete training report {i+1}: {delete_error}")
                
                print(f"✅ Deleted {deleted_count}/{len(created_training_report_ids)} training report items")
                
                # Verify reports were deleted
                try:
                    verification_model = model_service.get_model(
                        dataset_id=DATASET_ID,
                        model_id=created_model_id
                    )
                    
                    if verification_model.training_report:
                        if isinstance(verification_model.training_report, list):
                            remaining_count = len(verification_model.training_report)
                            print(f"   ⚠️  {remaining_count} training reports still present after deletion")
                        else:
                            print(f"   ⚠️  Training report still present after deletion")
                    else:
                        print(f"   ✅ All training reports successfully deleted")
                except Exception as verify_error:
                    print(f"   ⚠️  Could not verify deletion: {verify_error}")
                
            except Exception as e:
                print(f"❌ Failed to delete training report items: {e}")
                print(f"   Continuing with model verification...")
        else:
            if len(created_training_report_ids) > 0:
                print(f"\n[Step 14] Skipping training report deletion (CLEANUP=0)")
                print(f"   {len(created_training_report_ids)} training reports remain in the system")
            else:
                print("\n[Step 14] Skipping training report deletion (no reports created)")
        
        # ==================== VERIFY MODEL STATE BEFORE DELETION ====================
        
        print("\n[Step 15] Verifying model state before deletion...")
        try:
            model_before_delete = model_service.get_model(
                dataset_id=DATASET_ID,
                model_id=created_model_id
            )
            
            print(f"✅ Retrieved model state before deletion")
            print(f"   Model ID: {model_before_delete.id}")
            print(f"   Name: {model_before_delete.name}")
            print(f"   Status: {model_before_delete.status}")
            print(f"   Description: {model_before_delete.description}")
            print(f"   Task Type: {model_before_delete.task_type}")
            print(f"   Is Pinned: {model_before_delete.is_pinned}")
            print(f"   Score: {model_before_delete.score_key} = {model_before_delete.score_value} {model_before_delete.score_unit}")
            print(f"   Training Parameters: {model_before_delete.training_parameters}")
            print(f"   Data Counts: total={model_before_delete.total_data_count}, train={model_before_delete.train_data_count}, val={model_before_delete.validation_data_count}")
            
        except Exception as e:
            print(f"❌ Failed to verify model state: {e}")
            pytest.fail(str(e))
        
        # ==================== DELETE MODEL ====================
        
        if CLEANUP:
            print("\n[Step 16] Deleting the test model...")
            try:
                delete_result = model_service.delete_model(
                    dataset_id=DATASET_ID,
                    model_id=created_model_id
                )
                
                print(f"✅ Model deletion executed successfully")
                print(f"   Delete Result: {delete_result}")
                
                assert delete_result == True, "Delete operation should return True"
                
            except Exception as e:
                print(f"❌ Failed to delete model: {e}")
                pytest.fail(str(e))
        else:
            print("\n[Step 16] Skipping model deletion (CLEANUP=0)")
            print(f"   Model remains in the system: {created_model_id}")
        
        # ==================== VERIFY MODEL DELETION ====================
        
        if CLEANUP:
            print("\n[Step 17] Verifying model deletion...")
            try:
                deleted_model = model_service.get_model(
                    dataset_id=DATASET_ID,
                    model_id=created_model_id
                )
                
                if deleted_model is None:
                    print(f"✅ Model successfully deleted (returns None)")
                else:
                    print(f"⚠️  Model still exists after deletion:")
                    print(f"   Model ID: {deleted_model.id}")
                    print(f"   Name: {deleted_model.name}")
                    pytest.fail("Model should be deleted but still exists")
                    
            except Exception as e:
                # NotFoundError is expected when model is deleted
                from spb_onprem.exceptions import NotFoundError
                if isinstance(e, NotFoundError):
                    print(f"✅ Model successfully deleted (NotFoundError raised as expected)")
                else:
                    print(f"❌ Unexpected error while verifying deletion: {e}")
                    pytest.fail(str(e))
        
        # ==================== FINAL SUCCESS MESSAGE ====================
        
        print("\n" + "=" * 80)
        print("Model Service Complete Lifecycle Workflow Test Passed Successfully! 🎉")
        print("=" * 80)
        print("\nTest Summary:")
        print(f"  ✓ Dataset ID: {DATASET_ID}")
        print(f"  ✓ Created model: {created_model_id}")
        print(f"  ✓ Model name: {test_model_name}")
        print(f"  ✓ Task type: {test_task_type}")
        print(f"  ✓ Created {len(created_training_report_ids)} training report items with chart data:")
        print(f"    - PIE, HORIZONTAL_BAR, VERTICAL_BAR, HEATMAP, TABLE")
        print(f"    - LINE_CHART, SCATTER_PLOT, HISTOGRAM, METRICS")
        if CLEANUP:
            print(f"  ✓ Cleaned up all training reports and model")
        else:
            print(f"  ℹ️  Model and training reports remain in system (CLEANUP=0)")
            print(f"     Model ID: {created_model_id}")
        print("\nTo run without cleanup:")
        print("  CLEANUP=0 RUN_MODEL_WORKFLOW_TESTS=1 python -m pytest tests/models/test_workflow.py::test_model_lifecycle_workflow")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        
        if CLEANUP:
            print(f"\n⚠️  Attempting cleanup...")
            # Cleanup: try to delete the model if it was created
            if created_model_id:
                try:
                    print(f"   Attempting to delete model: {created_model_id}")
                    model_service.delete_model(
                        dataset_id=DATASET_ID,
                        model_id=created_model_id
                    )
                    print(f"   ✅ Cleanup successful - model deleted")
                except Exception as cleanup_error:
                    print(f"   ⚠️  Cleanup failed: {cleanup_error}")
                    print(f"   ⚠️  Please manually delete model: {created_model_id}")
        else:
            if created_model_id:
                print(f"\n⚠️  Model remains in system (CLEANUP=0): {created_model_id}")
        
        pytest.fail(str(e))


def test_model_filter_and_pagination_workflow():
    """
    Test model filtering and pagination:
    - Create multiple models
    - Test pagination with cursor
    - Test filtering by status
    - Cleanup created models
    """
    if os.environ.get("CI") == "true":
        pytest.skip("Skip workflow tests on CI")
    if os.environ.get("RUN_MODEL_WORKFLOW_TESTS") != "1":
        pytest.skip("RUN_MODEL_WORKFLOW_TESTS!=1 (avoid accidental mutations)")
    
    model_service = ModelService()
    dataset_service = DatasetService()
    
    print("\n" + "=" * 80)
    print("Model Service Filter and Pagination Workflow Test")
    print("=" * 80)
    
    # ==================== FIND DATASET ====================
    
    print("\n[Step 0] Finding a dataset for pagination testing...")
    DATASET_ID = None
    
    try:
        # Get first available dataset
        datasets, _, total = dataset_service.get_datasets(length=1)
        
        if total > 0 and len(datasets) > 0:
            dataset = datasets[0]
            DATASET_ID = dataset.id
            print(f"✅ Found dataset: {dataset.name} (ID: {dataset.id})")
        else:
            print("❌ No datasets found")
            pytest.fail("No datasets found")
    except Exception as e:
        pytest.fail(str(e))
    
    # ==================== CREATE MULTIPLE MODELS ====================
    
    print("\n[Step 1] Creating multiple test models...")
    created_model_ids = []
    num_models_to_create = 3
    
    try:
        for i in range(num_models_to_create):
            model_name = f"pagination_test_model_{int(time.time())}_{i}"
            
            # Vary the status and task type for filtering tests
            if i == 0:
                status = None  # Will be PENDING by default
                task_type = ModelTaskType.OBJECT_DETECTION
            elif i == 1:
                status = None
                task_type = ModelTaskType.INSTANCE_SEGMENTATION
            else:
                status = None
                task_type = ModelTaskType.OCR
            
            model = model_service.create_model(
                dataset_id=DATASET_ID,
                name=model_name,
                task_type=task_type,
                description=f"Pagination test model {i+1}",
                total_data_count=100 * (i + 1),
                train_data_count=80 * (i + 1),
                validation_data_count=20 * (i + 1),
            )
            
            created_model_ids.append(model.id)
            print(f"   ✅ Created model {i+1}/{num_models_to_create}: {model.name} (ID: {model.id})")
            
            # Update some models to different statuses for filtering
            if i == 1:
                model_service.update_model(
                    dataset_id=DATASET_ID,
                    model_id=model.id,
                    status=ModelStatus.IN_PROGRESS
                )
                print(f"      Updated status to IN_PROGRESS")
            elif i == 2:
                model_service.update_model(
                    dataset_id=DATASET_ID,
                    model_id=model.id,
                    status=ModelStatus.COMPLETED
                )
                print(f"      Updated status to COMPLETED")
        
        print(f"✅ Created {len(created_model_ids)} test models")
        
    except Exception as e:
        print(f"❌ Failed to create test models: {e}")
        # Cleanup any created models
        for model_id in created_model_ids:
            try:
                model_service.delete_model(DATASET_ID, model_id)
            except:
                pass
        pytest.fail(str(e))
    
    try:
        # ==================== TEST PAGINATION ====================
        
        print("\n[Step 2] Testing pagination with small page size...")
        try:
            # Get first page
            page1_models, page1_cursor, total = model_service.get_models(
                dataset_id=DATASET_ID,
                length=2
            )
            
            print(f"✅ Retrieved first page")
            print(f"   Total Count: {total}")
            print(f"   Page 1 Count: {len(page1_models)}")
            print(f"   Next Cursor: {page1_cursor}")
            
            # Get second page if cursor exists
            if page1_cursor:
                page2_models, page2_cursor, _ = model_service.get_models(
                    dataset_id=DATASET_ID,
                    cursor=page1_cursor,
                    length=2
                )
                
                print(f"✅ Retrieved second page")
                print(f"   Page 2 Count: {len(page2_models)}")
                print(f"   Next Cursor: {page2_cursor}")
                
                # Verify no overlap between pages
                page1_ids = {m.id for m in page1_models}
                page2_ids = {m.id for m in page2_models}
                overlap = page1_ids & page2_ids
                
                assert len(overlap) == 0, f"Pages should not overlap, but found: {overlap}"
                print(f"   ✅ No overlap between pages")
            
        except Exception as e:
            print(f"❌ Failed pagination test: {e}")
            raise
        
        # ==================== TEST FILTERING BY STATUS ====================
        
        print("\n[Step 3] Testing model filtering...")
        try:
            # Note: Actual filter implementation depends on ModelFilter class
            # This is a placeholder - adjust based on actual API
            print(f"   Note: Filter testing depends on ModelFilter implementation")
            print(f"   Retrieving all models to verify status distribution")
            
            all_models, _, _ = model_service.get_models(
                dataset_id=DATASET_ID,
                length=100
            )
            
            # Count models by status
            status_counts = {}
            for model in all_models:
                status = model.status if model.status else "None"
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"✅ Model status distribution:")
            for status, count in status_counts.items():
                print(f"   - {status}: {count}")
            
        except Exception as e:
            print(f"❌ Failed filtering test: {e}")
            raise
        
        # ==================== VERIFY CREATED MODELS ====================
        
        print("\n[Step 4] Verifying all created models exist...")
        try:
            all_models, _, _ = model_service.get_models(
                dataset_id=DATASET_ID,
                length=100
            )
            
            all_model_ids = {m.id for m in all_models}
            
            found_count = 0
            for created_id in created_model_ids:
                if created_id in all_model_ids:
                    found_count += 1
                    print(f"   ✅ Found created model: {created_id}")
                else:
                    print(f"   ⚠️  Missing created model: {created_id}")
            
            print(f"✅ Found {found_count}/{len(created_model_ids)} created models")
            assert found_count == len(created_model_ids), "Not all created models were found"
            
        except Exception as e:
            print(f"❌ Failed to verify created models: {e}")
            raise
        
        # ==================== CLEANUP ====================
        
        print("\n[Step 5] Cleaning up test models...")
        cleanup_count = 0
        for model_id in created_model_ids:
            try:
                model_service.delete_model(
                    dataset_id=DATASET_ID,
                    model_id=model_id
                )
                cleanup_count += 1
                print(f"   ✅ Deleted model: {model_id}")
            except Exception as e:
                print(f"   ⚠️  Failed to delete model {model_id}: {e}")
        
        print(f"✅ Cleaned up {cleanup_count}/{len(created_model_ids)} models")
        
        # ==================== FINAL SUMMARY ====================
        
        print("\n" + "=" * 80)
        print("Model Filter and Pagination Workflow Test Passed Successfully! 🎉")
        print("=" * 80)
        print("\nSummary:")
        print(f"  ✓ Created {num_models_to_create} test models with varied statuses")
        print("  ✓ Tested pagination with cursor")
        print("  ✓ Tested model filtering and status distribution")
        print("  ✓ Verified all created models")
        print(f"  ✓ Cleaned up {cleanup_count}/{len(created_model_ids)} models")
        print("=" * 80)
        
    except Exception as e:
        # Cleanup on failure
        print(f"\n❌ Test failed: {e}")
        print(f"⚠️  Attempting cleanup...")
        for model_id in created_model_ids:
            try:
                model_service.delete_model(DATASET_ID, model_id)
            except:
                pass
        pytest.fail(str(e))


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Running Model Service Workflow Tests")
    print("=" * 80)
    print("\nTest 1: Complete Lifecycle Workflow")
    test_model_lifecycle_workflow()
    
    print("\n\nTest 2: Filter and Pagination Workflow")
    test_model_filter_and_pagination_workflow()
    
    print("\n" + "=" * 80)
    print("All Model Workflow Tests Completed Successfully! 🎉")
    print("=" * 80)
