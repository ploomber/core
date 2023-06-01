from warnings import warn
from ploomber_core.telemetry import telemetry


class PloomberDeprecationWarning(FutureWarning):
    """
    Notes
    -----
    .. versionchanged:: 0.1
        Changed superclass from UserWarning to FutureWarning
    """

    # @
    def __init__(self, message):
        print("message: ", message)
        self.message = message


def deprecation_warning(message, module_telemetry=None):
    """Raise deprecation warning message, also log to posthug if telemetry instance
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

    if module_telemetry and isinstance(module_telemetry, telemetry.Telemetry):
        module_telemetry.log_api(
            action="deprecation-warning-shown", metadata={"message": message}
        )
