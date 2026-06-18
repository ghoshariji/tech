from typing import Any, Dict, List, Optional


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        errors: Optional[List[Dict[str, Any]]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, resource: str, identifier: Any = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(message=message, status_code=404)


class ConflictException(AppException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=409)


class ValidationException(AppException):
    def __init__(self, message: str, errors: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message=message, status_code=422, errors=errors)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message=message, status_code=403)


class BadRequestException(AppException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=400)


class InsufficientStockException(AppException):
    def __init__(self, product_name: str, available: int, requested: int):
        super().__init__(
            message=f"Insufficient stock for '{product_name}'. Available: {available}, Requested: {requested}",
            status_code=400,
        )


class RateLimitException(AppException):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message=message, status_code=429)
