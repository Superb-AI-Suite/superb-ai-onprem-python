# Chart Data Factory

모델 학습 결과와 데이터 분석을 시각화하기 위한 차트 데이터를 생성하는 팩토리 클래스입니다.

## 개요

`ChartDataFactory`는 9가지 차트 타입에 대한 데이터를 생성하고 검증합니다:
- **PIE**: 원형 차트 (클래스 분포, 비율 표시)
- **HORIZONTAL_BAR**: 가로 막대 차트 (카테고리별 비교)
- **VERTICAL_BAR**: 세로 막대 차트 (메트릭 비교)
- **HEATMAP**: 히트맵 (혼동 행렬, 상관관계)
- **TABLE**: 테이블 (상세 메트릭 표시)
- **LINE_CHART**: 선 그래프 (학습 곡선, 시계열 데이터)
- **SCATTER_PLOT**: 산점도 (두 변수 간 관계)
- **HISTOGRAM**: 히스토그램 (분포 시각화)
- **METRICS**: 주요 지표 (요약 통계)

## 설치 및 Import

```python
from spb_onprem.charts import (
    ChartDataFactory,
    ChartDataResult,
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
from spb_onprem.models import ModelService
```

## 기본 사용법

모든 차트 생성 메서드는 `ChartDataResult` 객체를 반환합니다:

```python
chart_data = ChartDataFactory.create_pie_chart(...)

# ChartDataResult 구조
# - reports_json: 차트 데이터 (필수)
# - data_ids_json: 데이터 ID 매핑 (선택)

# 업로드
model_service = ModelService()
model_service.upload_reports_json(content_id, chart_data)

if chart_data.data_ids_json:
    model_service.upload_data_ids_json(content_id, chart_data)
```

---

## 1. PIE 차트 (원형 차트)

**용도**: 카테고리별 비율, 클래스 분포 표시

### 예제: 객체 클래스 분포

```python
from spb_onprem.charts import ChartDataFactory, CategoryValueData, DataIdsIndex

# 데이터 생성
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
        DataIdsIndex(index="Person", data_ids=["data_4", "data_5"]),
    ]
)

# 결과 구조
# reports_json = {
#     "category_name": "Class",
#     "value_name": "Count",
#     "data": [
#         {"category": "Car", "value": 3421},
#         {"category": "Person", "value": 5672},
#         ...
#     ]
# }
#
# data_ids_json = {
#     "data_ids": [
#         {"index": "Car", "data_ids": ["data_1", "data_2", "data_3"]},
#         {"index": "Person", "data_ids": ["data_4", "data_5"]},
#     ]
# }
```

---

## 2. HORIZONTAL_BAR 차트 (가로 막대)

**용도**: 카테고리별 값 비교, 에포크별 손실 추이

### 예제: 학습 손실 (Training Loss)

```python
from spb_onprem.charts import ChartDataFactory, CategoryValueData

chart_data = ChartDataFactory.create_horizontal_bar_chart(
    category_name="Epoch",
    value_name="Training Loss",
    data=[
        CategoryValueData(category="Epoch 1", value=2.45),
        CategoryValueData(category="Epoch 2", value=1.89),
        CategoryValueData(category="Epoch 3", value=1.34),
        CategoryValueData(category="Epoch 4", value=0.92),
        CategoryValueData(category="Epoch 5", value=0.68),
        CategoryValueData(category="Epoch 6", value=0.51),
    ]
)
```

---

## 3. VERTICAL_BAR 차트 (세로 막대)

**용도**: 메트릭 비교, 성능 지표 표시

### 예제: 모델 평가 메트릭

```python
from spb_onprem.charts import ChartDataFactory, CategoryValueData

chart_data = ChartDataFactory.create_vertical_bar_chart(
    category_name="Metric",
    value_name="Score",
    data=[
        CategoryValueData(category="Precision", value=0.92),
        CategoryValueData(category="Recall", value=0.88),
        CategoryValueData(category="F1-Score", value=0.90),
        CategoryValueData(category="mAP", value=0.85),
        CategoryValueData(category="IoU", value=0.78),
    ]
)
```

---

## 4. HEATMAP 차트 (히트맵)

**용도**: 혼동 행렬(Confusion Matrix), 상관관계 표시

### 예제: Confusion Matrix

