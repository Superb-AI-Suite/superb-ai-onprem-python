# Reports Module

Analytics reports를 생성하고 관리하는 모듈입니다.

## 기본 사용법

```python
from spb_onprem import ReportService, ContentService
from spb_onprem.reports.entities import AnalyticsReportItemType

report_service = ReportService()
content_service = ContentService()

# 1. Report 생성
report = report_service.create_analytics_report(
    dataset_id="dataset_123",
    title="Dataset Analysis Report",
    description="Statistical analysis of dataset"
)

# 2. Chart 데이터 생성 및 업로드
# (차트 데이터 형식은 아래 Chart Data Formats 섹션 참조)

# 3. Report Item 추가
report_item = report_service.create_analytics_report_item(
    dataset_id="dataset_123",
    report_id=report.id,
    type=AnalyticsReportItemType.PIE,
    title="Class Distribution",
    description="Distribution of classes in the dataset",
    content_id=folder_content_id
)
```

## Chart Data Formats

각 차트 타입별로 정확한 데이터 형식이 필요합니다.

### PIE Chart

```python
from collections import defaultdict

# 1. 데이터 수집
behavior_status_counts = defaultdict(int)
behavior_status_data_ids = defaultdict(list)

for data_item in dataset:
    for annotation in data_item.annotations:
        status = annotation.behavior_status  # 예: "Walking", "Running", "Standing"
        behavior_status_counts[status] += 1
        behavior_status_data_ids[status].append(data_item.id)

# 2. chart_data 생성 (category_name, value_name 필수)
chart_data = {
    "category_name": "Behavior Status",
    "value_name": "Count",
    "data": [
        {"category": category, "value": count}
        for category, count in sorted(behavior_status_counts.items(), key=lambda x: x[1], reverse=True)
    ]
}

# 3. data_ids_data 생성
data_ids_data = [
    {"index": category, "data_ids": list(behavior_status_data_ids[category])}
    for category, _ in sorted(behavior_status_counts.items(), key=lambda x: x[1], reverse=True)
]

# 4. Content 업로드
folder_content_id = content_service.create_folder_content()
report_service.upload_reports_json(folder_content_id, chart_data)
report_service.upload_data_ids_json(folder_content_id, data_ids_data)

# 5. Report Item 생성
report_item = report_service.create_analytics_report_item(
    dataset_id=dataset_id,
    report_id=report_id,
    type=AnalyticsReportItemType.PIE,
    title="Behavior Status Distribution",
    description="Pie chart showing the distribution of behavior status",
    content_id=folder_content_id
)
```

**실제 데이터 예시:**

```python
# chart_data 예시
chart_data = {
    "category_name": "Behavior Status",
    "value_name": "Count",
    "data": [
        {"category": "Walking", "value": 145},
        {"category": "Running", "value": 89},
        {"category": "Standing", "value": 67},
        {"category": "Sitting", "value": 43}
    ]
}

# data_ids_data 예시
data_ids_data = [
    {
        "index": "Walking",
        "data_ids": [
            "01HX3K8F9J2MZWQP6R7S8T9V0A",
            "01HX3K8F9K3NAXRQ7S8T9U0W1B",
            "01HX3K8F9L4OBYSZ8T9U0V1X2C"
            # ... 145개
        ]
    },
    {
        "index": "Running",
        "data_ids": [
            "01HX3K8F9M5PCZTA9U0V1W2Y3D",
            "01HX3K8F9N6QDAUB0V1W2X3Z4E"
            # ... 89개
        ]
    },
    {
        "index": "Standing",
        "data_ids": [
            "01HX3K8F9P7REBVC1W2X3Y4A5F",
            "01HX3K8F9Q8SFCWD2X3Y4Z5B6G"
            # ... 67개
        ]
    },
    {
        "index": "Sitting",
        "data_ids": [
            "01HX3K8F9R9TGDXE3Y4Z5A6C7H",
            "01HX3K8F9S0UHEYF4Z5A6B7D8I"
            # ... 43개
        ]
    }
]
```

### VERTICAL_BAR / HORIZONTAL_BAR Chart

