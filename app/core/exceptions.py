# In app/core/exceptions.py

class AppException(Exception):
    """
    Base class for all custom exceptions in this application.
    Each custom exception should inherit from this class.
    """
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

# --- Authentication/Authorization Exceptions ---

class InvalidCredentials(AppException):
    def __init__(self, detail: str = "Incorrect email or password"):
        super().__init__(status_code=401, detail=detail)

class NotAuthorized(AppException):
    def __init__(self, detail: str = "You are not authorized to perform this action"):
        super().__init__(status_code=403, detail=detail)

class InactiveUser(AppException):
    def __init__(self, detail: str = "Your account is inactive."):
        super().__init__(status_code=403, detail=detail)

class UnverifiedUser(AppException):
    def __init__(self, detail: str = "Your account has not been verified."):
        super().__init__(status_code=403, detail=detail)

class InvalidToken(AppException):
    def __init__(self, detail: str = "Token is invalid or has expired"):
        super().__init__(status_code=401, detail=detail)

# --- User Management Exceptions ---

class UserNotFound(AppException):
    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=404, detail=detail)

class UserAlreadyExists(AppException):
    def __init__(self, detail: str = "A user with this email already exists"):
        super().__init__(status_code=409, detail=detail)



# --- Book Management Exceptions ---
class BookNotFound(AppException):
    def __init__(self, detail: str = "Book not found"):
        super().__init__(status_code=404, detail=detail)

class BookAlreadyExists(AppException):
    def __init__(self, detail: str = "This book already exists"):
        super().__init__(status_code=409, detail=detail)
        
        
# --- Book Management Exceptions ---
class ReviewNotFound(AppException):
    def __init__(self, detail: str = "Review not found"):
        super().__init__(status_code=404, detail=detail)
        

# --- Tag Management Exceptions ---
class TagNotFound(AppException):
    def __init__(self, detail: str = "Tag not found"):
        super().__init__(status_code=404, detail=detail)

class TagAlreadyExists(AppException):
    def __init__(self, detail: str = "This tag already exists"):
        super().__init__(status_code=409, detail=detail)