```python
from spb_onprem.charts import ChartDataFactory, HeatmapData, XYDataIds

chart_data = ChartDataFactory.create_heatmap_chart(
    y_axis_name="True Label",
    x_axis_name="Predicted Label",
    data=[
        # True Label: Car
        HeatmapData(y_category="Car", x_category="Car", value=452),
        HeatmapData(y_category="Car", x_category="Truck", value=23),
        HeatmapData(y_category="Car", x_category="Bus", value=8),
        
        # True Label: Truck
        HeatmapData(y_category="Truck", x_category="Car", value=15),
        HeatmapData(y_category="Truck", x_category="Truck", value=387),
        HeatmapData(y_category="Truck", x_category="Bus", value=12),
        
        # True Label: Bus
        HeatmapData(y_category="Bus", x_category="Car", value=5),
        HeatmapData(y_category="Bus", x_category="Truck", value=18),
        HeatmapData(y_category="Bus", x_category="Bus", value=234),
    ],
    data_ids=[
        XYDataIds(x="Car", y="Car", data_ids=["data_1", "data_2"]),
        XYDataIds(x="Truck", y="Car", data_ids=["data_3"]),
    ]
)

# data_ids는 특정 셀에 해당하는 데이터 ID를 매핑
# 예: (True=Car, Predicted=Car) 셀의 데이터는 ["data_1", "data_2"]
```

---

## 5. TABLE 차트 (테이블)

**용도**: 클래스별 상세 메트릭, 통계 표시

### 예제: 클래스별 성능 지표

```python
from spb_onprem.charts import ChartDataFactory, XYDataIds

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
        # (column, row) 조합으로 특정 셀 지정
        XYDataIds(x="Precision", y="Car", data_ids=["data_1"]),
        XYDataIds(x="Recall", y="Car", data_ids=["data_2"]),
    ]
)

# 주의: 모든 row는 headers와 동일한 길이여야 함
```

---

## 6. LINE_CHART 차트 (선 그래프)

**용도**: 학습 곡선, 시간에 따른 변화 추이

### 예제: Train/Validation 정확도 곡선

```python
from spb_onprem.charts import ChartDataFactory, LineChartData, LineChartDataIds

chart_data = ChartDataFactory.create_line_chart(
    x_name="Epoch",
    y_name="Accuracy",
    data=[
        # Train 시리즈
        LineChartData(series="Train", x=1, y=0.65),
        LineChartData(series="Train", x=2, y=0.73),
        LineChartData(series="Train", x=3, y=0.81),
        LineChartData(series="Train", x=4, y=0.87),
        LineChartData(series="Train", x=5, y=0.91),
        
        # Validation 시리즈
        LineChartData(series="Validation", x=1, y=0.62),
        LineChartData(series="Validation", x=2, y=0.68),
        LineChartData(series="Validation", x=3, y=0.75),
        LineChartData(series="Validation", x=4, y=0.82),
        LineChartData(series="Validation", x=5, y=0.85),
    ],
    data_ids=[
        # (series, x) 조합으로 데이터 포인트 지정
        LineChartDataIds(series="Train", x="1", data_ids=["data_1", "data_2"]),
        LineChartDataIds(series="Validation", x="1", data_ids=["data_3"]),
    ]
)

# series 필드는 필수 (여러 선을 그리기 위해)
# x는 숫자, 문자열, 날짜 모두 가능
```

---

## 7. SCATTER_PLOT 차트 (산점도)

**용도**: 두 변수 간 관계, 모델 성능 vs 추론 시간

### 예제: 추론 시간 vs 정확도

```python
from spb_onprem.charts import ChartDataFactory, ScatterPlotData, DataIdsIndex

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

# category는 선택 사항 (점들을 그룹화할 때 사용)
```

---

## 8. HISTOGRAM 차트 (히스토그램)

**용도**: 분포 시각화, 신뢰도 점수 분포

### 예제: 예측 신뢰도 점수 분포

```python
from spb_onprem.charts import ChartDataFactory, BinFrequencyData, DataIdsIndex

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
        DataIdsIndex(index="0.8-0.9", data_ids=["data_4", "data_5"]),
    ]
)

# bin은 문자열로 범위를 표시 (예: "0-10", "10-20")
```

---

## 9. METRICS 차트 (주요 지표)

**용도**: 학습 요약, 주요 통계 표시

### 예제: 학습 요약 지표

```python
from spb_onprem.charts import ChartDataFactory, MetricData

chart_data = ChartDataFactory.create_metrics_chart(
    metrics=[
        MetricData(key="Total Epochs", value=50),
        MetricData(key="Best Epoch", value=47),
        MetricData(key="Final Loss", value=0.0234),
        MetricData(key="Best Accuracy", value=0.9567),
        MetricData(key="Training Time", value="2h 34m"),
        MetricData(key="GPU Usage", value="87.3%"),
        MetricData(key="Model Size", value="245 MB"),
        # Dictionary 값도 가능
        MetricData(key="Parameters", value={
            "total": 25600000,
            "trainable": 25550000
        }),
    ],
    data_ids=["data_1", "data_2", "data_3"]
)

# value는 str, int, float, dict 모두 가능
# 같은 key를 여러 번 사용할 수 있음 (List[MetricData])
```

