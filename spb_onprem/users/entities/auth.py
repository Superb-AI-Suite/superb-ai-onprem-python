import base64
import os
import configparser
from typing import Optional, ClassVar

from spb_onprem.base_model import CustomBaseModel, Field
from spb_onprem.exceptions import SDKConfigError

class AuthUser(CustomBaseModel):
    host: str = Field(alias="host")
    access_key: str = Field(alias="accessKey")
    access_key_secret: str = Field(alias="accessKeySecret")
    is_system_sdk: bool = Field(alias="isSystemSdk")
    system_sdk_user_email: str = Field(alias="systemSdkUserEmail")

    _access_token: Optional[str] = None
    _instance: ClassVar[Optional["AuthUser"]] = None

    @classmethod
    def get_instance(
        cls,
        config_file: str = "~/.spb/onprem-config"
    ) -> "AuthUser":
        if cls._instance is None:
            if os.environ.get("SUPERB_SYSTEM_SDK") == "true":
                if not os.environ.get("SUNRISE_SERVER_URL") and not os.environ.get("SUPERB_SYSTEM_SDK_HOST"):
                    raise SDKConfigError("Superb Platform SDK is not configured. Please set the environment variable SUPERB_SYSTEM_SDK_URL.")
                
                if os.environ.get("SUNRISE_SERVER_URL"):
                    system_sdk_host = os.environ.get("SUNRISE_SERVER_URL")
                else:
                    system_sdk_host = os.environ.get("SUPERB_SYSTEM_SDK_HOST")
                
                # Skip reading config file when SUPERB_SYSTEM_SDK is true
                cls._instance = cls(
                    host=system_sdk_host,
                    access_key="",
                    access_key_secret="",
                    is_system_sdk=True,
                    system_sdk_user_email=os.environ.get("SUPERB_SYSTEM_SDK_USER_EMAIL", "")
                )
            else:
                config_file_path = os.path.expanduser(config_file)
                config = configparser.ConfigParser()
                try:
                    if not config.read(config_file_path):
                        raise SDKConfigError(f"Failed to read config file: {config_file_path}")
                    
                    if "default" not in config:
                        raise SDKConfigError(f"Missing 'default' section in config file: {config_file_path}")
                    
                    required_keys = ["host", "access_key", "access_key_secret"]
                    for key in required_keys:
                        if key not in config["default"]:
                            raise SDKConfigError(f"Missing required key '{key}' in config file: {config_file_path}")
                    
                    cls._instance = cls(
                        host=config["default"]["host"],
                        access_key=config["default"]["access_key"],
                        access_key_secret=config["default"]["access_key_secret"],
                        is_system_sdk=False
                    )
                except configparser.Error as e:
                    raise SDKConfigError(f"Error parsing config file: {str(e)}") from e
        return cls._instance

    @property
    def access_token(self):
        if self._access_token:
            return self._access_token
        decoded_token = f"{self.access_key}:{self.access_key_secret}"
        decoded_token_bytes = decoded_token.encode("utf-8")
        encoded_token = base64.b64encode(decoded_token_bytes).decode("utf-8")
        self._access_token = f"Basic {encoded_token}"
        return self._access_token
    
    @property
    def auth_headers(self):
        if self.is_system_sdk:
            return {
                "x-user-email": self.system_sdk_user_email
            }
        return {
            "Authorization": self.access_token
        }