```python
from collections import defaultdict

# 1. 데이터 수집
class_counts = defaultdict(int)
class_data_ids = defaultdict(list)

for data_item in dataset:
    for annotation in data_item.annotations:
        class_name = annotation.class_name  # 예: "Car", "Person", "Bicycle"
        class_counts[class_name] += 1
        class_data_ids[class_name].append(data_item.id)

# 2. chart_data 생성 (y_axis_name, x_axis_name 필수)
chart_data = {
    "y_axis_name": "Class",
    "x_axis_name": "Count",
    "data": [
        {"category": category, "value": count}
        for category, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
    ]
}

# 3. data_ids_data 생성
data_ids_data = [
    {"index": category, "data_ids": list(class_data_ids[category])}
    for category, _ in sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
]

# 4. Content 업로드
folder_content_id = content_service.create_folder_content()
report_service.upload_reports_json(folder_content_id, chart_data)
report_service.upload_data_ids_json(folder_content_id, data_ids_data)

# 5. Report Item 생성
report_item = report_service.create_analytics_report_item(
    dataset_id=dataset_id,
    report_id=report_id,
    type=AnalyticsReportItemType.VERTICAL_BAR,  # 또는 HORIZONTAL_BAR
    title="Class Distribution",
    description="Bar chart showing the distribution of classes",
    content_id=folder_content_id
)
```

**실제 데이터 예시:**

```python
# chart_data 예시
chart_data = {
    "y_axis_name": "Class",
    "x_axis_name": "Count",
    "data": [
        {"category": "Car", "value": 523},
        {"category": "Person", "value": 412},
        {"category": "Bicycle", "value": 198},
        {"category": "Motorcycle", "value": 87},
        {"category": "Bus", "value": 45}
    ]
}

# data_ids_data 예시
data_ids_data = [
    {
        "index": "Car",
        "data_ids": [
            "01HX3K8F9T1VIFZG5A6B7C8D9E",
            "01HX3K8F9U2WJGAH6B7C8D9E0F",
            "01HX3K8F9V3XKHBI7C8D9E0F1G"
            # ... 523개
        ]
    },
    {
        "index": "Person",
        "data_ids": [
            "01HX3K8F9W4YLICJ8D9E0F1G2H",
            "01HX3K8F9X5ZMJDK9E0F1G2H3I"
            # ... 412개
        ]
    },
    {
        "index": "Bicycle",
        "data_ids": [
            "01HX3K8F9Y6ANKEL0F1G2H3I4J",
            "01HX3K8F9Z7BOLFM1G2H3I4J5K"
            # ... 198개
        ]
    },
    {
        "index": "Motorcycle",
        "data_ids": [
            "01HX3K8FA08CPMGN2H3I4J5K6L",
            "01HX3K8FA19DQNHO3I4J5K6L7M"
            # ... 87개
        ]
    },
    {
        "index": "Bus",
        "data_ids": [
            "01HX3K8FA2AEROIP4J5K6L7M8N",
            "01HX3K8FA3BFSPJQ5K6L7M8N9O"
            # ... 45개
        ]
    }
]
```

### HEATMAP Chart

```python
from collections import defaultdict

# 1. 데이터 수집
heatmap_counts = defaultdict(int)
heatmap_data_ids = defaultdict(list)

for data_item in dataset:
    for annotation in data_item.annotations:
        behavior_status = annotation.behavior_status  # Y축
        class_name = annotation.class_name  # X축
        key = (behavior_status, class_name)
        heatmap_counts[key] += 1
        heatmap_data_ids[key].append(data_item.id)

# 2. chart_data 생성 (y_axis_name, x_axis_name 필수, y_category, x_category 사용)
chart_data = {
    "y_axis_name": "Behavior Status",
    "x_axis_name": "Class",
    "data": [
        {"y_category": y_cat, "x_category": x_cat, "value": count}
        for (y_cat, x_cat), count in sorted(heatmap_counts.items(), key=lambda x: x[1], reverse=True)
    ]
}

# 3. data_ids_data 생성 (y, x 사용)
data_ids_data = [
    {"y": y_cat, "x": x_cat, "data_ids": list(heatmap_data_ids[(y_cat, x_cat)])}
    for (y_cat, x_cat), _ in sorted(heatmap_counts.items(), key=lambda x: x[1], reverse=True)
]

# 4. Content 업로드
folder_content_id = content_service.create_folder_content()
report_service.upload_reports_json(folder_content_id, chart_data)
report_service.upload_data_ids_json(folder_content_id, data_ids_data)

# 5. Report Item 생성
report_item = report_service.create_analytics_report_item(
    dataset_id=dataset_id,
    report_id=report_id,
    type=AnalyticsReportItemType.HEATMAP,
    title="Behavior Status vs Class Heatmap",
    description="Heatmap showing the relationship between behavior status and class",
    content_id=folder_content_id
)
```

