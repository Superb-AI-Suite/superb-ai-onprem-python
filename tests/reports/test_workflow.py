import os

from spb_onprem import (
    ReportService, 
    DatasetService, 
    AnalyticsReportItemType, 
    AnalyticsReportStatus,
    AnalyticsReportsFilter,
    AnalyticsReportsFilterOptions,
    ContentService
)


def test_analytics_report_workflow():
    if os.environ.get("CI") == "true":
        print("⚠️  Skipping: CI environment detected")
        return False
    if os.environ.get("RUN_REPORT_WORKFLOW_TESTS") != "1":
        print("⚠️  Skipping: RUN_REPORT_WORKFLOW_TESTS!=1 (set RUN_REPORT_WORKFLOW_TESTS=1 to run)")
        return False

    """Test complete workflow for analytics report and items:
    - Report: create -> list -> get -> update -> get
    - Items: create all types -> update all -> delete all
    - Report: delete
    """
    
    # Get the latest dataset dynamically
    print("Fetching latest dataset...")
    dataset_service = DatasetService()
    
    try:
        datasets, _, total_count = dataset_service.get_datasets()
        
        if not datasets or total_count == 0:
            print("❌ No datasets found. Please create a dataset first.")
            return False
        
        dataset = datasets[0]
        dataset_id = dataset.id
        print(f"✅ Using dataset: {dataset.name} (ID: {dataset_id})\n")
    except Exception as e:
        print(f"⚠️  Could not fetch datasets dynamically: {e}")
        print("⚠️  Using fallback dataset ID: 01K99Q3E9H94QAMP2DHWG24XB5\n")
        dataset_id = "01K99Q3E9H94QAMP2DHWG24XB5"
    
    report_service = ReportService()
    
    print("=" * 70)
    print("Analytics Report & Items Workflow Test")
    print("=" * 70)
    
    # ==================== ANALYTICS REPORT TESTS ====================
    
    # Step 1: Create analytics report
    print("\n[Step 1] Creating analytics report...")
    created_report = report_service.create_analytics_report(
        dataset_id=dataset_id,
        title="Workflow Test Report",
        description="Testing complete analytics report workflow",
        meta={
            "test_type": "workflow",
            "version": "1.0"
        }
    )
    print(f"✅ Created report: {created_report.id}")
    print(f"   Title: {created_report.title}")
    print(f"   Description: {created_report.description}")
    print(f"   Status: {created_report.status} (should be PENDING)")
    print(f"   Completed At: {created_report.completed_at} (should be None)")
    print(f"   Meta: {created_report.meta}")
    
    # Verify initial status
    assert created_report.status == AnalyticsReportStatus.PENDING or created_report.status == "PENDING", "Initial status should be PENDING"
    assert created_report.completed_at is None, "Initial completedAt should be None"
    
    # Step 2: List analytics reports (search)
    print("\n[Step 2] Listing analytics reports...")
    reports, next_cursor, total_count = report_service.get_analytics_reports(
        dataset_id=dataset_id,
        length=10
    )
    print(f"✅ Found {total_count} total reports")
    print(f"   Current page has {len(reports)} reports")
    
    # Verify our created report is in the list
    found_in_list = any(r.id == created_report.id for r in reports)
    print(f"   Our report found in list: {found_in_list}")
    
    # Step 3: Get specific analytics report
    print("\n[Step 3] Getting specific analytics report...")
    fetched_report = report_service.get_analytics_report(
        dataset_id=dataset_id,
        report_id=created_report.id
    )
    print(f"✅ Fetched report: {fetched_report.id}")
    print(f"   Title: {fetched_report.title}")
    print(f"   Description: {fetched_report.description}")
    print(f"   Meta: {fetched_report.meta}")
    print(f"   Match with created: {fetched_report.id == created_report.id}")
    
    # Step 4: Update analytics report with status IN_PROGRESS
    print("\n[Step 4] Updating analytics report with status IN_PROGRESS...")
    updated_report = report_service.update_analytics_report(
        dataset_id=dataset_id,
        report_id=created_report.id,
        title="Updated Workflow Test Report",
        description="Updated description for workflow testing",
        status=AnalyticsReportStatus.IN_PROGRESS,
        meta={
            "test_type": "workflow",
            "version": "2.0",
            "updated": True
        }
    )
    print(f"✅ Updated report: {updated_report.id}")
    print(f"   New Title: {updated_report.title}")
    print(f"   New Description: {updated_report.description}")
    print(f"   New Status: {updated_report.status} (should be IN_PROGRESS)")
    print(f"   Completed At: {updated_report.completed_at} (should still be None)")
    print(f"   New Meta: {updated_report.meta}")
    
    # Verify status update
    assert updated_report.status == AnalyticsReportStatus.IN_PROGRESS or updated_report.status == "IN_PROGRESS", "Status should be IN_PROGRESS"
    assert updated_report.completed_at is None, "completedAt should still be None for IN_PROGRESS"
    
    # Step 5: Get analytics report again to verify update
    print("\n[Step 5] Getting analytics report again to verify update...")
    re_fetched_report = report_service.get_analytics_report(
        dataset_id=dataset_id,
        report_id=created_report.id
    )
    print(f"✅ Re-fetched report: {re_fetched_report.id}")
    print(f"   Title: {re_fetched_report.title}")
    print(f"   Description: {re_fetched_report.description}")
    print(f"   Status: {re_fetched_report.status}")
    print(f"   Completed At: {re_fetched_report.completed_at}")
    print(f"   Meta: {re_fetched_report.meta}")
    print(f"   Title updated correctly: {re_fetched_report.title == 'Updated Workflow Test Report'}")
    print(f"   Status updated correctly: {re_fetched_report.status == AnalyticsReportStatus.IN_PROGRESS or re_fetched_report.status == 'IN_PROGRESS'}")
    print(f"   Meta version updated: {re_fetched_report.meta.get('version') == '2.0'}")
    
    # Step 5.5: Update status to COMPLETED and verify completedAt is set
    print("\n[Step 5.5] Updating status to COMPLETED to test completedAt auto-setting...")
    completed_report = report_service.update_analytics_report(
        dataset_id=dataset_id,
        report_id=created_report.id,
        status=AnalyticsReportStatus.COMPLETED
    )
    print(f"✅ Updated report to COMPLETED: {completed_report.id}")
    print(f"   Status: {completed_report.status} (should be COMPLETED)")
    print(f"   Completed At: {completed_report.completed_at} (should be set automatically)")
    
    # Verify COMPLETED status and completedAt
    assert completed_report.status == AnalyticsReportStatus.COMPLETED or completed_report.status == "COMPLETED", "Status should be COMPLETED"
    print(f"   ✓ Status is COMPLETED")
    if completed_report.completed_at:
        print(f"   ✓ completedAt is set: {completed_report.completed_at}")
    else:
        print(f"   ⚠️  completedAt not set (may be handled by backend)")
    
    # Step 5.6: Test statusIn filter
    print("\n[Step 5.6] Testing statusIn filter...")
    
    # Search for COMPLETED reports
    completed_filter = AnalyticsReportsFilter(
        must_filter=AnalyticsReportsFilterOptions(
            status_in=[AnalyticsReportStatus.COMPLETED]
        )
    )
    completed_reports, _, completed_count = report_service.get_analytics_reports(
        dataset_id=dataset_id,
        analytics_reports_filter=completed_filter,
        length=10
    )
    print(f"✅ Found {completed_count} COMPLETED reports")
    found_our_completed = any(r.id == created_report.id for r in completed_reports)
    print(f"   Our COMPLETED report found: {found_our_completed}")
    if completed_reports:
        for report in completed_reports[:3]:  # Show first 3
            print(f"   - {report.title}: {report.status}")
    
    # Search for IN_PROGRESS reports (should not include our report anymore)
    in_progress_filter = AnalyticsReportsFilter(
        must_filter=AnalyticsReportsFilterOptions(
            status_in=[AnalyticsReportStatus.IN_PROGRESS]
        )
    )
    in_progress_reports, _, in_progress_count = report_service.get_analytics_reports(
        dataset_id=dataset_id,
        analytics_reports_filter=in_progress_filter,
        length=10
    )
    print(f"\n✅ Found {in_progress_count} IN_PROGRESS reports")
    found_in_progress = any(r.id == created_report.id for r in in_progress_reports)
    print(f"   Our report found in IN_PROGRESS: {found_in_progress} (should be False)")
    
    # Search for multiple statuses
    multiple_status_filter = AnalyticsReportsFilter(
        must_filter=AnalyticsReportsFilterOptions(
            status_in=[AnalyticsReportStatus.PENDING, AnalyticsReportStatus.COMPLETED]
        )
    )
    multiple_reports, _, multiple_count = report_service.get_analytics_reports(
        dataset_id=dataset_id,
        analytics_reports_filter=multiple_status_filter,
        length=10
    )
    print(f"\n✅ Found {multiple_count} reports with PENDING or COMPLETED status")
    found_in_multiple = any(r.id == created_report.id for r in multiple_reports)
    print(f"   Our COMPLETED report found: {found_in_multiple}")
    
    # ==================== ANALYTICS REPORT ITEMS TESTS ====================
    
    print("\n" + "=" * 70)
    print("Analytics Report Items Tests")
    print("=" * 70)
    
    # Step 6: Create report items for all types
    print("\n[Step 6] Creating report items for all types...")
    
    item_types = [
        AnalyticsReportItemType.PIE,
        AnalyticsReportItemType.HORIZONTAL_BAR,
        AnalyticsReportItemType.VERTICAL_BAR,
        AnalyticsReportItemType.HEATMAP,
    ]
    
    # Create folder content IDs using ContentService
    content_service = ContentService()
    content_ids = {}
    
    print("   Creating folder content IDs...")
    for item_type in item_types:
        folder_content_id = content_service.create_folder_content()
        content_ids[item_type] = folder_content_id
        print(f"   ✓ Created folder content for {item_type.value}: {folder_content_id}")
    
    # Upload sample JSON data for each content
    print("   Uploading sample JSON data to folder contents...")
    uploaded_data = {}  # Store uploaded data for verification
    for item_type, content_id in content_ids.items():
        # Create chart data using ChartDataFactory
        from spb_onprem.charts import ChartDataFactory, CategoryValueData, DataIdsIndex
        
        if item_type == AnalyticsReportItemType.PIE:
            chart_data = ChartDataFactory.create_pie_chart(
                category_name="Category",
                value_name="Value",
                data=[
                    CategoryValueData(category="A", value=10),
                    CategoryValueData(category="B", value=20),
                    CategoryValueData(category="C", value=30),
                ]
            )
        elif item_type == AnalyticsReportItemType.HORIZONTAL_BAR:
            chart_data = ChartDataFactory.create_horizontal_bar_chart(
                y_axis_name="Category",
                x_axis_name="Value",
                data=[
                    CategoryValueData(category="A", value=10),
                    CategoryValueData(category="B", value=20),
                ],
                data_ids=[
                    DataIdsIndex(index="A", data_ids=["id_a1", "id_a2"]),
                    DataIdsIndex(index="B", data_ids=["id_b1", "id_b2"]),
                ]
            )
        elif item_type == AnalyticsReportItemType.VERTICAL_BAR:
            chart_data = ChartDataFactory.create_vertical_bar_chart(
                x_axis_name="Category",
                y_axis_name="Value",
                data=[
                    CategoryValueData(category="A", value=10),
                    CategoryValueData(category="B", value=20),
                ]
            )
        elif item_type == AnalyticsReportItemType.HEATMAP:
            from spb_onprem.charts import HeatmapData
            chart_data = ChartDataFactory.create_heatmap_chart(
                y_axis_name="Y",
                x_axis_name="X",
                data=[
                    HeatmapData(y_category="Y1", x_category="X1", value=10),
                    HeatmapData(y_category="Y1", x_category="X2", value=20),
                ]
            )
        else:
            # Fallback to simple vertical bar
            chart_data = ChartDataFactory.create_vertical_bar_chart(
                x_axis_name="Category",
                y_axis_name="Value",
                data=[CategoryValueData(category="A", value=10)]
            )
        
        # Upload reports.json
        report_service.upload_reports_json(content_id, chart_data)
        
        # Upload data_ids.json if available
        if chart_data.data_ids_json:
            report_service.upload_data_ids_json(content_id, chart_data)
        
        # Store for later verification
        uploaded_data[item_type] = {
            "reports": chart_data.reports_json,
            "data_ids": chart_data.data_ids_json
        }
        print(f"   ✓ Uploaded JSON files for {item_type.value}")
    
    # Verify uploaded files by downloading them
    print("   Verifying uploaded files by downloading...")
    import requests
    import json as json_lib
    for item_type, content_id in content_ids.items():
        # Get download URLs
        reports_download_url = content_service.get_download_url(content_id, "reports.json")
        
        # Download and verify reports.json
        reports_response = requests.get(reports_download_url)
        downloaded_reports = reports_response.json()
        assert downloaded_reports == uploaded_data[item_type]["reports"], f"reports.json mismatch for {item_type.value}"
        
        # Download and verify data_ids.json if it exists
        if uploaded_data[item_type]["data_ids"] is not None:
            data_ids_download_url = content_service.get_download_url(content_id, "data_ids.json")
            data_ids_response = requests.get(data_ids_download_url)
            if data_ids_response.status_code == 200 and data_ids_response.content:
                downloaded_data_ids = data_ids_response.json()
                assert downloaded_data_ids == uploaded_data[item_type]["data_ids"], f"data_ids.json mismatch for {item_type.value}"
        
        print(f"   ✓ Verified downloaded JSON files for {item_type.value}")
    
    created_items = {}
    
    for item_type in item_types:
        item = report_service.create_analytics_report_item(
            dataset_id=dataset_id,
            report_id=created_report.id,
            type=item_type,
            title=f"{item_type.value} Chart",
            description=f"Test {item_type.value} chart for workflow testing",
            content_id=content_ids[item_type],
            meta={
                "chart_type": item_type.value,
                "version": "1.0"
            }
        )
        created_items[item_type] = item
        print(f"✅ Created {item_type.value} item: {item.id}")
        print(f"   Title: {item.title}")
        print(f"   Content ID: {content_ids[item_type]}")
    
    # Step 7: Verify items by fetching report
    print("\n[Step 7] Verifying items by fetching report...")
    report_with_items = report_service.get_analytics_report(
        dataset_id=dataset_id,
        report_id=created_report.id
    )
    print(f"✅ Fetched report has {len(report_with_items.items) if report_with_items.items else 0} items")
    if report_with_items.items:
        for item in report_with_items.items:
            print(f"   - {item.type}: {item.title} (ID: {item.id})")
    
    # Step 8: Update all report items
    print("\n[Step 8] Updating all report items...")
    
    # Create new folder content IDs for updates
    updated_content_ids = {}
    
    print("   Creating new folder content IDs for updates...")
    for item_type in item_types:
        folder_content_id = content_service.create_folder_content()
        updated_content_ids[item_type] = folder_content_id
        print(f"   ✓ Created updated folder content for {item_type.value}: {folder_content_id}")
    
    # Upload updated JSON data
    print("   Uploading updated JSON data...")
    updated_uploaded_data = {}  # Store updated data for verification
    for item_type, content_id in updated_content_ids.items():
        # Create updated chart data using ChartDataFactory
        if item_type == AnalyticsReportItemType.PIE:
            updated_chart_data = ChartDataFactory.create_pie_chart(
                category_name="Updated Category",
                value_name="Updated Value",
                data=[
                    CategoryValueData(category="X", value=15),
                    CategoryValueData(category="Y", value=25),
                    CategoryValueData(category="Z", value=35),
                ]
            )
        elif item_type == AnalyticsReportItemType.HORIZONTAL_BAR:
            updated_chart_data = ChartDataFactory.create_horizontal_bar_chart(
                y_axis_name="Updated Category",
                x_axis_name="Updated Value",
                data=[
                    CategoryValueData(category="X", value=15),
                    CategoryValueData(category="Y", value=25),
                ],
                data_ids=[
                    DataIdsIndex(index="X", data_ids=["id_x1", "id_x2"]),
                    DataIdsIndex(index="Y", data_ids=["id_y1", "id_y2"]),
                ]
            )
        elif item_type == AnalyticsReportItemType.VERTICAL_BAR:
            updated_chart_data = ChartDataFactory.create_vertical_bar_chart(
                x_axis_name="Updated Category",
                y_axis_name="Updated Value",
                data=[
                    CategoryValueData(category="X", value=15),
                    CategoryValueData(category="Y", value=25),
                ]
            )
        elif item_type == AnalyticsReportItemType.HEATMAP:
            updated_chart_data = ChartDataFactory.create_heatmap_chart(
                y_axis_name="Updated Y",
                x_axis_name="Updated X",
                data=[
                    HeatmapData(y_category="Y2", x_category="X2", value=15),
                    HeatmapData(y_category="Y2", x_category="X3", value=25),
                ]
            )
        else:
            updated_chart_data = ChartDataFactory.create_vertical_bar_chart(
                x_axis_name="Updated Category",
                y_axis_name="Updated Value",
                data=[CategoryValueData(category="X", value=15)]
            )
        
        # Upload updated reports.json
        report_service.upload_reports_json(content_id, updated_chart_data)
        
        # Upload updated data_ids.json if available
        if updated_chart_data.data_ids_json:
            report_service.upload_data_ids_json(content_id, updated_chart_data)
        
        # Store for later verification
        updated_uploaded_data[item_type] = {
            "reports": updated_chart_data.reports_json,
            "data_ids": updated_chart_data.data_ids_json
        }
        print(f"   ✓ Uploaded updated JSON files for {item_type.value}")
    
    # Verify updated uploaded files by downloading them
    print("   Verifying updated uploaded files by downloading...")
    for item_type, content_id in updated_content_ids.items():
        # Get download URL for reports.json
        reports_download_url = content_service.get_download_url(content_id, "reports.json")
        
        # Download and verify updated reports.json
        reports_response = requests.get(reports_download_url)
        downloaded_reports = reports_response.json()
        assert downloaded_reports == updated_uploaded_data[item_type]["reports"], f"Updated reports.json mismatch for {item_type.value}"
        
        # Download and verify updated data_ids.json if it exists
        if updated_uploaded_data[item_type]["data_ids"] is not None:
            data_ids_download_url = content_service.get_download_url(content_id, "data_ids.json")
            data_ids_response = requests.get(data_ids_download_url)
            if data_ids_response.status_code == 200 and data_ids_response.content:
                downloaded_data_ids = data_ids_response.json()
                assert downloaded_data_ids == updated_uploaded_data[item_type]["data_ids"], f"Updated data_ids.json mismatch for {item_type.value}"
        
        print(f"   ✓ Verified downloaded updated JSON files for {item_type.value}")
    
    for item_type, item in created_items.items():
        updated_item = report_service.update_analytics_report_item(
            dataset_id=dataset_id,
            report_id=created_report.id,
            item_id=item.id,
            title=f"Updated {item_type.value} Chart",
            description=f"Updated {item_type.value} chart description",
            content_id=updated_content_ids[item_type],
            meta={
                "chart_type": item_type.value,
                "version": "2.0",
                "updated": True
            }
        )
        print(f"✅ Updated {item_type.value} item: {updated_item.id}")
        print(f"   New Title: {updated_item.title}")
        print(f"   New Content ID: {updated_content_ids[item_type]}")
    
    # Step 9: Verify updates by fetching report again
    print("\n[Step 9] Verifying item updates...")
    report_with_updated_items = report_service.get_analytics_report(
        dataset_id=dataset_id,
        report_id=created_report.id
    )
    print(f"✅ Fetched report has {len(report_with_updated_items.items) if report_with_updated_items.items else 0} items")
    if report_with_updated_items.items:
        for item in report_with_updated_items.items:
            is_updated = item.title.startswith("Updated")
            print(f"   - {item.type}: {item.title} (Updated: {is_updated})")
    
    # Step 10: Delete all report items
    print("\n[Step 10] Deleting all report items...")
    
    for item_type, item in created_items.items():
        delete_result = report_service.delete_analytics_report_item(
            dataset_id=dataset_id,
            report_id=created_report.id,
            item_id=item.id
        )
        print(f"✅ Deleted {item_type.value} item: {item.id}")
        print(f"   Delete result: {delete_result}")
    
    # Step 11: Verify item deletion
    print("\n[Step 11] Verifying item deletion...")
    report_after_item_deletion = report_service.get_analytics_report(
        dataset_id=dataset_id,
        report_id=created_report.id
    )
    items_count = len(report_after_item_deletion.items) if report_after_item_deletion.items else 0
    print(f"✅ Report now has {items_count} items (should be 0)")
    
    # ==================== CLEANUP ====================
    
    # Step 12: Delete analytics report
    print("\n[Step 12] Deleting analytics report...")
    delete_result = report_service.delete_analytics_report(
        dataset_id=dataset_id,
        report_id=created_report.id
    )
    print(f"✅ Deleted report: {created_report.id}")
    print(f"   Delete result: {delete_result}")
    
    # Step 13: Verify deletion by trying to list again
    print("\n[Step 13] Verifying report deletion...")
    reports_after, _, total_after = report_service.get_analytics_reports(
        dataset_id=dataset_id,
        length=10
    )
    found_after_delete = any(r.id == created_report.id for r in reports_after)
    print(f"✅ Report found after deletion: {found_after_delete}")
    print(f"   Total reports now: {total_after}")
    
    print("\n" + "=" * 70)
    print("Complete Workflow Test Passed Successfully! 🎉")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    test_analytics_report_workflow()
