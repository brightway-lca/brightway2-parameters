class ValidationError(StandardError):
    pass


class CircularReference(ValidationError):
    pass


class DuplicateName(ValidationError):
    pass


class MissingName(ValidationError):
    pass


class SelfReference(ValidationError):
    pass


class MissingParameter(ValidationError):
    pass
