"""
shisetsu.middlewares
<github.com/kixpanganiban>

Contains `Middlewares`.
"""
from .contract import Contract
from .exceptions import MiddlewareError

class Middlewares(object):
    """Middlewares facilitate registering and executing middlwares wherever
    they are defined. To add a middleware handler, a function called `handler`
    may be passed to `Middlewares.register_before` or
    `Middlewares.register_after`.

    In a Server:
    All handlers registered via the former are called before the contract is
    sent to the `func` it calls, that is, after it is unpacked and created.
    Handlers registered via the latter are called after the `func` returns a
    response and an outgoing contract is created.

    In a Client:
    All handlers registered via the former are called before the request is
    packed and sent to the channel. Handlers registered via the latter are
    called after the response is received, and before the response body is
    returned.

    A `handler` MUST return a Contract after execution, or a `MiddlewareError`
    will be raised. To interrupt processing of a contract, you may raise a
    custom exception inside a handler.

    Example usage:
        from shisetsu.server import Server

        def dictify(contract):
            contract.body = {
                'status': 'OK',
                'content': contract.body
            }
            return contract

        s = Server('db_reader')
        server.middlewares.register_after(dictify)
    """

    def __init__(self):
        self._middlewares = {
            'before': [],
            'after': []
        }

    @classmethod
    def check_return(cls, return_value):
        """Check if the middleware handler's response is a valid Contract.
        """
        if not return_value:
            raise MiddlewareError('Middleware handler returned None')
        if not isinstance(return_value, Contract):
            raise MiddlewareError('Middleware must return a contract')
        return return_value

    def register_before(self, handler):
        """Register a before `handler`.
        """
        self._middlewares['before'].append(handler)

    def register_after(self, handler):
        """Register an after `handler`.
        """
        self._middlewares['after'].append(handler)

    def execute_before(self, contract):
        """Execute all before `handler`s on the contract.
        """
        for handler in self._middlewares['before']:
            contract = self.check_return(handler(contract))
        return contract

    def execute_after(self, contract):
        """Execute all after `handler`s on the contract.
        """
        for handler in self._middlewares['after']:
            contract = self.check_return(handler(contract))
        return contract
