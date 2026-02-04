from typing import Optional, List, Tuple, Union

from spb_onprem.base_service import BaseService
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.exceptions import BadParameterError
from spb_onprem.contents.service import ContentService
from spb_onprem.charts import ChartDataResult

from .queries import Queries
from .entities import (
    Diagnosis,
    DiagnosisReportItem,
    AnalyticsReportItemType,
    DiagnosisPageInfo,
    DiagnosisStatus,
)
from .params import (
    DiagnosisFilter,
    DiagnosisOrderBy,
)


class DiagnosisService(BaseService):
    """Diagnosis 및 DiagnosisReportItem API 서비스"""

    def get_diagnosis(
        self,
        dataset_id: str,
        diagnosis_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Optional[Diagnosis]:
        """diagnosis_id 또는 name으로 단일 diagnosis 조회.

        Args:
            dataset_id (str): Dataset ID.
            diagnosis_id (Optional[str], optional): Diagnosis ID. Defaults to None.
            name (Optional[str], optional): Diagnosis 이름. Defaults to None.

        Raises:
            BadParameterError: dataset_id 미제공 시, 또는 diagnosis_id와 name 둘 다 미제공 시.

        Returns:
            Optional[Diagnosis]: 조회된 diagnosis, 없으면 None.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if not diagnosis_id and not name:
            raise BadParameterError("Either diagnosis_id or name must be provided.")

        response = self.request_gql(
            Queries.GET,
            Queries.GET["variables"](
                dataset_id=dataset_id,
                diagnosis_id=diagnosis_id if diagnosis_id else Undefined,
                name=name if name else Undefined,
            ),
        )
        return Diagnosis.model_validate(response) if response is not None else None

    def get_diagnosis_by_name(
        self,
        dataset_id: str,
        name: str,
    ) -> Optional[Diagnosis]:
        """이름으로 단일 diagnosis 조회.

        Args:
            dataset_id (str): Dataset ID.
            name (str): Diagnosis 이름.

        Returns:
            Optional[Diagnosis]: 조회된 diagnosis, 없으면 None.
        """
        return self.get_diagnosis(dataset_id=dataset_id, name=name)

    def get_diagnoses(
        self,
        dataset_id: str,
        filter: Optional[DiagnosisFilter] = None,
        order_by: Optional[DiagnosisOrderBy] = None,
        cursor: Optional[str] = None,
        length: int = 10,
    ) -> Tuple[List[Diagnosis], Optional[str], int]:
        """diagnosis 목록 조회 (필터/정렬/페이지네이션).

        Args:
            dataset_id (str): Dataset ID.
            filter (Optional[DiagnosisFilter], optional): 필터 조건. Defaults to None.
            order_by (Optional[DiagnosisOrderBy], optional): 정렬 조건. Defaults to None.
            cursor (Optional[str], optional): 페이지 커서. Defaults to None.
            length (int, optional): 페이지 크기 (1–50). Defaults to 10.

        Raises:
            BadParameterError: dataset_id 미제공 시.

        Returns:
            Tuple[List[Diagnosis], Optional[str], int]: (diagnosis 목록, 다음 커서, 전체 개수).
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")

        response = self.request_gql(
            Queries.GET_LIST,
            Queries.GET_LIST["variables"](
                dataset_id=dataset_id,
                filter=filter,
                order_by=order_by,
                cursor=cursor,
                length=length,
            ),
        )

        page_info = DiagnosisPageInfo.model_validate(response)
        diagnoses = page_info.diagnoses or []
        return (
            diagnoses,
            page_info.next,
            page_info.total_count or 0,
        )

    def create_diagnosis(
        self,
        dataset_id: str,
        name: str,
        description: Optional[str] = None,
        score_key: Optional[str] = None,
        score_value: Optional[float] = None,
        score_unit: Optional[str] = None,
        diagnosis_parameters: Optional[dict] = None,
        contents: Optional[dict] = None,
        source_slice_id: Optional[str] = None,
        target_slice_id: Optional[str] = None,
        source_data_count: Optional[int] = None,
        target_data_count: Optional[int] = None,
        diagnosis_data_count: Optional[int] = None,
    ) -> Diagnosis:
        """diagnosis 생성.

        Args:
            dataset_id (str): Dataset ID.
            name (str): Diagnosis 이름.
            description (Optional[str], optional): 설명. Defaults to None.
            score_key (Optional[str], optional): Score 키. Defaults to None.
            score_value (Optional[float], optional): Score 값. Defaults to None.
            score_unit (Optional[str], optional): Score 단위. Defaults to None.
            diagnosis_parameters (Optional[dict], optional): 진단 파라미터(JSON). Defaults to None.
            contents (Optional[dict], optional): 컨텐츠(JSON). Defaults to None.
            source_slice_id (Optional[str], optional): 소스 슬라이스 ID. Defaults to None.
            target_slice_id (Optional[str], optional): 타겟 슬라이스 ID. Defaults to None.
            source_data_count (Optional[int], optional): 소스 데이터 개수. Defaults to None.
            target_data_count (Optional[int], optional): 타겟 데이터 개수. Defaults to None.
            diagnosis_data_count (Optional[int], optional): 진단 데이터 개수. Defaults to None.

        Returns:
            Diagnosis: 생성된 diagnosis.
        """
        response = self.request_gql(
            Queries.CREATE,
            Queries.CREATE["variables"](
                dataset_id=dataset_id,
                name=name,
                description=description,
                score_key=score_key,
                score_value=score_value,
                score_unit=score_unit,
                diagnosis_parameters=diagnosis_parameters,
                contents=contents,
                source_slice_id=source_slice_id,
                target_slice_id=target_slice_id,
                source_data_count=source_data_count,
                target_data_count=target_data_count,
                diagnosis_data_count=diagnosis_data_count,
            ),
        )
        return Diagnosis.model_validate(response)

    def update_diagnosis(
        self,
        dataset_id: str,
        diagnosis_id: str,
        name: Union[Optional[str], UndefinedType] = Undefined,
        description: Union[Optional[str], UndefinedType] = Undefined,
        status: Union[Optional[DiagnosisStatus], UndefinedType] = Undefined,
        score_key: Union[Optional[str], UndefinedType] = Undefined,
        score_value: Union[Optional[float], UndefinedType] = Undefined,
        score_unit: Union[Optional[str], UndefinedType] = Undefined,
        diagnosis_parameters: Union[Optional[dict], UndefinedType] = Undefined,
        contents: Union[Optional[dict], UndefinedType] = Undefined,
        source_slice_id: Union[Optional[str], UndefinedType] = Undefined,
        target_slice_id: Union[Optional[str], UndefinedType] = Undefined,
        source_data_count: Union[Optional[int], UndefinedType] = Undefined,
        target_data_count: Union[Optional[int], UndefinedType] = Undefined,
        diagnosis_data_count: Union[Optional[int], UndefinedType] = Undefined,
    ) -> Diagnosis:
        """diagnosis 수정. 전달한 필드만 갱신되며, 미전달 필드는 기존 값 유지.

        Args:
            dataset_id (str): Dataset ID.
            diagnosis_id (str): Diagnosis ID.
            name (Union[Optional[str], UndefinedType], optional): 이름. Defaults to Undefined.
            description (Union[Optional[str], UndefinedType], optional): 설명. Defaults to Undefined.
            status (Union[Optional[DiagnosisStatus], UndefinedType], optional): 상태. Defaults to Undefined.
            score_key (Union[Optional[str], UndefinedType], optional): Score 키. Defaults to Undefined.
            score_value (Union[Optional[float], UndefinedType], optional): Score 값. Defaults to Undefined.
            score_unit (Union[Optional[str], UndefinedType], optional): Score 단위. Defaults to Undefined.
            diagnosis_parameters (Union[Optional[dict], UndefinedType], optional): 진단 파라미터. Defaults to Undefined.
            contents (Union[Optional[dict], UndefinedType], optional): 컨텐츠. Defaults to Undefined.
            source_slice_id (Union[Optional[str], UndefinedType], optional): 소스 슬라이스 ID. Defaults to Undefined.
            target_slice_id (Union[Optional[str], UndefinedType], optional): 타겟 슬라이스 ID. Defaults to Undefined.
            source_data_count (Union[Optional[int], UndefinedType], optional): 소스 데이터 개수. Defaults to Undefined.
            target_data_count (Union[Optional[int], UndefinedType], optional): 타겟 데이터 개수. Defaults to Undefined.
            diagnosis_data_count (Union[Optional[int], UndefinedType], optional): 진단 데이터 개수. Defaults to Undefined.

        Returns:
            Diagnosis: 수정된 diagnosis.
        """
        response = self.request_gql(
            Queries.UPDATE,
            Queries.UPDATE["variables"](
                dataset_id=dataset_id,
                diagnosis_id=diagnosis_id,
                name=name,
                description=description,
                status=status,
                score_key=score_key,
                score_value=score_value,
                score_unit=score_unit,
                diagnosis_parameters=diagnosis_parameters,
                contents=contents,
                source_slice_id=source_slice_id,
                target_slice_id=target_slice_id,
                source_data_count=source_data_count,
                target_data_count=target_data_count,
                diagnosis_data_count=diagnosis_data_count,
            ),
        )
        return Diagnosis.model_validate(response)

    def delete_diagnosis(
        self,
        dataset_id: str,
        diagnosis_id: str,
    ) -> bool:
        """diagnosis 삭제.

        Args:
            dataset_id (str): Dataset ID.
            diagnosis_id (str): Diagnosis ID.

        Raises:
            BadParameterError: dataset_id 또는 diagnosis_id 미제공 시.

        Returns:
            bool: 삭제 성공 여부.
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if diagnosis_id is None:
            raise BadParameterError("diagnosis_id is required.")

        response = self.request_gql(
            Queries.DELETE,
            Queries.DELETE["variables"](
                dataset_id=dataset_id,
                diagnosis_id=diagnosis_id,
            ),
        )
        return bool(response)

    def create_diagnosis_report_item(
        self,
        dataset_id: str,
        diagnosis_id: str,
        name: str,
        type: AnalyticsReportItemType,
        content_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Diagnosis:
        """diagnosis 리포트 아이템 생성.

        Args:
            dataset_id (str): Dataset ID.
            diagnosis_id (str): Diagnosis ID.
            name (str): 리포트 아이템 이름.
            type (AnalyticsReportItemType): 리포트 아이템 타입.
            content_id (Optional[str], optional): Content ID. Defaults to None.
            description (Optional[str], optional): 설명. Defaults to None.

        Returns:
            Diagnosis: 업데이트된 diagnosis (리포트 아이템 포함).
        """
        response = self.request_gql(
            Queries.CREATE_REPORT_ITEM,
            Queries.CREATE_REPORT_ITEM["variables"](
                dataset_id=dataset_id,
                diagnosis_id=diagnosis_id,
                name=name,
                type=type,
                content_id=content_id,
                description=description,
            ),
        )
        return Diagnosis.model_validate(response)

    def update_diagnosis_report_item(
        self,
        dataset_id: str,
        diagnosis_id: str,
        diagnosis_report_item_id: str,
        name: Union[Optional[str], UndefinedType] = Undefined,
        type: Union[Optional[AnalyticsReportItemType], UndefinedType] = Undefined,
        content_id: Union[Optional[str], UndefinedType] = Undefined,
        description: Union[Optional[str], UndefinedType] = Undefined,
    ) -> Diagnosis:
        """diagnosis 리포트 아이템 수정. 전달한 필드만 갱신.

        Args:
            dataset_id (str): Dataset ID.
            diagnosis_id (str): Diagnosis ID.
            diagnosis_report_item_id (str): 리포트 아이템 ID.
            name (Union[Optional[str], UndefinedType], optional): 이름. Defaults to Undefined.
            type (Union[Optional[AnalyticsReportItemType], UndefinedType], optional): 타입. Defaults to Undefined.
            content_id (Union[Optional[str], UndefinedType], optional): Content ID. Defaults to Undefined.
            description (Union[Optional[str], UndefinedType], optional): 설명. Defaults to Undefined.

        Returns:
            Diagnosis: 수정된 diagnosis.
        """
        response = self.request_gql(
            Queries.UPDATE_REPORT_ITEM,
            Queries.UPDATE_REPORT_ITEM["variables"](
                dataset_id=dataset_id,
                diagnosis_id=diagnosis_id,
                diagnosis_report_item_id=diagnosis_report_item_id,
                name=name,
                type=type,
                content_id=content_id,
                description=description,
            ),
        )
        return Diagnosis.model_validate(response)

    def delete_diagnosis_report_item(
        self,
        dataset_id: str,
        diagnosis_id: str,
        diagnosis_report_item_id: str,
    ) -> Diagnosis:
        """diagnosis 리포트 아이템 삭제.

        Args:
            dataset_id (str): Dataset ID.
            diagnosis_id (str): Diagnosis ID.
            diagnosis_report_item_id (str): 삭제할 리포트 아이템 ID.

        Raises:
            BadParameterError: 필수 인자 미제공 시.

        Returns:
            Diagnosis: 업데이트된 diagnosis (해당 리포트 아이템 제외).
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        if diagnosis_id is None:
            raise BadParameterError("diagnosis_id is required.")
        if diagnosis_report_item_id is None:
            raise BadParameterError("diagnosis_report_item_id is required.")

        response = self.request_gql(
            Queries.DELETE_REPORT_ITEM,
            Queries.DELETE_REPORT_ITEM["variables"](
                dataset_id=dataset_id,
                diagnosis_id=diagnosis_id,
                diagnosis_report_item_id=diagnosis_report_item_id,
            ),
        )
        return Diagnosis.model_validate(response)
    
    def upload_reports_json(
        self,
        content_id: str,
        chart_data: ChartDataResult,
    ) -> bool:
        """Upload reports.json to S3 for the given content ID.
        
        Args:
            content_id (str): The folder content ID where reports.json will be uploaded
            chart_data (ChartDataResult): Chart data result from ChartDataFactory
        
        Returns:
            bool: True if upload was successful
        """
        return self._upload_json_file(content_id, "reports.json", chart_data.reports_json)
    
    def upload_data_ids_json(
        self,
        content_id: str,
        chart_data: ChartDataResult,
    ) -> bool:
        """Upload data_ids.json to S3 for the given content ID.
        
        Args:
            content_id (str): The folder content ID where data_ids.json will be uploaded
            chart_data (ChartDataResult): Chart data result from ChartDataFactory
        
        Returns:
            bool: True if upload was successful
        
        Raises:
            BadParameterError: If chart_data has no data_ids_json
        """
        if not chart_data.data_ids_json:
            raise BadParameterError("chart_data has no data_ids_json to upload")
        return self._upload_json_file(content_id, "data_ids.json", chart_data.data_ids_json)
    
    def _upload_json_file(
        self,
        content_id: str,
        filename: str,
        json_data: dict,
    ) -> bool:
        """Upload a JSON file to S3 for the given content ID.
        
        Args:
            content_id (str): The folder content ID
            filename (str): The filename (e.g., "reports.json", "data_ids.json")
            json_data (dict): The JSON data to upload
        
        Returns:
            bool: True if upload was successful
        """
        import json
        
        content_service = ContentService()
        
        # Create a content entry for the JSON file
        file_content, upload_url = content_service.create_content(
            key=f"{content_id}/{filename}",
            content_type="application/json"
        )
        
        # Upload JSON data to S3
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
        
        import requests
        response = requests.put(
            upload_url,
            data=json_str.encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to upload {filename}: {response.status_code} {response.text}")
        
        return True
