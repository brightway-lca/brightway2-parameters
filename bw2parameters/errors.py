class ValidationError(Exception):
    pass


class ParameterError(ValidationError):
    pass


class CapitalizationError(ParameterError):
    """Parameter(s) names are case-sensitive"""
    pass


class DuplicateName(ValidationError):
    pass


class MissingName(ValidationError):
    pass


class SelfReference(ValidationError):
    pass
