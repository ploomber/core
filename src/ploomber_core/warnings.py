from warnings import warn
from ploomber_core.telemetry import telemetry as core_telemetry


class PloomberDeprecationWarning(FutureWarning):
    """
    Notes
    -----
    .. versionchanged:: 0.1
        Changed superclass from UserWarning to FutureWarning
    """

    pass


def deprecation_warning(telemetry, message):
    """Raise deprecation warning message, also log to posthog if telemetry instance
    is provided

    Parameters
    ----------
    message : str
        The warning message displayed to the user
    module_telemetry : Telemetry
        The telemetry instance defined in ploomber_core.telemetry.Telemetry,
        by default None
    """
    warn(message, FutureWarning)
    if telemetry and isinstance(telemetry, core_telemetry.Telemetry):
        telemetry.log_api(
            action="deprecation-warning-shown", metadata={"message": message}
        )
