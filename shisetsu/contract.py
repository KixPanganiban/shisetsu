"""
shisetsu.contract
<github.com/kixpanganiban>

Contains `Contract`, `Request`, `Response`, and `Failure`.
"""
from datetime import datetime
import hmac

import msgpack


class Contract(object):
    """The Contract is the base class for the Request, Response, and Failure
    contracts. It includes the `pack` and `unpack` methods, and accepts the
    following parameters to instatiate:

        headers       -- dict of header contents
        body          -- dict of contract body
        contract_type -- integer contract type

    When created, a `digest` is generated using the HMAC function with the
    datetime string as as key and the string headers+body as message.

    When dumped, a list-type `payload` is created:
        [contract_type, digest, headers, body]

    When loading, the payload's digest is compared to the generated digest
    and raises DigestMismatch when it fails.
    """

    CONTRACT_REQUEST = 0
    CONTRACT_RESPONSE = 1
    CONTRACT_FAILURE = -1

    digest = None
    body = None
    header = None
    contract_type = None

    def __init__(self, headers, body, contract_type):
        if not self.digest:
            self.digest = hmac.new(
                str(datetime.now()),
                (str(headers) + str(body))
            ).hexdigest()
        self.body = body
        self.headers = headers
        self.contract_type = contract_type

    def dump(self):
        """Create a payload from the Contract attributes.
        """
        payload = [
            self.contract_type,
            self.digest,
            self.headers,
            self.body
        ]
        return payload

    @staticmethod
    def receive(msgpack_string, contract_digest=None):
        """Unpack a msgpack string into the appropriate Contract type.
        If `contract_digest` is set, only returns the Response/Failure
        if its digest matches the `contract_digest`, and returns False if it
        doesn't.
        """
        payload = msgpack.unpackb(msgpack_string)
        if payload[0] == Contract.CONTRACT_REQUEST:
            contract = Request.load(payload)
        elif payload[0] == Contract.CONTRACT_RESPONSE:
            contract = Response.load(payload)
        elif payload[0] == Contract.CONTRACT_FAILURE:
            contract = Failure.load(payload)

        if contract_digest is not None and not isinstance(contract, Request):
            if contract.request_digest == contract_digest:
                return contract
            else:
                return False

        return contract

    @staticmethod
    def send(contract):
        """Pack a contract into a msgpack string.
        """
        return msgpack.packb(contract.dump())


class Request(Contract):
    """A Request is a Contract type which is created with a string in its
    header called `func`, and the associated `args` and `kwargs`.

    `func` is the name of function to fulfill the Request, to which
    `args` and `kwargs` are unpacked, and then called.
    """

    def __init__(self, func, *args, **kwargs):
        self.digest = kwargs.pop('digest', None)
        super(Request, self).__init__(
            {'func': func},
            {'args': args, 'kwargs': kwargs},
            Contract.CONTRACT_REQUEST
        )

    @property
    def func(self):
        """Name of the function to fulfill this Request
        """
        return self.headers['func']

    @property
    def args(self):
        """Function args
        """
        return self.body['args']

    @property
    def kwargs(self):
        """Function kwargs
        """
        return self.body['kwargs']

    @classmethod
    def load(cls, payload):
        """Return a new Request object from a payload.
        """
        digest = payload[1]
        func = payload[2]['func']
        args = payload[3]['args']
        kwargs = payload[3]['kwargs']

        request = cls(
            func,
            digest=digest,
            *args,
            **kwargs
        )

        return request


class Response(Contract):
    """A Response is the fulfillment of a Request, returned by the function
    which fulfilled the Request. It is created with a `request_digest`,
    which is the digest of the Request it is fulfilling, and `body`, which
    contains the respnse body.
    """

    def __init__(self, request_digest, body):
        super(Response, self).__init__(
            {'request_digest': request_digest},
            body,
            Contract.CONTRACT_RESPONSE
        )

    @property
    def request_digest(self):
        return self.headers['request_digest']

    def get(self):
        """Return the response body
        """
        return self.body

    @classmethod
    def load(cls, payload):
        """Return a new Response object from a payload.
        """
        request_digest = payload[2]['request_digest']
        body = payload[3]

        response = cls(
            request_digest,
            body
        )

        return response


class Failure(Contract):
    """A Failure is a Contract that cannot be fulfilled, returned by the
    function that was supposed to fulfill it, or elsewhere. It is created
    with a `request_digest` which is the digest of the Request it was
    supposed to fulfill, a `failure_code`, and a `failure_message`.
    """

    FAILURE_NOHANDLER = 0
    FAILURE_EXCEPTION = 1

    def __init__(self, request_digest, failure_code=None,
                 failure_message=None):
        if not failure_code:
            failure_code = self.FAILURE_EXCEPTION
        super(Failure, self).__init__(
            {'request_digest': request_digest},
            {'failure_code': failure_code, 'failure_message': failure_message},
            Contract.CONTRACT_FAILURE
        )

    @property
    def request_digest(self):
        return self.headers['request_digest']

    def get(self):
        """Return the `failure_code` and `failure_message`
        """
        return {
            'failure_code': self.body['failure_code'],
            'failure_message': self.body['failure_message']
        }

    @classmethod
    def load(cls, payload):
        """Return a new Failure object from a payload.
        """
        request_digest = payload[2]['request_digest']
        failure_code = payload[3]['failure_code']
        failure_message = payload[3]['failure_message']

        failure = cls(
            request_digest,
            failure_code,
            failure_message
        )

        return failure
