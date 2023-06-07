from warnings import warn


class PloomberDeprecationWarning(FutureWarning):
    """
    Notes
    -----
    .. versionchanged:: 0.1
        Changed superclass from UserWarning to FutureWarning
    """

    pass


def deprecation_warning(telemetry, message):
    """Raise deprecation warning message, also log to posthog with telemetry instance
    is provided

    Parameters
    ----------
    module_telemetry : Telemetry
        The telemetry instance defined in ploomber_core.telemetry.Telemetry

    action : str
        The action to log to posthog. example: deprecated-feature-warning

    message : str
        The warning message displayed to the user
    """
    warn(message, FutureWarning)
    telemetry.log_api(action="deprecation-warning-shown", metadata={"message": message})
