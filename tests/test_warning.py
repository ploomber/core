# import posthog

from unittest.mock import Mock
from ploomber_core.warnings import deprecation_warning
from ploomber_core.telemetry import telemetry as telemetry_module

import pytest


def test_deprecation_warning_w_posthog(monkeypatch):
    # Initiate telemetry instance with mock_log_api
    somepackage_telemetry = telemetry_module.Telemetry(
        api_key="KEY", package_name="somepackage", version="0.1"
    )
    mock_log_api = Mock()
    monkeypatch.setattr(somepackage_telemetry, "log_api", mock_log_api)

    # To test if warning is shown
    with pytest.warns(FutureWarning):
        deprecation_warning("Test", somepackage_telemetry)

    # To test if log_api is called
    mock_log_api.assert_called_once_with(
        action="deprecation-warning-shown", metadata={"message": "Test"}
    )
