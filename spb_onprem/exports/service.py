from typing import Optional, List, Union, Tuple

from spb_onprem.base_service import BaseService
from spb_onprem.base_types import (
    Undefined,
    UndefinedType,
)
from spb_onprem.data.params import DataListFilter

from .entities import Export
from .params import (
    ExportFilter,
)
from .queries import Queries


class ExportService(BaseService):
    """Service class for handling export-related operations."""
    
    def create_export(
        self,
        dataset_id: str,
        name: Union[
            UndefinedType,
            str
        ] = Undefined,
        data_filter: Union[
            UndefinedType,
            DataListFilter,
            dict
        ] = Undefined,
        location: Union[
            UndefinedType,
            str
        ] = Undefined,
        data_count: Union[
            UndefinedType,
            int
        ] = Undefined,
        frame_count: Union[
            UndefinedType,
            int
        ] = Undefined,
        annotation_count: Union[
            UndefinedType,
            int
        ] = Undefined,
        meta: Union[
            UndefinedType,
            dict
        ] = Undefined,
    ) -> Export:
        """Create an export.
        
        Args:
            dataset_id (str): The ID of the dataset to create the export for.
            name (Optional[str]): The name of the export.
            data_filter (Optional[DataListFilter | dict]): The search filter of the data.
            data_count (Optional[int]): The number of data items to export.
            frame_count (Optional[int]): The number of frames to export.
            annotation_count (Optional[int]): The number of annotations to export.
            meta (Optional[dict]): The meta information for the export.
        """
        response = self.request_gql(
            Queries.CREATE_EXPORT,
            Queries.CREATE_EXPORT["variables"](
                dataset_id=dataset_id,
                name=name,
                data_filter=data_filter,
                location=location,
                data_count=data_count,
                frame_count=frame_count,
                annotation_count=annotation_count,
                meta=meta,
            )
        )
        return Export.model_validate(response)
    
    def get_exports(
        self,
        dataset_id: str,
        export_filter: Optional[ExportFilter] = None,
        cursor: Optional[str] = None,
        length: int = 10
    ) -> Tuple[List[Export], Optional[str], int]:
        """Get exports.
        
        Args:
            dataset_id (str): The ID of the dataset to get exports for.
            export_filter (Optional[ExportsFilterOptions]): The filter to apply to the exports.
            cursor (Optional[str]): The cursor to use for pagination.
            length (int): The number of exports to get.
        
        Returns:
            Tuple[List[Export], Optional[str], int]: A tuple containing the exports, the next cursor, and the total count of exports.
        """
        response = self.request_gql(
            Queries.GET_EXPORTS,
            Queries.GET_EXPORTS["variables"](
                dataset_id=dataset_id,
                export_filter=export_filter,
                cursor=cursor,
                length=length,
            )
        )
        exports_dict = response.get("exports", [])
        return (
            [Export.model_validate(export_dict) for export_dict in exports_dict],
            response.get("next"),
            response.get("totalCount"),
        )

    def get_export(
        self,
        dataset_id: str,
        export_id: str,
    ) -> Export:
        """Get an export.
        
        Args:
            dataset_id (str): The ID of the dataset to get the export for.
            export_id (str): The ID of the export to get.
        
        Returns:
            Export: The export object.
        """
        response = self.request_gql(
            Queries.GET_EXPORT,
            Queries.GET_EXPORT["variables"](
                dataset_id=dataset_id,
                export_id=export_id,
            )
        )
        return Export.model_validate(response)

    def update_export(
        self,
        dataset_id: str,
        export_id: str,
        location: Union[
            UndefinedType,
            str
        ] = Undefined,
        name: Union[
            UndefinedType,
            str
        ] = Undefined,
        data_filter: Union[
            UndefinedType,
            DataListFilter,
            dict
        ] = Undefined,
        data_count: Union[
            UndefinedType,
            int
        ] = Undefined,
        frame_count: Union[
            UndefinedType,
            int
        ] = Undefined,
        annotation_count: Union[
            UndefinedType,
            int
        ] = Undefined,
        meta: Union[
            UndefinedType,
            dict
        ] = Undefined,
        completed_at: Union[
            UndefinedType,
            str
        ] = Undefined,
    ) -> Export:
        """Update an export.
        
        Args:
            dataset_id (str): The ID of the dataset to update the export for.
            export_id (str): The ID of the export to update.
            location (Optional[str]): The location where the export will be stored.
            name (Optional[str]): The name of the export.
            data_filter (Optional[DataListFilter | dict]): The search filter of the data.
            data_count (Optional[int]): The number of data items to export.
            frame_count (Optional[int]): The number of frames to export.
            annotation_count (Optional[int]): The number of annotations to export.
            meta (Optional[dict]): The meta information for the export.
            completed_at (Optional[str]): The completed time of the export.
        
        Returns:
            Export: The updated export object.
        """
        response = self.request_gql(
            Queries.UPDATE_EXPORT,
            Queries.UPDATE_EXPORT["variables"](
                dataset_id=dataset_id,
                export_id=export_id,
                location=location,
                name=name,
                data_filter=data_filter,
                data_count=data_count,
                frame_count=frame_count,
                annotation_count=annotation_count,
                meta=meta,
                completed_at=completed_at,
            )
        )
        return Export.model_validate(response)

    def delete_export(
        self,
        dataset_id: str,
        export_id: str,
    ) -> bool:
        """Delete an export.
        
        Args:
            dataset_id (str): The ID of the dataset to delete the export for.
            export_id (str): The ID of the export to delete.
        
        Returns:
            bool: True if the export was deleted, False otherwise.
        """
        response = self.request_gql(
            Queries.DELETE_EXPORT,
            Queries.DELETE_EXPORT["variables"](
                dataset_id=dataset_id,
                export_id=export_id,
            )
        )
        return response
