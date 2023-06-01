from warnings import warn
from uuid import uuid4
import posthog


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


def deprecation_warning(message):
    warn(message, FutureWarning)
    # log the event to posthog
    posthog.project_api_key = "phc_JtG9P0pl0v0XExLqbqKfmXZjUm2wFq9cCxHE4LM74IG"
    event_id = uuid4()
    posthog.capture(event_id, "deprecation-warning-shown", {"message": message})
