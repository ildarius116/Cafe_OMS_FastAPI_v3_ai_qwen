"""Кастомные исключения приложения."""


class AppError(Exception):
    """Базовое исключение приложения."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppError):
    """Ресурс не найден."""
    
    def __init__(self, message: str = "Ресурс не найден"):
        super().__init__(message, status_code=404)


class ValidationError(AppError):
    """Ошибка валидации данных."""
    
    def __init__(self, message: str = "Ошибка валидации"):
        super().__init__(message, status_code=400)


class AuthenticationError(AppError):
    """Ошибка аутентификации."""
    
    def __init__(self, message: str = "Неверные учётные данные"):
        super().__init__(message, status_code=401)


class PermissionError(AppError):
    """Недостаточно прав для выполнения операции."""
    
    def __init__(self, message: str = "Недостаточно прав"):
        super().__init__(message, status_code=403)


class ConflictError(AppError):
    """Конфликт данных (например, дубликат)."""
    
    def __init__(self, message: str = "Конфликт данных"):
        super().__init__(message, status_code=409)
