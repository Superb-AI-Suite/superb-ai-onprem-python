from typing import Any, List, Optional, Union
from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import BadParameterError
from spb_onprem.activities.deletion import (
    DeletionActivityType,
    deletion_filter,
    require_id,
    start_deletion_activity,
    warn_deprecated,
)
from spb_onprem.activities.entities import ActivityHistory
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.contents.service import ContentService
from spb_onprem.charts import ChartDataResult
from .queries import Queries
from .entities import (
    AnalyticsReport,
    AnalyticsReportItem,
    AnalyticsReportItemType,
    AnalyticsReportPageInfo,
    AnalyticsReportStatus,
)
from .params.analytics_reports import AnalyticsReportsFilter, AnalyticsReportsOrderBy


class ReportService(BaseService):
    """
    Service class for handling analytics report-related operations.
    """
    
    def get_analytics_reports(
        self,
        dataset_id: str,
        analytics_reports_filter: Optional[AnalyticsReportsFilter] = None,
        cursor: Optional[str] = None,
        length: Optional[int] = 10,
        order_by: Union[AnalyticsReportsOrderBy, UndefinedType] = Undefined,
    ):
        """
        Get a list of analytics reports based on the provided filter and pagination parameters.
        
        Args:
            dataset_id (str): The dataset ID
            analytics_reports_filter (Optional[AnalyticsReportsFilter]): Filter criteria for reports
            cursor (Optional[str]): Cursor for pagination
            length (Optional[int]): Number of items per page (default: 10)
            order_by (Optional[AnalyticsReportsOrderBy]): Order by options
        
        Returns:
            tuple: A tuple containing:
                - List[AnalyticsReport]: A list of AnalyticsReport objects
                - str: Next cursor for pagination
                - int: Total count of reports
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        
        if length and length > 50:
            raise BadParameterError("The maximum length is 50.")
        
        response = self.request_gql(
            Queries.ANALYTICS_REPORTS,
            Queries.ANALYTICS_REPORTS["variables"](
                dataset_id=dataset_id,
                analytics_reports_filter=analytics_reports_filter,
                cursor=cursor,
                length=length,
                order_by=order_by,
            )
        )
        
        page_info = AnalyticsReportPageInfo.model_validate(response)
        return (
            page_info.analytics_reports or [],
            page_info.next,
            page_info.total_count or 0
        )

    def get_analytics_report(
        self,
        dataset_id: str,
        report_id: str,
    ):
        """
        Retrieve an analytics report by its ID.

        Args:
            dataset_id (str): The dataset ID
            report_id (str): The ID of the report to retrieve

        Returns:
            AnalyticsReport: The retrieved analytics report object
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        
        if report_id is None:
            raise BadParameterError("report_id is required.")
        
        response = self.request_gql(
            Queries.ANALYTICS_REPORT,
            Queries.ANALYTICS_REPORT["variables"](
                dataset_id=dataset_id,
                report_id=report_id
            ),
        )
        return AnalyticsReport.model_validate(response)
    
    def create_analytics_report(
        self,
        dataset_id: str,
        title: Union[str, UndefinedType] = Undefined,
        description: Union[str, UndefinedType] = Undefined,
        meta: Union[Any, UndefinedType] = Undefined,
    ):
        """
        Create a new analytics report.

        Args:
            dataset_id (str): The dataset ID
            title (Optional[str]): The title of the report
            description (Optional[str]): The description of the report
            meta (Optional[Any]): The metadata of the report

        Returns:
            AnalyticsReport: The created analytics report object
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        
        response = self.request_gql(
            Queries.CREATE_ANALYTICS_REPORT,
            Queries.CREATE_ANALYTICS_REPORT["variables"](
                dataset_id=dataset_id,
                title=title,
                description=description,
                meta=meta,
            ),
        )
        return AnalyticsReport.model_validate(response)
    
    def update_analytics_report(
        self,
        dataset_id: str,
        report_id: str,
        title: Union[str, UndefinedType] = Undefined,
        description: Union[str, UndefinedType] = Undefined,
        status: Union[Optional[AnalyticsReportStatus], UndefinedType] = Undefined,
        meta: Union[Any, UndefinedType] = Undefined,
    ):
        """
        Update an analytics report.

        Args:
            dataset_id (str): The dataset ID
            report_id (str): The ID of the report to update
            title (Optional[str]): The new title of the report
            description (Optional[str]): The new description of the report
            status (Optional[str]): The new status of the report (PENDING/IN_PROGRESS/COMPLETED/FAILED)
            meta (Optional[Any]): The new metadata of the report

        Returns:
            AnalyticsReport: The updated analytics report object
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        
        if report_id is None:
            raise BadParameterError("report_id is required.")
        
        response = self.request_gql(
            Queries.UPDATE_ANALYTICS_REPORT,
            Queries.UPDATE_ANALYTICS_REPORT["variables"](
                dataset_id=dataset_id,
                report_id=report_id,
                title=title,
                description=description,
                status=status,
                meta=meta,
            ),
        )
        return AnalyticsReport.model_validate(response)
    
    def delete_analytics_reports(
        self,
        dataset_id: str,
        report_ids: Optional[List[str]] = None,
        report_filter: Optional[Union[AnalyticsReportsFilter, dict]] = None,
    ) -> ActivityHistory:
        """Start deleting analytics reports.

        Starts one ``DELETE_ANALYTICS_REPORT`` activity for every analytics
        report that ``report_ids`` or ``report_filter`` selects (pass exactly
        one). The activity deletes each report, its items and their files.
        Selecting by ID needs a server whose analytics report filter has
        ``idIn``. To block until it ends, use
        ``ActivityService.wait_for_activity``.
        Targets are found when the activity runs. If none match or they are
        already deleted, it succeeds without deleting anything. A target that
        cannot be deleted then (still being made) is not refused at request time; the
        activity ends FAILED (see its ``status`` and ``meta``).
        A caller who is not an admin of the dataset (Owner, WorkspaceAdmin or
        DATASET-ADMIN) submits it as AWAITING_APPROVAL.

        Args:
            dataset_id (str): The dataset ID.
            report_ids (Optional[List[str]]): The analytics report IDs.
            report_filter (Optional[AnalyticsReportsFilter | dict]): An AnalyticsReportsFilter
                (``{"must": ..., "not": ...}``). A dict is sent as it is, in
                the GraphQL field names. A filter without a condition is refused.
                A filter with only ``not`` selects every target except those.

        Raises:
            BadParameterError: If dataset_id is missing.
            BadDeletionTargetError: If none or both of report_ids and
                report_filter are given, or they are empty (also a
                ValueError).
            InvalidInputError: If the platform refuses the request. It checks
                only keys, types and required values then; other filter
                problems (e.g. an empty ``idIn``) are checked when the activity
                runs and would fail it, so the SDK refuses those before sending
                (BadDeletionTargetError).
            UnknownError: Other request errors (e.g. no role in the dataset).

        Returns:
            ActivityHistory: The started activity.
        """
        require_id(dataset_id, "dataset_id")
        parameters = {
            "dataset_id": dataset_id,
            "analytics_report_filter": deletion_filter(
                ids=report_ids,
                ids_name="report_ids",
                filter=report_filter,
                filter_name="report_filter",
                filter_types=(AnalyticsReportsFilter,),
                status_values=[status.value for status in AnalyticsReportStatus],
            ),
        }
        return start_deletion_activity(
            self, dataset_id, DeletionActivityType.DELETE_ANALYTICS_REPORT, parameters
        )

    def delete_analytics_report(
        self,
        dataset_id: str,
        report_id: str,
    ) -> ActivityHistory:
        """Start deleting one analytics report. Deprecated: use ``delete_analytics_reports``.

        It will be removed in the next major version. It warns with
        DeprecationWarning and calls ``delete_analytics_reports(dataset_id, report_ids=[report_id])``,
        so it starts one activity with the filter ``{"must": {"idIn": [report_id]}}``.
        Calling it in a loop starts one activity per analytics report; pass all the IDs to
        ``delete_analytics_reports`` instead.

        Raises:
            BadParameterError: If dataset_id or report_id is missing.

        Returns:
            ActivityHistory: The started activity.
        """
        warn_deprecated(
            "delete_analytics_report", "delete_analytics_reports", "analytics report", "report_ids", "report_filter"
        )
        require_id(dataset_id, "dataset_id")
        require_id(report_id, "report_id")
        return self.delete_analytics_reports(dataset_id, report_ids=[report_id])
    
    def create_analytics_report_item(
        self,
        dataset_id: str,
        report_id: str,
        type: AnalyticsReportItemType,
        title: Union[str, UndefinedType] = Undefined,
        description: Union[str, UndefinedType] = Undefined,
        content_id: Union[str, UndefinedType] = Undefined,
        meta: Union[Any, UndefinedType] = Undefined,
    ):
        """
        Create a new analytics report item.

        Args:
            dataset_id (str): The dataset ID
            report_id (str): The report ID
            type (AnalyticsReportItemType): The type of report item
            title (Optional[str]): The title of the item
            description (Optional[str]): The description of the item
            content_id (Optional[str]): The content ID of the item
            meta (Optional[Any]): The metadata of the item

        Returns:
            AnalyticsReportItem: The created analytics report item object
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        
        if report_id is None:
            raise BadParameterError("report_id is required.")
        
        if type is None:
            raise BadParameterError("type is required.")
        
        response = self.request_gql(
            Queries.CREATE_ANALYTICS_REPORT_ITEM,
            Queries.CREATE_ANALYTICS_REPORT_ITEM["variables"](
                dataset_id=dataset_id,
                report_id=report_id,
                type=type,
                title=title,
                description=description,
                content_id=content_id,
                meta=meta,
            ),
        )
        return AnalyticsReportItem.model_validate(response)
    
    def update_analytics_report_item(
        self,
        dataset_id: str,
        report_id: str,
        item_id: str,
        title: Union[str, UndefinedType] = Undefined,
        description: Union[str, UndefinedType] = Undefined,
        content_id: Union[str, UndefinedType] = Undefined,
        meta: Union[Any, UndefinedType] = Undefined,
    ):
        """
        Update an analytics report item.

        Args:
            dataset_id (str): The dataset ID
            report_id (str): The report ID
            item_id (str): The ID of the item to update
            title (Optional[str]): The new title of the item
            description (Optional[str]): The new description of the item
            content_id (Optional[str]): The new content ID of the item
            meta (Optional[Any]): The new metadata of the item

        Returns:
            AnalyticsReportItem: The updated analytics report item object
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        
        if report_id is None:
            raise BadParameterError("report_id is required.")
        
        if item_id is None:
            raise BadParameterError("item_id is required.")
        
        response = self.request_gql(
            Queries.UPDATE_ANALYTICS_REPORT_ITEM,
            Queries.UPDATE_ANALYTICS_REPORT_ITEM["variables"](
                dataset_id=dataset_id,
                report_id=report_id,
                item_id=item_id,
                title=title,
                description=description,
                content_id=content_id,
                meta=meta,
            ),
        )
        return AnalyticsReportItem.model_validate(response)
    
    def delete_analytics_report_item(
        self,
        dataset_id: str,
        report_id: str,
        item_id: str,
    ) -> bool:
        """Delete an analytics report item.
        
        Args:
            dataset_id (str): The dataset ID
            report_id (str): The report ID
            item_id (str): The ID of the item to delete
        
        Returns:
            bool: True if deletion was successful
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        
        if report_id is None:
            raise BadParameterError("report_id is required.")
        
        if item_id is None:
            raise BadParameterError("item_id is required.")

        response = self.request_gql(
            Queries.DELETE_ANALYTICS_REPORT_ITEM,
            Queries.DELETE_ANALYTICS_REPORT_ITEM["variables"](
                dataset_id=dataset_id,
                report_id=report_id,
                item_id=item_id,
            )
        )
        return response
    
    def _upload_json_file(
        self,
        content_id: str,
        file_name: str,
        data: dict,
    ) -> bool:
        """Upload a JSON file to S3 for the given content ID.
        
        Args:
            content_id (str): The folder content ID
            file_name (str): The name of the file to upload
            data (dict): The data to be uploaded as JSON
        
        Returns:
            bool: True if upload was successful
        """
        if content_id is None:
            raise BadParameterError("content_id is required.")
        
        if data is None:
            raise BadParameterError("data is required.")
        
        # Get upload URL
        content_service = ContentService()
        upload_url = content_service.get_upload_url(
            content_id=content_id,
            file_name=file_name,
            content_type="application/json"
        )
        
        # Upload the JSON data
        self.request(
            method="PUT",
            auth=False,  # presigned storage URL: no platform credentials
            url=upload_url,
            headers={'Content-Type': 'application/json'},
            json_data=data,
        )
        
        return True
    
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
        if chart_data.data_ids_json is None:
            raise BadParameterError("chart_data does not contain data_ids_json")
        
        return self._upload_json_file(content_id, "data_ids.json", chart_data.data_ids_json)
