class ValidationError(Exception):
    pass


class ParameterError(ValidationError):
    pass


class DuplicateName(ValidationError):
    pass


class MissingName(ValidationError):
    pass


class SelfReference(ValidationError):
    pass
