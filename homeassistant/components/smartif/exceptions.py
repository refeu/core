"""Exceptions for SmartIf."""


class SmartIfError(Exception):
    """Generic SmartIf exception."""


class SmartIfConnectionError(SmartIfError):
    """SmartIf connection exception."""
