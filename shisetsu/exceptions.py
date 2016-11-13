"""
shisetsu.exceptions
<github.com/kixpanganiban>

Contains `DigestMismatch`.
"""


class MiddlewareError(Exception):
    """Raised when a middleware doesn't return a contract.
    """
    pass

class RequestFailure(Exception):
    """Raised when a Contract was not fulfilled.
    """

    def __init__(self, failure):
        self.message = failure.get()['failure_message']
        super(RequestFailure, self).__init__(self.message)


class TimeoutError(Exception):
    """Raised when timeout has been reached after calling a remote function.
    """

    def __init__(self, func, timeout):
        self.message = 'No response from remote func `{}` after {} seconds'\
                       .format(func, timeout)
        super(TimeoutError, self).__init__(self.message)
