class CompanyError(Exception):
    """Error"""


class CompanyNotFound(CompanyError):
    """Company not found"""


class PermissionDenied(CompanyError):
    """Permission denied"""
