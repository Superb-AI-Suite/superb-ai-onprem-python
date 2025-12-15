from typing import Optional, Union, Any
from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import BadParameterError
from spb_onprem.base_types import Undefined, UndefinedType
from spb_onprem.contents.service import ContentService
from .queries import Queries
from .entities import (
    AnalyticsReport,
    AnalyticsReportItem,
    AnalyticsReportItemType,
    AnalyticsReportPageInfo,
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
        meta: Union[Any, UndefinedType] = Undefined,
    ):
        """
        Update an analytics report.

        Args:
            dataset_id (str): The dataset ID
            report_id (str): The ID of the report to update
            title (Optional[str]): The new title of the report
            description (Optional[str]): The new description of the report
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
                meta=meta,
            ),
        )
        return AnalyticsReport.model_validate(response)
    
    def delete_analytics_report(
        self,
        dataset_id: str,
        report_id: str,
    ) -> bool:
        """Delete an analytics report.
        
        Args:
            dataset_id (str): The dataset ID
            report_id (str): The ID of the report to delete
        
        Returns:
            bool: True if deletion was successful
        """
        if dataset_id is None:
            raise BadParameterError("dataset_id is required.")
        
        if report_id is None:
            raise BadParameterError("report_id is required.")

        response = self.request_gql(
            Queries.DELETE_ANALYTICS_REPORT,
            Queries.DELETE_ANALYTICS_REPORT["variables"](
                dataset_id=dataset_id,
                report_id=report_id
            )
        )
        return response
    
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
    
    def upload_reports_json(
        self,
        content_id: str,
        data: dict,
    ) -> bool:
        """Upload reports.json to S3 for the given content ID.
        
        Args:
            content_id (str): The folder content ID where reports.json will be uploaded
            data (dict): The reports data to be uploaded as JSON
        
        Returns:
            bool: True if upload was successful
        """
        if content_id is None:
            raise BadParameterError("content_id is required.")
        
        if data is None:
            raise BadParameterError("data is required.")
        
        # Get upload URL using ContentService
        content_service = ContentService()
        upload_url = content_service.get_upload_url(
            content_id=content_id,
            file_name="reports.json",
            content_type="application/json"
        )
        
        # Upload the JSON data
        self.request(
            method="PUT",
            url=upload_url,
            headers={
                'Content-Type': 'application/json'
            },
            json_data=data,
        )
        
        return True
    
    def upload_data_ids_json(
        self,
        content_id: str,
        data: dict,
    ) -> bool:
        """Upload data_ids.json to S3 for the given content ID.
        
        Args:
            content_id (str): The folder content ID where data_ids.json will be uploaded
            data (dict): The data IDs to be uploaded as JSON
        
        Returns:
            bool: True if upload was successful
        """
        if content_id is None:
            raise BadParameterError("content_id is required.")
        
        if data is None:
            raise BadParameterError("data is required.")
        
        # Get upload URL using ContentService
        content_service = ContentService()
        upload_url = content_service.get_upload_url(
            content_id=content_id,
            file_name="data_ids.json",
            content_type="application/json"
        )
        
        # Upload the JSON data
        self.request(
            method="PUT",
            url=upload_url,
            headers={
                'Content-Type': 'application/json'
            },
            json_data=data,
        )
        
        return True
