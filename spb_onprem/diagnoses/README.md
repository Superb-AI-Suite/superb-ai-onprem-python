# Diagnosis Service Guide

Diagnosis 및 DiagnosisReportItem API 서비스 가이드.

## Overview

DiagnosisService는 데이터셋 내 diagnosis(진단) 및 report item 관리를 위한 서비스입니다. CRUD, 필터/정렬, 리포트 아이템 관리를 제공합니다.

## Core Operations

### Diagnosis
- **get_diagnosis()** - ID 또는 name으로 단일 diagnosis 조회
- **get_diagnoses()** - 필터/정렬/페이지네이션 목록 조회
- **create_diagnosis()** - diagnosis 생성
- **update_diagnosis()** - diagnosis 수정
- **delete_diagnosis()** - diagnosis 삭제

### DiagnosisReportItem
- **create_diagnosis_report_item()** - 리포트 아이템 생성
- **update_diagnosis_report_item()** - 리포트 아이템 수정
- **delete_diagnosis_report_item()** - 리포트 아이템 삭제

## Filtering

`DiagnosisFilter` / `DiagnosisFilterOptions`로 목록 필터링, `DiagnosisOrderBy`로 정렬 필드/방향 지정.

```python
from spb_onprem import DiagnosisService, DiagnosisFilter, DiagnosisFilterOptions
from spb_onprem.diagnoses import DiagnosisOrderBy, DiagnosisOrderField, OrderDirection

service = DiagnosisService()
filter = DiagnosisFilter(must=DiagnosisFilterOptions(status_in=["COMPLETED"]))
order_by = DiagnosisOrderBy(field=DiagnosisOrderField.CREATED_AT, direction=OrderDirection.DESC)
diagnoses, next_cursor, total = service.get_diagnoses(
    dataset_id="dataset-123",
    filter=filter,
    order_by=order_by,
    length=20,
)
```

## Testing

### 전체 SDK 테스트

프로젝트 루트에서:

```bash
# 의존성 설치 (최초 1회)
pip install -e .
pip install -r requirements-test.txt

# 전체 테스트 실행
pytest tests/ -v

# 특정 도메인만 실행
pytest tests/datasets/ -v
pytest tests/diagnoses/ -v
```

- **단위 테스트**: `request_gql`을 mock하여 API 호출 없이 서비스/파라미터 로직만 검증.
- **워크플로우 테스트**: 실제 서버 호출이 필요하며, CI에서는 기본 스킵. 로컬에서 실행하려면 해당 테스트에서 안내하는 환경 변수 설정 후 실행 (예: `RUN_MODEL_WORKFLOW_TESTS=1`).

### Diagnoses 단위 테스트만 실행

```bash
pytest tests/diagnoses/ -v
```

## Structural checklist (구조 점검)

diagnoses 도메인을 models/reports와 맞춰 둔 상태에서, 추가로 확인해 두면 좋은 항목입니다.

| 항목 | 상태 | 비고 |
|------|------|------|
| **PageInfo 엔티티** | ✅ | models/reports와 동일 패턴, `model_validate(response)` 사용 |
| **엔티티 alias** | ✅ | camelCase 필드는 `Field(..., alias="camelCase")` 사용 (diagnosis, report_item, page_info) |
| **Filter/OrderBy** | ✅ | `DiagnosisFilter`(must, not), `DiagnosisOrderBy`(field, direction), params에서 `model_dump(by_alias=True)` |
| **서비스 반환 타입** | ✅ | `get_diagnoses` → `Tuple[List[Diagnosis], Optional[str], int]` (규칙 28) |
| **request_gql 응답** | ✅ | `data[query_name]` 반환 → DiagnosisPageInfo 구조와 일치 (diagnoses, next, totalCount) |
| **GraphQL 변수명** | ✅ | 쿼리 `$dataset_id`, `$order_by` 등과 params 반환 키 일치 (snake_case) |
| **서비스 docstring** | 선택 | data처럼 Args/Returns 넣으면 가독성·IDE 도움 증가 |
| **create params의 None** | 선택 | 규칙 31: 선택 인자를 Undefined로 두고 params에서 키 생략 가능 (현재는 null 전송, 동작에는 문제 없음) |
| **Filter 필드명** | 선택 | models는 `must_filter`(alias "must"), diagnoses는 `must`(alias "must"). 동작 동일, 네이밍만 통일 시 `must_filter`로 맞출 수 있음 |