**실제 데이터 예시:**

```python
# chart_data 예시
chart_data = {
    "y_axis_name": "Behavior Status",
    "x_axis_name": "Class",
    "data": [
        {"y_category": "Walking", "x_category": "Person", "value": 234},
        {"y_category": "Running", "x_category": "Person", "value": 156},
        {"y_category": "Standing", "x_category": "Person", "value": 89},
        {"y_category": "Sitting", "x_category": "Person", "value": 45},
        {"y_category": "Moving", "x_category": "Car", "value": 412},
        {"y_category": "Parked", "x_category": "Car", "value": 178},
        {"y_category": "Moving", "x_category": "Bicycle", "value": 123},
        {"y_category": "Parked", "x_category": "Bicycle", "value": 67}
    ]
}

# data_ids_data 예시
data_ids_data = [
    {
        "y": "Walking",
        "x": "Person",
        "data_ids": [
            "01HX3K8FA4CGTQKR6L7M8N9O0P",
            "01HX3K8FA5DHURLR7M8N9O0P1Q",
            "01HX3K8FA6EIVSMR8N9O0P1Q2R"
            # ... 234개
        ]
    },
    {
        "y": "Running",
        "x": "Person",
        "data_ids": [
            "01HX3K8FA7FJWTNS9O0P1Q2R3S",
            "01HX3K8FA8GKXUOT0P1Q2R3S4T"
            # ... 156개
        ]
    },
    {
        "y": "Standing",
        "x": "Person",
        "data_ids": [
            "01HX3K8FA9HLYVPU1Q2R3S4T5U",
            "01HX3K8FAA0IMZWQV2R3S4T5U6V"
            # ... 89개
        ]
    },
    {
        "y": "Sitting",
        "x": "Person",
        "data_ids": [
            "01HX3K8FAB1JNAXRW3S4T5U6V7W",
            "01HX3K8FAC2KOBYSX4T5U6V7W8X"
            # ... 45개
        ]
    },
    {
        "y": "Moving",
        "x": "Car",
        "data_ids": [
            "01HX3K8FAD3LPCZT5U6V7W8X9Y",
            "01HX3K8FAE4MQDAU6V7W8X9Y0Z"
            # ... 412개
        ]
    },
    {
        "y": "Parked",
        "x": "Car",
        "data_ids": [
            "01HX3K8FAF5NREBV7W8X9Y0Z1A",
            "01HX3K8FAG6OSFCW8X9Y0Z1A2B"
            # ... 178개
        ]
    },
    {
        "y": "Moving",
        "x": "Bicycle",
        "data_ids": [
            "01HX3K8FAH7PTGDX9Y0Z1A2B3C",
            "01HX3K8FAI8QUHEY0Z1A2B3C4D"
            # ... 123개
        ]
    },
    {
        "y": "Parked",
        "x": "Bicycle",
        "data_ids": [
            "01HX3K8FAJ9RVIFZ1A2B3C4D5E",
            "01HX3K8FAK0SWJGA2B3C4D5E6F"
            # ... 67개
        ]
    }
]
```

## Chart Data Format 요약

### PIE Chart
- **chart_data**: `category_name`, `value_name`, `data` (각 항목: `category`, `value`)
- **data_ids_data**: 각 항목에 `index`, `data_ids`

### BAR Chart (VERTICAL/HORIZONTAL)
- **chart_data**: `y_axis_name`, `x_axis_name`, `data` (각 항목: `category`, `value`)
- **data_ids_data**: 각 항목에 `index`, `data_ids`

### HEATMAP
- **chart_data**: `y_axis_name`, `x_axis_name`, `data` (각 항목: `y_category`, `x_category`, `value`)
- **data_ids_data**: 각 항목에 `y`, `x`, `data_ids`

## 주요 메서드

```python
# Report 조회
reports, cursor, total = report_service.get_analytics_reports(
    dataset_id="dataset_123",
    length=10
)

# Report 상세 조회
report = report_service.get_analytics_report(
    dataset_id="dataset_123",
    report_id="report_456"
)

# Report 삭제
report_service.delete_analytics_report(
    dataset_id="dataset_123",
    report_id="report_456"
)

# Report Item 삭제
report_service.delete_analytics_report_item(
    dataset_id="dataset_123",
    report_id="report_456",
    item_id="item_789"
)
```
