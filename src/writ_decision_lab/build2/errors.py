class InputError(ValueError):
    """Malformed or unsupported caller input."""


class CheckError(ValueError):
    """A result bundle failed independent exact checking."""


class BackendUnavailable(RuntimeError):
    """The search backend failed or supplied no usable evidence."""

