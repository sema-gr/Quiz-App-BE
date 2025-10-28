from fastapi import HTTPException, status


class CompanyNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found."
        )


class PermissionDenied(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
        )


class MemberAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a pending or active status",
        )


class InvitationNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found"
        )


class RequestNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Membership request not found"
        )


class MemberNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company member not found."
        )


class UserAlreadyExistsError(HTTPException):
    def __init__(self, detail: str = "User already exists"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidCredentialsError(HTTPException):
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InvalidTokenError(HTTPException):
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class TokenValidationError(HTTPException):
    def __init__(self, detail: str = "Token validation failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class AuthConfigurationError(HTTPException):
    def __init__(self, detail: str = "Authentication configuration error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )


class InvalidActionError(Exception):
    def __init__(self, detail: str = "Invalid action provided"):
        self.detail = detail
