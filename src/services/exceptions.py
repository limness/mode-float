class ServiceError(Exception):
    """Base class for service-layer errors."""

    pass


class RegionCreateError(ServiceError):
    """Raised when a region cannot be created."""

    pass


class UavFlightCreateError(ServiceError):
    """Raised when a UAV flight cannot be created."""

    pass


class FileCreateError(ServiceError):
    """Raised when a file metadata record cannot be created."""

    pass


class FileDeactivateError(ServiceError):
    """Raised when existing file metadata records cannot be deactivated."""

    pass
