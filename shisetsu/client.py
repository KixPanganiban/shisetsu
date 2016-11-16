"""
shisetsu.client
<github.com/kixpanganiban>

Contains `Client` and `CallableClient`.
"""
import time

from redis import StrictRedis

from .contract import Contract, Request, Response, Failure
from .exceptions import RequestFailure, TimeoutError
from .logger import Logger
from .middlewares import Middlewares


class Client(object):
    """A Client handles requesting a Server to fulfill a Request,
    and returns the Response body or the Failure details.
    """
    def __init__(self, channel, timeout=3, host='localhost', port=6379, db=0,
                 raise_on_failure=True):
        self.channel = channel
        self.logger = Logger(channel).get()
        self.middlewares = Middlewares()
        self.raise_on_failure = raise_on_failure
        self.redis_client = StrictRedis(host, port, db)
        self.response_channel = self.redis_client.pubsub(
            ignore_subscribe_messages=True
        )
        self.timeout = timeout

    def call(self, func, *args, **kwargs):
        """Execute a remote `func`, that is: create a Request and pass it to the
        remote Server. Will block until request is received. If `self.timeout`
        is set, will raise a TimeoutError if `self.timeout` seconds have passed
        and no response is received, otherwise blocks indefinitely.
        """
        request = Request(func, *args, **kwargs)
        self.middlewares.execute_before(request)
        self.response_channel.subscribe(request.digest)
        self.redis_client.publish(self.channel, Contract.send(request))
        start = time.time()
        while True:
            message = self.response_channel.get_message()
            if message and message['type'] == 'message':
                response = Contract.receive(message['data'], request.digest)
                if response:
                    self.middlewares.execute_after(response)
                    if isinstance(response, Response):
                        self.response_channel.unsubscribe(Request.digest)
                        return response.get()
                    elif isinstance(response, Failure):
                        if self.raise_on_failure:
                            self.response_channel.unsubscribe(Request.digest)
                            raise RequestFailure(response)
                        else:
                            self.response_channel.unsubscribe(Request.digest)
                            return response
            if (self.timeout is not None
                    and time.time() >= start + self.timeout):
                raise TimeoutError(func, self.timeout)
            time.sleep(0.001)

    def set_timeout(self, timeout):
        """Sets the client timeout duration in seconds.
        """
        self.timeout = timeout


class CallableClient(Client):
    """A thin wrapper around the Client, which makes it syntactically easier
    to call remote requests by treating function calls as remote requests.

    Example:

    Using Client class:

        >>> c = Client('channel')
        >>> c.call('sum', 1, 1)
        2

    Using CallableClient:

        >>> c = CallableClient('channel')
        >>> c.sum(1, 1)
        2
    """

    def __getattribute__(self, name):
        def _wrapped_call(*args, **kwargs):
            return self.call(name, *args, **kwargs)

        if name not in ['call', 'channel', 'middlewares', 'logger',
                        'raise_on_failure', 'redis_client',
                        'response_channel', 'timeout']:
            return _wrapped_call
        else:
            return super(CallableClient, self).__getattribute__(name)
