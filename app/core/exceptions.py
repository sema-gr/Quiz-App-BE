from fastapi import HTTPException, status


class CompanyNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found."
        )


class PermissionDenied(HTTPException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


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


class InvalidActionError(HTTPException):
    def __init__(self, detail: str = "Invalid action provided"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class QuizNotFound(HTTPException):
    def __init__(self, detail: str = "Quiz not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class PermissionDenied(HTTPException):
    def __init__(self, message: str = "Not enough permissions"):
        super().__init__(message)


class NotCompanyMember(HTTPException):
    def __init__(self, detail: str = "User is not a member of this company"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class MaxAttemptsReached(HTTPException):
    def __init__(self, detail: str = "Maximum number of quiz attempts reached"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
