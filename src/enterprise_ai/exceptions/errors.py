"""Application exception hierarchy."""


class EnterpriseAIError(Exception):
    """Base exception for expected application errors."""


class ConfigurationError(EnterpriseAIError):
    """Raised when application configuration is invalid."""


class ValidationError(EnterpriseAIError):
    """Raised when an application contract is violated."""


class DependencyError(EnterpriseAIError):
    """Raised when a required dependency or downstream service fails."""
