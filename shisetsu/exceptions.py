"""
shisetsu.contract
<github.com/kixpanganiban>

Contains `DigestMismatch`.
"""


class RequestFailure(Exception):
    """Raised when a Contract was not fulfilled.
    """

    def __init__(self, failure):
        self.message = failure.get()['failure_message']
        super(RequestFailure, self).__init__(self.message)
