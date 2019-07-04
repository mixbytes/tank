
class TankError(RuntimeError):
    """
    Base class of Tank-specific errors.
    """
    pass


class TankConfigError(TankError):
    """
    Configuration error.
    """
    pass


class TankTestCaseError(TankError):
    """
    Error specific for a test case configuration.
    """
    pass
