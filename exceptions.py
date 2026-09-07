class HealthcareSystemError(Exception):
    """Base exception for the healthcare appointment system."""


class ValidationError(HealthcareSystemError):
    """Raised when user input fails validation."""


class DuplicateAppointmentError(HealthcareSystemError):
    """Raised when an appointment conflicts with an existing active slot."""


class RecordNotFoundError(HealthcareSystemError):
    """Raised when a requested patient, doctor, or appointment is missing."""
