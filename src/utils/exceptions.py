"""Custom exceptions for the automation scaffold."""


class YouTubeAutomationError(Exception):
    """Base exception for project-specific failures."""


class ConfigurationError(YouTubeAutomationError):
    """Raised when configuration is missing or malformed."""


class ValidationError(YouTubeAutomationError):
    """Raised when user input or pipeline state is invalid."""


class ExternalServiceError(YouTubeAutomationError):
    """Raised when an external API call or client check fails."""
