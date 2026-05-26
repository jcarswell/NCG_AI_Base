"""Custom exceptions for NCG."""


class NCGException(Exception):
    """Base exception for all NCG errors."""

    pass


class ConfigurationError(NCGException):
    """Raised when configuration is invalid."""

    pass


class ServiceNowError(NCGException):
    """Raised when ServiceNow integration fails."""

    pass


class SecretServerError(NCGException):
    """Raised when SecretServer integration fails."""

    pass


class TemplateError(NCGException):
    """Raised when template operations fail."""

    pass


class ValidationError(NCGException):
    """Raised when validation fails."""

    pass


class GenerationError(NCGException):
    """Raised when configuration generation fails."""

    pass
