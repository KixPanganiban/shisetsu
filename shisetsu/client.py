"""
shisetsu.client
<github.com/kixpanganiban>

Contains `Client` and `CallableClient`.
"""
import time

from redis import StrictRedis

from .contract import Contract, Request, Response, Failure
from .exceptions import RequestFailure
from .logger import Logger


class Client(object):
    """A Client handles requesting a Server to fulfill a Request,
    and returns the Response body or the Failure details.
    """
    def __init__(self, channel, host='localhost', port=6379, db=0,
                 raise_on_failure=True):
        self.channel = channel
        self.logger = Logger(channel).get()
        self.raise_on_failure = raise_on_failure
        self.redis_client = StrictRedis(host, port, db)
        self.response_channel = self.redis_client.pubsub(
            ignore_subscribe_messages=True
        )

    def call(self, func, *args, **kwargs):
        """Execute a remote func, that is: create a Request and pass it to the
        remote Server. Will block until request is received.
        """
        request = Request(func, *args, **kwargs)
        self.response_channel.subscribe(request.digest)
        self.redis_client.publish(self.channel, Contract.send(request))
        while True:
            message = self.response_channel.get_message()
            if message and message['type'] == 'message':
                response = Contract.receive(message['data'], request.digest)
                if response:
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
            time.sleep(0.001)


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

        if name not in ['call', 'channel', 'logger', 'raise_on_failure',
                        'redis_client', 'response_channel']:
            return _wrapped_call
        else:
            return super(CallableClient, self).__getattribute__(name)
