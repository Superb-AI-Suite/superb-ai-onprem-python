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
    system_sdk_user_email: Optional[str] = Field(None, alias="systemSdkUserEmail")

    _access_token: Optional[str] = None
    _instance: ClassVar[Optional["AuthUser"]] = None

    @classmethod
    def get_instance(
        cls,
        config_file: str = "~/.spb/onprem-config"
    ) -> "AuthUser":
        if cls._instance is None:
            config_file_path = os.path.expanduser(config_file)
            
            if not os.path.exists(config_file_path):
                cls._instance = cls._create_system_sdk_instance()
            else:
                cls._instance = cls._create_config_instance(config_file_path)
        return cls._instance

    @classmethod
    def _create_system_sdk_instance(cls) -> "AuthUser":        
        system_sdk_host = os.environ.get("SUNRISE_SERVER_URL") or os.environ.get("SUPERB_SYSTEM_SDK_HOST") or "http://app-api:8080"
        
        return cls(
            host=system_sdk_host,
            access_key="",
            access_key_secret="",
            is_system_sdk=True,
            system_sdk_user_email=os.environ.get("SUPERB_SYSTEM_SDK_USER_EMAIL", "system@superb-ai.com")
        )

    @classmethod
    def _create_config_instance(cls, config_file_path: str) -> "AuthUser":
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
            
            return cls(
                host=config["default"]["host"],
                access_key=config["default"]["access_key"],
                access_key_secret=config["default"]["access_key_secret"],
                is_system_sdk=False,
                system_sdk_user_email=None
            )
        except configparser.Error as e:
            raise SDKConfigError(f"Error parsing config file: {str(e)}") from e

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
