import logging
from typing import List, Optional, Union

from spb_onprem.base_service import BaseService
from spb_onprem.base_types import (
    Undefined,
    UndefinedType,
)

from .entities import (
    Slice
)
from .params import (
    SlicesFilter
)
from .queries import (
    Queries,
)
from spb_onprem.activities.deletion import (
    DeletionActivityType,
    deletion_filter,
    require_id,
    start_deletion_activity,
    warn_deprecated,
)
from spb_onprem.activities.entities import ActivityHistory

logger = logging.getLogger(__name__)


class SliceService(BaseService):
    """Service class for handling slice-related operations."""
    
    def create_slice(
        self,
        dataset_id: str,
        name: str,
        description: Union[
            UndefinedType,
            str
        ] = Undefined,
    ):
        """Create a slice.
        
        Args:
            dataset_id (str): The ID of the dataset to create the slice for.
            name (str): The name of the slice to create.
            description (Optional[str]): The description of the slice to create.
        
        Returns:
            Slice: The created slice object.
        """
        variables = Queries.CREATE_SLICE["variables"](
            dataset_id=dataset_id,
            slice_name=name,
            slice_description=description
        )
        logger.debug("create_slice variables: %s", variables)

        response = self.request_gql(
            Queries.CREATE_SLICE,
            variables
        )
        # response는 이미 createSlice 객체 자체 (request_gql이 data.createSlice를 추출함)
        logger.debug("create_slice response: %s", response)
        return Slice.model_validate(response)

    def get_slices(
        self,
        dataset_id: str,
        slice_filter: Optional[SlicesFilter] = None,
        cursor: Optional[str] = None,
        length: int = 10
    ):
        """Get slices of a dataset.
        
        Args:
            dataset_id (str): The ID of the dataset to get the slices for.
            slice_filter (Optional[SlicesFilter]): The filter to apply to the slices.
            cursor (Optional[str]): The cursor to use for pagination.
            length (int): The number of slices to get.
        
        Returns:
            tuple: A tuple containing the slices, the next cursor, and the total count of slices.
        """
        if length > 50:
            raise ValueError("Length must be less than or equal to 50.")

        response = self.request_gql(
            Queries.GET_SLICES,
            Queries.GET_SLICES["variables"](
                dataset_id=dataset_id,
                slices_filter=slice_filter,
                cursor=cursor,
                length=length
            )
        )
        slices_dict = response.get("slices", [])
        slices = [Slice.model_validate(slice_dict) for slice_dict in slices_dict]
        return (
            slices,
            response.get("next", None),
            response.get("totalCount", 0)
        )

    def get_slice(
        self,
        dataset_id: str,
        slice_id: Optional[str] = None,
    ):
        """Get a slice by ID.
        
        Args:
            dataset_id (str): The ID of the dataset to get the slice for.
            slice_id (Optional[str]): The ID of the slice to get.
        
        Returns:
            Slice: The slice object.
        """
        response = self.request_gql(
            Queries.GET_SLICE,
            Queries.GET_SLICE["variables"](
                dataset_id=dataset_id,
                slice_id=slice_id
            )
        )
        # slice_dict = response.get("slice", {})
        return Slice.model_validate(response)
    
    def get_slice_by_name(
        self,
        dataset_id: str,
        name: str,
    ):
        """Get a slice by name.
        
        Args:
            dataset_id (str): The ID of the dataset to get the slice for.
            name (str): The name of the slice to get.
        
        Returns:
            Slice: The slice object.
        """
        response = self.request_gql(
            Queries.GET_SLICE,
            Queries.GET_SLICE["variables"](
                dataset_id=dataset_id,
                name=name
            )
        )
        return Slice.model_validate(response)

    def update_slice(
        self,
        dataset_id: str,
        slice_id: str,
        name: Union[
            UndefinedType,
            str
        ] = Undefined,
        description: Union[
            UndefinedType,
            str
        ] = Undefined,
    ):
        """Update a slice.
        
        Args:
            dataset_id (str): The ID of the dataset to update the slice for.
            slice_id (str): The ID of the slice to update.
            name (Optional[str]): The name of the slice to update.
            description (Optional[str]): The description of the slice to update.
        
        Returns:
            Slice: The updated slice object.
        """
        response = self.request_gql(
            Queries.UPDATE_SLICE,
            Queries.UPDATE_SLICE["variables"](
                dataset_id=dataset_id,
                slice_id=slice_id,
                slice_name=name,
                slice_description=description
            )
        )
        slice_dict = response.get("updateSlice", {})
        return Slice.model_validate(slice_dict)

    def delete_slices(
        self,
        dataset_id: str,
        slice_ids: Optional[List[str]] = None,
        slice_filter: Optional[Union[SlicesFilter, dict]] = None,
    ) -> ActivityHistory:
        """Start deleting slices.

        Starts one ``DELETE_SLICE`` activity for every slice that ``slice_ids``
        or ``slice_filter`` selects (pass exactly one). The activity deletes
        each slice's annotation files, then the slice; the data stay in the
        dataset. To block until it ends, use
        ``ActivityService.wait_for_activity``.
        Targets are found when the activity runs. If none match or they are
        already deleted, it succeeds without deleting anything. A target that
        cannot be deleted then (for example a storage error) is not refused at request time; the
        activity ends FAILED (see its ``status`` and ``meta``).
        A caller who is not an admin of the dataset (Owner, WorkspaceAdmin or
        DATASET-ADMIN) submits it as AWAITING_APPROVAL.

        Args:
            dataset_id (str): The dataset ID.
            slice_ids (Optional[List[str]]): The slice IDs.
            slice_filter (Optional[SlicesFilter | dict]): A SlicesFilter
                (``{"must": ..., "not": ...}``). A dict is sent as it is, in
                the GraphQL field names. A filter without a condition is refused.
                A filter with only ``not`` selects every target except those.

        Raises:
            BadParameterError: If dataset_id is missing.
            BadDeletionTargetError: If none or both of slice_ids and
                slice_filter are given, or they are empty (also a
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
            "slice_filter": deletion_filter(
                ids=slice_ids,
                ids_name="slice_ids",
                filter=slice_filter,
                filter_name="slice_filter",
                filter_types=(SlicesFilter,),
            ),
        }
        return start_deletion_activity(
            self, dataset_id, DeletionActivityType.DELETE_SLICE, parameters
        )

    def delete_slice(
        self,
        dataset_id: str,
        slice_id: str,
    ) -> ActivityHistory:
        """Start deleting one slice. Deprecated: use ``delete_slices``.

        It will be removed in the next major version. It warns with
        DeprecationWarning and calls ``delete_slices(dataset_id, slice_ids=[slice_id])``,
        so it starts one activity with the filter ``{"must": {"idIn": [slice_id]}}``.
        Calling it in a loop starts one activity per slice; pass all the IDs to
        ``delete_slices`` instead.

        Raises:
            BadParameterError: If dataset_id or slice_id is missing.

        Returns:
            ActivityHistory: The started activity.
        """
        warn_deprecated("delete_slice", "delete_slices", "slice", "slice_ids", "slice_filter")
        require_id(dataset_id, "dataset_id")
        require_id(slice_id, "slice_id")
        return self.delete_slices(dataset_id, slice_ids=[slice_id])
