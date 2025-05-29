from typing import Optional, Union
from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import BadParameterError
from spb_onprem.base_types import Undefined, UndefinedType
from .queries import Queries
from .entities import Dataset
from .params.datasets import DatasetsFilter


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
            response.get("totalCount", False)
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
    ):
        """
        Create a new dataset.

        Args:
            name (str): The name of the dataset to create.
            description (Optional[str]): The description of the dataset to create.

        Returns:
            Dataset: The created dataset object.
        """
        response = self.request_gql(
            Queries.CREATE_DATASET,
            Queries.CREATE_DATASET["variables"](
                name=name,
                description=description,
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
