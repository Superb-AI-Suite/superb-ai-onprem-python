from typing import Optional, Union
from sdk.base_service import BaseService
from sdk.base_types import Undefined, UndefinedType
from .queries import Queries
from .entities import Dataset


class DatasetService(BaseService):
    """
    Service class for handling dataset-related operations.
    """

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
