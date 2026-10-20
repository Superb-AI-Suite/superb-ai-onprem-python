"""VLM settings (question set) of a VLM dataset or slice (FDE-103)."""
from typing import Optional

from spb_onprem.base_service import BaseService

from .entities import DatasetVLMSettings, SliceVLMSettings, VLMSettings
from .queries import Queries


class VLMSettingsService(BaseService):
    """Read and write the question set of a VLM dataset or slice.

    The same calls the web app makes (``datasetVLMSettings``,
    ``createDatasetVLMSettings``, ... and the slice versions).

    - Only a VLM dataset (``DatasetType.VLM``) and its slices can have one.
    - A slice's question set is never copied from the dataset by the platform;
      create it with the settings you read from the dataset or another slice.
    - ``settings`` is a ``VLMSettings`` (build it like a filter, or read it with
      ``get_*`` and change it with its helpers). For a dict use
      ``VLMSettings.model_validate(data)``. It is checked before sending
      (``VLMSettingsValidationError``); a read set is also checked against what
      was read (``VLMSettingsChangeError``).
    - Updates and deletes take ``expected_updated_at``: the ``version`` of the
      record you read. When someone else saved in between, the platform refuses
      with ``ConflictError``; read again and retry. Leaving it out skips the check.

    Errors from the platform:
        InvalidInputError: Not a VLM dataset, invalid settings (sizes included),
            or an update that changes an existing question or evidence class
            instead of adding, deleting or restoring.
        ConflictError: Settings already exist (create), or they changed since
            ``expected_updated_at`` (update, delete).
        NotFoundError: ``details["resource"]`` is ``"dataset"``, ``"slice"`` or
            ``"vlmSettings"`` (no settings to update or delete).
        ForbiddenError: The caller may not edit them.
    """

    # Dataset ---------------------------------------------------------------
    def get_dataset_vlm_settings(self, dataset_id: str) -> Optional[DatasetVLMSettings]:
        """The question set of a dataset, or None when it has none."""
        response = self.request_gql(
            Queries.GET_DATASET_VLM_SETTINGS,
            Queries.GET_DATASET_VLM_SETTINGS["variables"](dataset_id),
        )
        return DatasetVLMSettings.from_platform(response) if response else None

    def create_dataset_vlm_settings(self, dataset_id: str, settings: VLMSettings) -> DatasetVLMSettings:
        """Create the question set of a VLM dataset. ConflictError if it already exists."""
        response = self.request_gql(
            Queries.CREATE_DATASET_VLM_SETTINGS,
            Queries.CREATE_DATASET_VLM_SETTINGS["variables"](dataset_id, settings),
        )
        return DatasetVLMSettings.from_platform(response)

    def update_dataset_vlm_settings(
        self,
        dataset_id: str,
        settings: VLMSettings,
        expected_updated_at: Optional[str] = None,
    ) -> DatasetVLMSettings:
        """Replace the question set of a dataset.

        Send the whole set, deleted questions and classes included. Pass the
        ``version`` of the record you read as ``expected_updated_at``.
        """
        response = self.request_gql(
            Queries.UPDATE_DATASET_VLM_SETTINGS,
            Queries.UPDATE_DATASET_VLM_SETTINGS["variables"](dataset_id, settings, expected_updated_at),
        )
        return DatasetVLMSettings.from_platform(response)

    def delete_dataset_vlm_settings(self, dataset_id: str, expected_updated_at: Optional[str] = None) -> bool:
        """Delete the question set of a dataset entirely. A new one can be created afterwards."""
        response = self.request_gql(
            Queries.DELETE_DATASET_VLM_SETTINGS,
            Queries.DELETE_DATASET_VLM_SETTINGS["variables"](dataset_id, expected_updated_at),
        )
        return bool(response)

    # Slice -----------------------------------------------------------------
    def get_slice_vlm_settings(self, dataset_id: str, slice_id: str) -> Optional[SliceVLMSettings]:
        """The question set of a slice, or None when it has none."""
        response = self.request_gql(
            Queries.GET_SLICE_VLM_SETTINGS,
            Queries.GET_SLICE_VLM_SETTINGS["variables"](dataset_id, slice_id),
        )
        return SliceVLMSettings.from_platform(response) if response else None

    def create_slice_vlm_settings(self, dataset_id: str, slice_id: str, settings: VLMSettings) -> SliceVLMSettings:
        """Create the question set of a slice. ConflictError if it already exists."""
        response = self.request_gql(
            Queries.CREATE_SLICE_VLM_SETTINGS,
            Queries.CREATE_SLICE_VLM_SETTINGS["variables"](dataset_id, slice_id, settings),
        )
        return SliceVLMSettings.from_platform(response)

    def update_slice_vlm_settings(
        self,
        dataset_id: str,
        slice_id: str,
        settings: VLMSettings,
        expected_updated_at: Optional[str] = None,
    ) -> SliceVLMSettings:
        """Replace the question set of a slice (same rules as the dataset one)."""
        response = self.request_gql(
            Queries.UPDATE_SLICE_VLM_SETTINGS,
            Queries.UPDATE_SLICE_VLM_SETTINGS["variables"](dataset_id, slice_id, settings, expected_updated_at),
        )
        return SliceVLMSettings.from_platform(response)

    def delete_slice_vlm_settings(
        self, dataset_id: str, slice_id: str, expected_updated_at: Optional[str] = None
    ) -> bool:
        """Delete the question set of a slice entirely."""
        response = self.request_gql(
            Queries.DELETE_SLICE_VLM_SETTINGS,
            Queries.DELETE_SLICE_VLM_SETTINGS["variables"](dataset_id, slice_id, expected_updated_at),
        )
        return bool(response)
