class ServiceError(Exception):
    """Base class for event-related exceptions."""


class EventNotFoundError(ServiceError):
    """Raised when the event does not exist."""


class EventExpiredError(ServiceError):
    """Raised when the event has already started or passed."""


class EventCreatorLeaveError(ServiceError):
    """Raised when the creator attempts to leave their own event."""


class UserNotParticipantError(ServiceError):
    """Raised when a non-participant tries to leave the event."""


class UserIsAlreadyParticipantError(ServiceError):
    """Raised when a user is already participant."""


class UserNotFoundError(ServiceError):
    """Raised when a user not present"""


class NotEventCreatorError(ServiceError):
    """Raised when a non-creator tries to delete the event."""
