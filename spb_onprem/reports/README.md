# 📈 Reports Module

Create, manage, and visualize analytics reports for your datasets with interactive charts and dashboards.

## 📋 Table of Contents
- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [Key Concepts](#-key-concepts)
- [Key Report Entities](#-key-report-entities)
- [Common Use Cases](#-common-use-cases)
- [Advanced Usage](#-advanced-usage)
- [Best Practices](#-best-practices)

## 🎯 Overview

The Reports module provides comprehensive analytics and visualization capabilities:
- **📊 Report Management**: Create and organize analytics reports
- **📈 Chart Types**: Support for pie charts, bar charts, and heatmaps
- **🎨 Visualization**: Link reports to visualization content (images, JSON data)
- **📁 Organization**: Group multiple chart items in a single report
- **🔄 Dynamic Updates**: Update reports as data changes

## 🚀 Quick Start

### Initialize the Service

```python
from spb_onprem import ReportService

# Create service instance
report_service = ReportService()
```

### Basic Report Operations

```python
# 1. List analytics reports
reports, next_cursor, total_count = report_service.get_analytics_reports(
    dataset_id="dataset_123",
    length=10
)

print(f"Found {total_count} reports")
for report in reports:
    print(f"- {report.title}")
    print(f"  Items: {len(report.items) if report.items else 0}")

# 2. Get a specific report
report = report_service.get_analytics_report(
    dataset_id="dataset_123",
    report_id="report_456"
)

print(f"Report: {report.title}")
print(f"Description: {report.description}")
if report.items:
    for item in report.items:
        print(f"  - {item.title} ({item.type})")

# 3. Create a new report
new_report = report_service.create_analytics_report(
    dataset_id="dataset_123",
    title="Dataset Quality Report - January 2025",
    description="Monthly data quality and annotation statistics",
    meta={
        "period": "2025-01",
        "generated_by": "analytics_pipeline"
    }
)

print(f"✅ Created report: {new_report.id}")
```

## 🔑 Key Concepts

### Report Structure

```python
AnalyticsReport:
  - id: Unique identifier
  - dataset_id: Parent dataset
  - title: Report title
  - description: Report description
  - items: List of AnalyticsReportItem (charts)
  - meta: Custom metadata
  - created_at, updated_at: Timestamps
```

### Report Item Types

The module supports four chart types:

```python
from spb_onprem.reports.entities import AnalyticsReportItemType

AnalyticsReportItemType.PIE              # Pie/donut charts
AnalyticsReportItemType.HORIZONTAL_BAR   # Horizontal bar charts
AnalyticsReportItemType.VERTICAL_BAR     # Vertical bar charts
AnalyticsReportItemType.HEATMAP          # Heatmaps
```

### Report Item Structure

```python
AnalyticsReportItem:
  - id: Unique identifier
  - type: Chart type (PIE, BAR, HEATMAP)
  - title: Chart title
  - description: Chart description
  - content: Reference to visualization file
  - meta: Custom chart metadata
```

## 📋 Key Report Entities

For detailed entity documentation with comprehensive field descriptions, see the entity files:

### Core Entities
- **[📈 AnalyticsReport](entities/analytics_report.py)** - Main report container with items
- **[📊 AnalyticsReportItem](entities/analytics_report_item.py)** - Individual chart/visualization
- **[📄 AnalyticsReportPageInfo](entities/analytics_report_page_info.py)** - Pagination information

Each entity file contains:
- **Comprehensive class documentation**
- **Detailed field descriptions with `description` parameter**
- **Usage examples and constraints**
- **Field aliases for API compatibility**

### Quick Entity Overview

```python
from spb_onprem.reports.entities import (
    AnalyticsReport,
    AnalyticsReportItem,
    AnalyticsReportItemType
)

# Entity relationship example
report = AnalyticsReport(
    title="Weekly Quality Report",
    description="Annotation quality metrics",
    items=[
        AnalyticsReportItem(
            type=AnalyticsReportItemType.PIE,
            title="Annotation Distribution"
        )
    ]
)

# Access field descriptions
field_info = AnalyticsReport.model_fields
print(f"Title field: {field_info['title'].description}")
print(f"Items field: {field_info['items'].description}")
```

## 💼 Common Use Cases

### 1. Create Data Quality Dashboard

```python
from spb_onprem.reports.entities import AnalyticsReportItemType

# Create main report
report = report_service.create_analytics_report(
    dataset_id="dataset_123",
    title="Data Quality Dashboard",
    description="Comprehensive quality metrics for the dataset"
)

# Add annotation distribution pie chart
pie_item = report_service.create_analytics_report_item(
    dataset_id="dataset_123",
    report_id=report.id,
    type=AnalyticsReportItemType.PIE,
    title="Annotation Type Distribution",
    description="Breakdown of annotation types in the dataset",
    content_id="content_pie_chart_001",  # Reference to generated chart
    meta={
        "total_annotations": 15000,
        "chart_colors": ["#FF6384", "#36A2EB", "#FFCE56"]
    }
)

# Add class distribution bar chart
bar_item = report_service.create_analytics_report_item(
    dataset_id="dataset_123",
    report_id=report.id,
    type=AnalyticsReportItemType.HORIZONTAL_BAR,
    title="Class Distribution",
    description="Number of annotations per class",
    content_id="content_bar_chart_001"
)

# Add quality heatmap
heatmap_item = report_service.create_analytics_report_item(
    dataset_id="dataset_123",
    report_id=report.id,
    type=AnalyticsReportItemType.HEATMAP,
    title="Quality Score Heatmap",
    description="Quality scores across different annotators and classes",
    content_id="content_heatmap_001"
)

print(f"✅ Created dashboard with {3} visualizations")
```

### 2. Weekly Progress Reports

```python
from datetime import datetime, timedelta

# Generate weekly report
week_start = datetime.now() - timedelta(days=7)
week_num = week_start.isocalendar()[1]

report = report_service.create_analytics_report(
    dataset_id="dataset_123",
    title=f"Weekly Progress Report - Week {week_num}",
    description=f"Progress summary for {week_start.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
    meta={
        "report_type": "weekly_progress",
        "week_number": week_num,
        "year": week_start.year,
        "generated_at": datetime.now().isoformat()
    }
)

# Add progress chart
progress_item = report_service.create_analytics_report_item(
    dataset_id="dataset_123",
    report_id=report.id,
    type=AnalyticsReportItemType.VERTICAL_BAR,
    title="Daily Annotation Progress",
    description="Annotations completed per day this week",
    content_id="content_weekly_progress_001",
    meta={
        "total_completed": 1250,
        "daily_average": 178
    }
)

print(f"✅ Weekly report created: {report.id}")
```

### 3. Model Performance Comparison

```python
# Create model comparison report
report = report_service.create_analytics_report(
    dataset_id="dataset_123",
    title="Model Performance Comparison Q1 2025",
    description="Comparing performance across different model architectures"
)

# Add AP score comparison
ap_chart = report_service.create_analytics_report_item(
    dataset_id="dataset_123",
    report_id=report.id,
    type=AnalyticsReportItemType.HORIZONTAL_BAR,
    title="Average Precision by Model",
    description="AP@0.5 scores for each model variant",
    content_id="content_ap_comparison_001",
    meta={
        "models": ["YOLOv8n", "YOLOv8s", "YOLOv8m"],
        "best_model": "YOLOv8m",
        "best_ap": 0.89
    }
)

# Add per-class heatmap
class_heatmap = report_service.create_analytics_report_item(
    dataset_id="dataset_123",
    report_id=report.id,
    type=AnalyticsReportItemType.HEATMAP,
    title="Per-Class Performance Matrix",
    description="AP scores for each class across models",
    content_id="content_class_heatmap_001"
)
```

### 4. Dataset Statistics Dashboard

```python
# Create comprehensive statistics report
stats_report = report_service.create_analytics_report(
    dataset_id="dataset_123",
    title="Dataset Statistics Overview",
    description="Complete statistical analysis of the dataset"
)

# Data type distribution
type_dist = report_service.create_analytics_report_item(
    dataset_id="dataset_123",
    report_id=stats_report.id,
    type=AnalyticsReportItemType.PIE,
    title="Data Type Distribution",
    description="Distribution of images, videos, and other data types",
    content_id="content_type_dist_001"
)

# Annotation counts
anno_counts = report_service.create_analytics_report_item(
    dataset_id="dataset_123",
    report_id=stats_report.id,
    type=AnalyticsReportItemType.VERTICAL_BAR,
    title="Annotations per Data Item",
    description="Distribution of annotation counts across dataset",
    content_id="content_anno_counts_001"
)
```

## 🔧 Advanced Usage

### Filtering Reports

```python
from spb_onprem.reports.params import (
    AnalyticsReportsFilter,
    AnalyticsReportsFilterOptions,
    AnalyticsReportsOrderBy,
    AnalyticsReportListOrderFields
)

# Filter by title
reports_filter = AnalyticsReportsFilter(
    must_filter=AnalyticsReportsFilterOptions(
        title_contains="Quality"
    )
)

# Sort by update time
order_by = AnalyticsReportsOrderBy(
    field=AnalyticsReportListOrderFields.UPDATED_AT,
    direction="DESC"
)

reports, cursor, total = report_service.get_analytics_reports(
    dataset_id="dataset_123",
    analytics_reports_filter=reports_filter,
    order_by=order_by,
    length=20
)

print(f"Found {total} quality reports")
```

### Updating Reports

```python
# Update report metadata
updated_report = report_service.update_analytics_report(
    dataset_id="dataset_123",
    report_id=report.id,
    title="Updated Dataset Quality Report - Q1 2025",
    description="Quarterly quality metrics with updated data",
    meta={
        "last_updated": datetime.now().isoformat(),
        "data_version": "v2.1",
        "reviewer": "data_team"
    }
)

# Update individual chart
updated_item = report_service.update_analytics_report_item(
    dataset_id="dataset_123",
    report_id=report.id,
    item_id=chart_item.id,
    title="Updated Annotation Distribution",
    content_id="content_updated_chart_001",
    meta={
        "regenerated_at": datetime.now().isoformat()
    }
)
```

### Pagination for Large Report Lists

```python
all_reports = []
cursor = None

while True:
    reports, cursor, total = report_service.get_analytics_reports(
        dataset_id="dataset_123",
        cursor=cursor,
        length=50
    )
    
    all_reports.extend(reports)
    print(f"Loaded {len(all_reports)}/{total} reports")
    
    if not cursor:
        break

print(f"✅ Loaded all {len(all_reports)} reports")
```

### Bulk Report Generation

```python
# Generate monthly reports for a year
from datetime import datetime
from dateutil.relativedelta import relativedelta

start_date = datetime(2024, 1, 1)
monthly_reports = []

for month in range(12):
    report_date = start_date + relativedelta(months=month)
    
    report = report_service.create_analytics_report(
        dataset_id="dataset_123",
        title=f"Monthly Report - {report_date.strftime('%B %Y')}",
        description=f"Quality and progress metrics for {report_date.strftime('%B %Y')}",
        meta={
            "report_type": "monthly",
            "month": report_date.month,
            "year": report_date.year
        }
    )
    
    monthly_reports.append(report)
    print(f"✅ Generated report for {report_date.strftime('%B %Y')}")

print(f"Total reports generated: {len(monthly_reports)}")
```

## 🎯 Best Practices

### 1. **Structured Report Naming**

```python
# Good: Clear, dated naming convention
title = f"{report_type} - {dataset_name} - {date_string}"
# Example: "Quality Report - Vehicles Dataset - 2025-01-15"

# Include report period in metadata
report = report_service.create_analytics_report(
    dataset_id=dataset_id,
    title=title,
    meta={
        "period_start": "2025-01-01",
        "period_end": "2025-01-31",
        "report_type": "quality",
        "frequency": "monthly"
    }
)
```

### 2. **Chart Organization**

```python
# Group related charts logically
sections = [
    {
        "name": "Data Overview",
        "charts": [
            {"type": "PIE", "title": "Data Type Distribution"},
            {"type": "VERTICAL_BAR", "title": "Data Count by Status"}
        ]
    },
    {
        "name": "Annotation Quality",
        "charts": [
            {"type": "HEATMAP", "title": "Quality Scores by Annotator"},
            {"type": "HORIZONTAL_BAR", "title": "Error Rates by Class"}
        ]
    }
]

for section in sections:
    for chart_config in section["charts"]:
        item = report_service.create_analytics_report_item(
            dataset_id=dataset_id,
            report_id=report_id,
            type=chart_config["type"],
            title=chart_config["title"],
            meta={"section": section["name"]}
        )
```

### 3. **Version Control for Reports**

```python
# Track report versions
report = report_service.create_analytics_report(
    dataset_id=dataset_id,
    title="Quality Report v3",
    meta={
        "version": "3.0",
        "previous_version_id": "report_v2_id",
        "changes": [
            "Added new heatmap visualization",
            "Updated class distribution metrics"
        ],
        "changelog_url": "https://docs.example.com/reports/v3-changelog"
    }
)
```

### 4. **Link to Source Data**

```python
# Reference source data for reproducibility
report = report_service.create_analytics_report(
    dataset_id=dataset_id,
    title="Model Performance Report",
    meta={
        "data_snapshot_id": "snapshot_20250115",
        "model_ids": ["model_123", "model_456"],
        "slice_ids": ["slice_test_001"],
        "query_filters": {
            "date_range": "2025-01-01 to 2025-01-31"
        }
    }
)
```

### 5. **Cleanup Old Reports**

```python
from datetime import datetime, timedelta

# Archive old reports
cutoff_date = (datetime.now() - timedelta(days=90)).isoformat()

reports, _, _ = report_service.get_analytics_reports(
    dataset_id=dataset_id,
    length=100
)

archived_count = 0
for report in reports:
    if report.created_at and report.created_at < cutoff_date:
        # Add archive tag before deletion
        report_service.update_analytics_report(
            dataset_id=dataset_id,
            report_id=report.id,
            meta={"archived": True, "archived_at": datetime.now().isoformat()}
        )
        archived_count += 1

print(f"📦 Archived {archived_count} old reports")
```

### 6. **Automated Report Generation**

```python
def generate_weekly_quality_report(dataset_id):
    """Generate standardized weekly quality report."""
    
    week_num = datetime.now().isocalendar()[1]
    
    # Create report
    report = report_service.create_analytics_report(
        dataset_id=dataset_id,
        title=f"Weekly Quality Report - Week {week_num}",
        description=f"Automated quality report for week {week_num}",
        meta={
            "automated": True,
            "generation_timestamp": datetime.now().isoformat(),
            "report_template": "weekly_quality_v1"
        }
    )
    
    # Add standard charts
    chart_configs = [
        {
            "type": AnalyticsReportItemType.PIE,
            "title": "Annotation Status Distribution",
            "content_generator": "generate_status_pie"
        },
        {
            "type": AnalyticsReportItemType.VERTICAL_BAR,
            "title": "Daily Annotation Volume",
            "content_generator": "generate_volume_bar"
        },
        {
            "type": AnalyticsReportItemType.HEATMAP,
            "title": "Annotator Performance Matrix",
            "content_generator": "generate_performance_heatmap"
        }
    ]
    
    for config in chart_configs:
        # Generate chart content (external process)
        content_id = generate_chart_content(config["content_generator"], dataset_id)
        
        # Add to report
        report_service.create_analytics_report_item(
            dataset_id=dataset_id,
            report_id=report.id,
            type=config["type"],
            title=config["title"],
            content_id=content_id
        )
    
    return report

# Schedule this function to run weekly
```

## 🔗 Related Modules

- **[📁 Datasets](../datasets/README.md)** - Parent container for reports
- **[📊 Data](../data/README.md)** - Source data for analytics
- **[🤖 Models](../models/README.md)** - Model performance metrics
- **[🔪 Slices](../slices/README.md)** - Data segments for targeted analysis

## ⚠️ Important Notes

- **Content References**: Reports reference visualization files via `content_id` - ensure content exists
- **Report Items**: Items belong to a specific report and are deleted when the report is deleted
- **Chart Types**: Use appropriate chart type for your data (PIE for proportions, BAR for comparisons, HEATMAP for matrices)
- **Metadata**: Use `meta` field for custom attributes and filtering
- **Performance**: Large numbers of items per report may impact loading performance

## 🆘 Common Issues

**Issue: Report item creation fails**
```python
# Solution: Verify content exists and report exists
from spb_onprem import ContentService

content_service = ContentService()
# Ensure content is created before referencing
```

**Issue: Chart type enum error**
```python
# Solution: Use the proper enum
from spb_onprem.reports.entities import AnalyticsReportItemType

# Correct
type=AnalyticsReportItemType.PIE

# Incorrect
type="PIE"  # String won't work properly
```

**Issue: Reports not filtering correctly**
```python
# Solution: Use proper filter structure
from spb_onprem.reports.params import (
    AnalyticsReportsFilter,
    AnalyticsReportsFilterOptions
)

# Correct filter
reports_filter = AnalyticsReportsFilter(
    must_filter=AnalyticsReportsFilterOptions(
        title_contains="Quality"
    )
)
```

---

**📚 Need more help?** Check the [main README](../../README.md) or explore related modules!
