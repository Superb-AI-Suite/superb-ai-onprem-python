import os
from typing import Dict, Any

from spb_onprem.base_service import BaseService
from spb_onprem.exceptions import BadParameterError


class InferService(BaseService):
    """Service class for handling inference operations."""
    
    def __init__(self):
        super().__init__()
        self.model_endpoint_url = os.environ.get("MODEL_ENDPOINT_URL")
        if not self.model_endpoint_url:
            raise ValueError("MODEL_ENDPOINT_URL environment variable is required")
    
    def infer_data(
        self,
        model_id: str,
        base64_image: str
    ) -> Dict[str, Any]:
        """Perform inference on image data using the specified model.
        
        Args:
            model_id (str): The model ID to use for inference.
            base64_image (str): Base64 encoded image data.
        
        Returns:
            Dict[str, Any]: The inference result.
        
        Raises:
            BadParameterError: If required parameters are missing.
        """
        if model_id is None:
            raise BadParameterError("model_id is required.")
        if base64_image is None:
            raise BadParameterError("base64_image is required.")
            
        payload = {
            "model_id": model_id,
            "base64_image": base64_image,
        }
        
        try:
            response = self.request(
                method="POST",
                url=self.model_endpoint_url,
                json_data=payload,
                headers={
                    "Content-Type": "application/json"
                }
            )
            return response
        except Exception as e:
            print(f"Failed to fetch inference result: {e}")
            raise