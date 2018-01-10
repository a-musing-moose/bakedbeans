class BakedBeansError(Exception):
    pass


class ContentNotFoundError(BakedBeansError):
    pass


class InvalidContent(BakedBeansError):
    pass


class BeanValidationError(BakedBeansError):
    pass
