# -*- coding: utf-8 -*-
"""
Exceptions
==========

Specific application exceptions.
"""


class HtmlCheckerUnexpectedException(Exception):
    """
    An exceptions which should not never raise from code.

    DON'T use this in code, this is reserved for tests purposes only.
    """
    pass


class HtmlCheckerBaseException(Exception):
    """
    Base for every application exceptions.
    """
    pass


class ExportError(HtmlCheckerBaseException):
    """
    Exception to be raised when report export fail.
    """
    pass


class PathInvalidError(HtmlCheckerBaseException):
    """
    Exception to be raised when given path is invalid.
    """
    pass


class ReportError(HtmlCheckerBaseException):
    """
    Exception to be raised when validator return invalid report or report
    export has failed.
    """
    pass


class SitemapInvalidError(HtmlCheckerBaseException):
    """
    Exception to be raised when sitemap ressource is invalid.
    """
    pass


class ValidatorError(HtmlCheckerBaseException):
    """
    Exception to be raised when validator fail.
    """
    pass
