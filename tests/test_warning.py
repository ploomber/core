# import posthog

from unittest.mock import patch, ANY
from ploomber_core.warnings import deprecation_warning
from ploomber_core.telemetry import telemetry as telemetry_module

import pytest


@patch("posthog.capture")
def test_deprecation_warning_w_posthug(capture):
    telemetry = telemetry_module.Telemetry(
        api_key="KEY", package_name="somepackage", version="0.1"
    )

    # To test if warning is shown
    with pytest.warns(FutureWarning):
        deprecation_warning("Test", telemetry)

    # # To test if posthug.capture is called
    capture.assert_called_once_with(
        distinct_id=ANY,
        event="deprecation-warning-shown",
        properties={
            "event_id": ANY,
            "user_id": ANY,
            "action": "deprecation-warning-shown",
            "client_time": ANY,
            "metadata": {"message": "Test"},
            "total_runtime": None,
            "python_version": ANY,
            "version": "0.1",
            "package_name": "somepackage",
            "docker_container": False,
            "cloud": None,
            "email": None,
            "os": ANY,
            "environment": ANY,
            "telemetry_version": ANY,
        },
    )
