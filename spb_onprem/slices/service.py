from typing import Optional, Union

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
        response = self.request_gql(
            Queries.CREATE_SLICE,
            Queries.CREATE_SLICE["variables"](
                dataset_id=dataset_id,
                slice_name=name,
                slice_description=description
            )
        )
        slice_dict = response.get("createSlice", {})
        return Slice.model_validate(slice_dict)

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
            response.get("totalCount", False)
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
        slice_dict = response.get("slice", {})
        return Slice.model_validate(slice_dict)
    
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
        slice_dict = response.get("slice", {})
        return Slice.model_validate(slice_dict)

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

    def delete_slice(
        self,
        dataset_id: str,
        slice_id: str,
    ) -> bool:
        """Delete a slice.
        
        Args:
            dataset_id (str): The ID of the dataset the slice belongs to.
            slice_id (str): The ID of the slice to delete.
        
        Returns:
            bool: True if the slice was deleted, False otherwise.
        """
        response = self.request_gql(
            Queries.DELETE_SLICE,
            Queries.DELETE_SLICE["variables"](
                dataset_id=dataset_id,
                slice_id=slice_id,
            )
        )
        return response
