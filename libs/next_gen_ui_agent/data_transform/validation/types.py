class ComponentDataValidationError:
    """Component Data Validation Error"""

    code: str
    """Error code describing field in error and the error itself"""
    message: str
    """Error message with more info about nature of the error"""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message

    def __str__(self):
        return f'"{self.code}: {self.message}"'

    def __repr__(self):
        return f'"{self.code}: {self.message}"'
