"""
shisetsu.server
<github.com/kixpanganiban>

Contains `Server`.
"""
import time

from redis import StrictRedis

from .contract import Contract, Failure, Response
from .logger import Logger
from .middlewares import Middlewares


class Server(object):
    """A Server is created with a `channel`, which it will attach an inbox, a
    `funcs` object which contains the handlers for all received Requests, and
    the StrictRedis parameters `host`, `port`, and `db`.

    It will listen to all inbox Requests when `run` is called, and will return
    either a Response or Failure the channel of the requesting client.
    """

    def __init__(self, channel, funcs, host='localhost', port=6379, db=0):
        self.channel = channel
        self.funcs = funcs
        self.inbox = None
        self.logger = Logger(channel).get()
        self.middlewares = Middlewares()
        self.redis_client = StrictRedis(host, port, db)
        self.running = False

    def _dispatch(self, message):
        request = Contract.receive(message)
        func = request.func
        args = request.args
        kwargs = request.kwargs
        try:
            self.logger.info('Received Request `%s`: %s(%s, %s)',
                             request.digest, func, str(args), str(kwargs))
            self.middlewares.execute_before(request)
            func_exec = getattr(self.funcs, func)
            response = Response(request.digest, func_exec(*args, **kwargs))
            self.middlewares.execute_after(response)
            self._publish(response)
            self.logger.info('Fulfilled Request `%s`: %s(%s, %s)',
                             response.request_digest, func, str(args),
                             str(kwargs))
        except AttributeError:
            failure = Failure(request.digest, Failure.FAILURE_NOHANDLER,
                              'No handlers for {}'.format(func))
            self._publish(failure)
            self.logger.error(
                'Returned FAILURE_NOHANDLER for `%s`: %s(%s, %s)',
                failure.request_digest, func, str(args), str(kwargs))
        except Exception as exc:
            failure = Failure(request.digest, Failure.FAILURE_EXCEPTION,
                              exc.message)
            self._publish(failure)
            self.logger.error('Returned FAILURE_EXCEPTION for `%s`: %s',
                              failure.request_digest, exc.message)

    def _publish(self, response):
        message = Contract.send(response)
        self.redis_client.publish(response.request_digest, message)

    def close(self):
        """Stop the server from lsitening for more messages.
        """
        self.inbox.unsubscribe(self.channel)
        self.running = False
        self.logger.info('Server STOPPED listening on channel %s',
                         self.channel)

    def run(self):
        """Listen to incoming requests in the inbox and handle them.
        """
        self.inbox = self.redis_client.pubsub(ignore_subscribe_messages=True)
        self.inbox.subscribe(self.channel)
        self.logger.info('Server STARTED listening on channel %s',
                         self.channel)
        self.running = True
        while self.running:
            message = self.inbox.get_message()
            if message and message['type'] == 'message':
                message = message['data']
                self._dispatch(message)
            time.sleep(0.001)
