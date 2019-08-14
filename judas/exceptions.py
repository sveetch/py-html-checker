# -*- coding: utf-8 -*-
"""
Exceptions
==========

Specific application exceptions.
"""


class JudasBaseException(Exception):
    """
    Base for every application exceptions.
    """
    pass


class PathInvalidError(JudasBaseException):
    """
    Exception to be raised when given path is invalid.
    """
    pass


class ReportError(JudasBaseException):
    """
    Exception to be raised when validator return invalid report or report
    export has failed.
    """
    pass


class SitemapInvalidError(JudasBaseException):
    """
    Exception to be raised when sitemap ressource is invalid.
    """
    pass


class ValidatorError(JudasBaseException):
    """
    Exception to be raised when validator fail.
    """
    pass
