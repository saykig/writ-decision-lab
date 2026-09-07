"""Build 2: checked finite rational uncertainty profiles.

Imports stay lazy so the exact checker remains usable when the optional search
backend is absent.
"""


def solve_and_check(*args, **kwargs):
    from .engine import solve_and_check as implementation
    return implementation(*args, **kwargs)


def consume(*args, **kwargs):
    from .consumer import consume as implementation
    return implementation(*args, **kwargs)


__all__ = ["solve_and_check", "consume"]
