#!/usr/bin/env python
# Copyright (C) 2017 DearBytes B.V. - All Rights Reserved


class DearBytesException(Exception):
    """
    Base class for custom exceptions
    Child of Exception class
    """


class ConfigurationException(DearBytesException):
    pass


class ServerException(DearBytesException):
    pass


class DirectoryNotFoundException(DearBytesException):
    pass


class IntegrityException(DearBytesException):
    pass
