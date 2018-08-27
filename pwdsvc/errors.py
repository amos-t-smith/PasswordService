"""
Provides common error types.
"""

class QueryError(RuntimeError):
    """
    This class when raised provides conveys that an exceptional
    situation occurred while trying to process a query.
    """
    pass


class PathError(RuntimeError):
    """
    This class when raised conveys that an exceptional
    situation occurred while trying load the passwd
    or group files respectively; i.e. bad path to file.
    """
    pass
