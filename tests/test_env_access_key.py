"""A key in the environment makes the SDK call the public API as that person (engine Pods, MOD2-24)."""
import pytest

from spb_onprem.exceptions import SDKConfigError
from spb_onprem.users.entities import AuthUser


@pytest.fixture(autouse=True)
def fresh(monkeypatch, tmp_path):
    for name in ("SUPERB_ACCESS_KEY", "SUPERB_ACCESS_KEY_SECRET", "SUNRISE_SERVER_URL", "SUPERB_SYSTEM_SDK_HOST"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(AuthUser, "_instance", None)
    yield tmp_path / "missing-config"
    AuthUser._instance = None


def test_env_key_uses_public_api_with_basic_auth(monkeypatch, fresh):
    monkeypatch.setenv("SUPERB_ACCESS_KEY", "test-key")
    monkeypatch.setenv("SUPERB_ACCESS_KEY_SECRET", "test-secret")
    monkeypatch.setenv("SUPERB_SYSTEM_SDK_HOST", "http://app-api:8080")
    user = AuthUser.get_instance(str(fresh))
    assert user.is_system_sdk is False
    assert user.host == "http://app-api:8080"
    assert set(user.auth_headers) == {"Authorization"}
    assert user.auth_headers["Authorization"].startswith("Basic ")


def test_env_key_wins_over_config_file(monkeypatch, tmp_path):
    config = tmp_path / "onprem-config"
    config.write_text("[default]\nhost=https://pc.example.test\naccess_key=file-key\naccess_key_secret=file-secret\n")
    monkeypatch.setenv("SUPERB_ACCESS_KEY", "test-key")
    monkeypatch.setenv("SUPERB_ACCESS_KEY_SECRET", "test-secret")
    user = AuthUser.get_instance(str(config))
    assert user.access_key == "test-key"


@pytest.mark.parametrize("present", ["SUPERB_ACCESS_KEY", "SUPERB_ACCESS_KEY_SECRET"])
def test_half_a_key_is_an_error_not_the_system_api(monkeypatch, fresh, present):
    monkeypatch.setenv(present, "value")
    with pytest.raises(SDKConfigError):
        AuthUser.get_instance(str(fresh))


def test_no_key_and_no_config_stays_system_api(fresh):
    user = AuthUser.get_instance(str(fresh))
    assert user.is_system_sdk is True
    assert set(user.auth_headers) == {"x-user-email"}
