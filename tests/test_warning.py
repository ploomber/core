# import posthog

from unittest.mock import patch, ANY
from ploomber_core.warnings import deprecation_warning
import pytest


@patch("posthog.capture")
def test_deprecation_warning_w_posthug(capture):
    # To test if warning is shown
    with pytest.warns(FutureWarning):
        deprecation_warning("Test")

    # To test if posthug.capture is called
    capture.assert_called_once_with(
        ANY, "deprecation-warning-shown", {"message": "Test"}
    )
