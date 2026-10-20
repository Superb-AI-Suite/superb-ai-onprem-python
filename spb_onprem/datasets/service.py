from typing import Optional, Union
from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import BadParameterError
from spb_onprem.activities.deletion import (
    DeletionActivityType,
    require_id,
    start_deletion_activity,
)
from spb_onprem.activities.entities import ActivityHistory
from spb_onprem.base_types import Undefined, UndefinedType
from .queries import Queries
from .entities import Dataset
from .params.datasets import DatasetsFilter
from .enums import DatasetType


class DatasetService(BaseService):
    """
    Service class for handling dataset-related operations.
    """
    
    def get_datasets(
        self,
        datasets_filter: Optional[DatasetsFilter] = None,
        cursor: Optional[str] = None,
        length: Optional[int] = 10
    ):
        """
        Get a list of datasets based on the provided filter and pagination parameters.
        
        Args:
            datasets_filter (Union[DatasetsFilter, UndefinedType]): Filter criteria for datasets
            cursor (Optional[str]): Cursor for pagination
            length (Optional[int]): Number of items per page (default: 10)
        
        Returns:
            List[Dataset]: A list of Dataset objects
        """
        if length > 50:
            raise BadParameterError("The maximum length is 50.")
        
        response = self.request_gql(
            Queries.DATASETS,
            Queries.DATASETS["variables"](
                datasets_filter=datasets_filter,
                cursor=cursor,
                length=length
            )
        )
        datasets = [Dataset.model_validate(dataset) for dataset in response["datasets"]]
        return (
            datasets,
            response.get("next", None),
            response.get("totalCount", 0)
        )

    def get_dataset(
        self,
        dataset_id: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """
        Retrieve a dataset by its ID or name.

        Args:
            dataset_id (Optional[str]): The ID of the dataset to retrieve.
            name (Optional[str]): The name of the dataset to retrieve.

        Returns:
            Dataset: The retrieved dataset object.
        """
        response = self.request_gql(
            Queries.DATASET,
            Queries.DATASET["variables"](
                dataset_id=dataset_id,
                name=name
            ),
        )
        return Dataset.model_validate(response)
    
    def create_dataset(
        self,
        name: str,
        description: Union[
            str,
            UndefinedType,
        ] = Undefined,
        type: Union[
            Optional[DatasetType],
            UndefinedType,
        ] = Undefined,
    ):
        """
        Create a new dataset.

        Args:
            name (str): The name of the dataset to create.
            description (Optional[str]): The description of the dataset to create.
            type (Optional[DatasetType]): The dataset type. Pass DatasetType.VLM
                for a VLM dataset; omit it (or pass None) for a Computer Vision
                dataset. It cannot be changed after creation.

        Returns:
            Dataset: The created dataset object.
        """
        response = self.request_gql(
            Queries.CREATE_DATASET,
            Queries.CREATE_DATASET["variables"](
                name=name,
                description=description,
                type=type,
            ),
        )
        return Dataset.model_validate(response)

    def update_dataset(
        self,
        dataset_id: str,
        name: Union[
            str,
            UndefinedType,
        ] = Undefined,
        description: Union[
            str,
            UndefinedType,
        ] = Undefined,
    ):
        """
        Update a dataset.

        Args:
            dataset_id (str): The ID of the dataset to update.
            name (Optional[str]): The name of the dataset to update.
            description (Optional[str]): The description of the dataset to update.

        Returns:
            Dataset: The updated dataset object.
        """
        response = self.request_gql(
            Queries.UPDATE_DATASET,
            Queries.UPDATE_DATASET["variables"](
                dataset_id=dataset_id,
                name=name,
                description=description,
            ),
        )
        return Dataset.model_validate(response)
    
    def delete_dataset(self, dataset_id: str) -> ActivityHistory:
        """Start deleting the dataset.

        Since 2.0.0 this starts a ``DELETE_DATASET`` activity instead of
        deleting the dataset at once. The activity deletes, with their files,
        the dataset's model deployments and diagnoses, then its models,
        analytics reports, slices and data, and then the dataset. A deployment
        does not block it; it is deleted first. The server refuses the request
        while a training, diagnosis or analytics report of the dataset is still
        running. To block until the activity ends, use
        ``ActivityService.wait_for_activity``.
        A caller who is not an admin of the dataset (Owner, WorkspaceAdmin or
        DATASET-ADMIN) submits it as AWAITING_APPROVAL.

        Args:
            dataset_id (str): The ID of the dataset to delete.

        Raises:
            BadParameterError: If dataset_id is missing.

        Returns:
            ActivityHistory: The started activity.
        """
        require_id(dataset_id, "dataset_id")
        return start_deletion_activity(
            self, dataset_id, DeletionActivityType.DELETE_DATASET, {"dataset_id": dataset_id}
        )