---

## 완전한 워크플로우 예제

```python
from spb_onprem import ModelService, ContentService
from spb_onprem.charts import ChartDataFactory, CategoryValueData

# 서비스 초기화
model_service = ModelService()
content_service = ContentService()

# 1. Content 폴더 생성
folder_content = content_service.create_content(
    dataset_id="your-dataset-id",
    name="training_metrics_pie_chart",
    content_type="FOLDER"
)
content_id = folder_content.id

# 2. 차트 데이터 생성
chart_data = ChartDataFactory.create_pie_chart(
    category_name="Class",
    value_name="Count",
    data=[
        CategoryValueData(category="Car", value=3421),
        CategoryValueData(category="Person", value=5672),
    ]
)

# 3. reports.json 업로드
model_service.upload_reports_json(content_id, chart_data)

# 4. data_ids.json 업로드 (있는 경우)
if chart_data.data_ids_json:
    model_service.upload_data_ids_json(content_id, chart_data)

# 5. Training Report Item 생성
model_service.create_training_report_item(
    dataset_id="your-dataset-id",
    model_id="your-model-id",
    name="Class Distribution",
    type=AnalyticsReportItemType.PIE,
    content_id=content_id,
    description="Distribution of object classes in training data"
)
```

---

## 데이터 모델 참조

### CategoryValueData
```python
CategoryValueData(
    category: str,        # 카테고리 이름
    value: Union[int, float]  # 값 (정수 또는 실수)
)
```

### HeatmapData
```python
HeatmapData(
    y_category: str,      # Y축 카테고리
    x_category: str,      # X축 카테고리
    value: Union[int, float]  # 셀 값
)
```

### LineChartData
```python
LineChartData(
    series: str,          # 시리즈 이름 (필수)
    x: Union[int, float, str],  # X 값 (숫자 또는 문자열)
    y: Union[int, float]  # Y 값
)
```

### ScatterPlotData
```python
ScatterPlotData(
    x: Union[int, float],     # X 값
    y: Union[int, float],     # Y 값
    category: Optional[str]   # 카테고리 (선택)
)
```

### BinFrequencyData
```python
BinFrequencyData(
    bin: str,             # 구간 이름 (예: "0-10")
    frequency: Union[int, float]  # 빈도
)
```

### MetricData
```python
MetricData(
    key: str,             # 메트릭 이름
    value: Union[str, int, float, Dict[str, Any]]  # 값
)
```

### DataIdsIndex
```python
DataIdsIndex(
    index: str,           # 인덱스 키 (카테고리, bin 등)
    data_ids: List[str]   # 데이터 ID 리스트
)
```

### XYDataIds
```python
XYDataIds(
    x: str,               # X 좌표 (컬럼, x_category)
    y: str,               # Y 좌표 (행, y_category)
    data_ids: List[str]   # 데이터 ID 리스트
)
```

### LineChartDataIds
```python
LineChartDataIds(
    series: str,          # 시리즈 이름
    x: str,               # X 값 (문자열)
    data_ids: List[str]   # 데이터 ID 리스트
)
```

---

## 타입 안전성

모든 차트 생성 메서드는 `ChartDataResult`만 반환하며, `ReportService`와 `ModelService`의 업로드 메서드는 `ChartDataResult`만 허용합니다:

```python
# ✅ 올바른 사용
chart_data = ChartDataFactory.create_pie_chart(...)  # ChartDataResult 반환
model_service.upload_reports_json(content_id, chart_data)

# ❌ 잘못된 사용
model_service.upload_reports_json(content_id, {"data": [...]})  # 오류!
```

---

## 에러 처리

```python
# Validation 에러
try:
    chart_data = ChartDataFactory.create_table_chart(
        headers=["A", "B"],
        rows=[["value1"]],  # 길이 불일치
    )
except ValueError as e:
    print(f"Validation error: {e}")

# data_ids가 없을 때
chart_data = ChartDataFactory.create_pie_chart(...)
if chart_data.data_ids_json:
    model_service.upload_data_ids_json(content_id, chart_data)
else:
    print("No data_ids to upload")
```

---

## 참고사항

1. **data_ids는 선택 사항**: 차트 데이터와 실제 데이터셋의 데이터를 연결할 때만 사용
2. **Pydantic 검증**: 모든 입력 데이터는 자동으로 검증됨
3. **타입 힌트**: IDE 자동완성과 타입 체크 지원
4. **Python 3.9+**: Python 3.9 이상에서 사용 가능

## 추가 예제

전체 워크플로우 예제는 `tests/models/test_workflow.py`를 참고하세요.
