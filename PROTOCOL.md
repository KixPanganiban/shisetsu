# The Shisetsu Protocol

**Last Updated**: v0.1.3 (11/16/2016)

The Shisetsu protocol revolves around an object called [Contract](shisetsu/contract.py). Every request and response (or failure) is a subclass of `Contract`, and is what gets passed through the Redis channel, serialized as msgpack.

## 1. Contract Structure

A `Contract` is first converted into a `list` before being serialized to msgpack. The `list` looks like this:

```
[0:<contract_type:int>, 1:<digest:string>, 2:<headers:dict>, 3:<body:mixed>]
```

- `contract_type` specifies whether the `Contract` is a `Request` (`0`), a `Response` (`1`), or a `Failure` (`-1`).
- `digest` is the identifier of the `Request`, and also identifies the channel to which the `Response` or `Failure` is sent. It is generated using the HMAC module with the current datetime string as key, and a concatenation of the string-casted `headers` and `body`.
- `headers` is a dict, and in a `Request` contains a key `func` which identifies the function name of the remote function to fulfill it. In `Response` and `Failure`, the `headers` contains a key `request_digest` which is the `digest` of the `Request` it is fulfilling/failing.
- `body` is a variable containing the return object of the function called, or in the case of `Failure`, contains a dict with `failure_code` and `failure_message`.

## 2. Request<->Response Cycle

1. A [Client](shisetsu/client.py) creates a `Request`
  - serializes the `Request` into msgpack message
  - subscribes to the `<receive>` channel (where `<receive>` is the `digest` of the created `Request`)
  - sends the message to channel where the `Server` is listening
  - waits for a response on the `<receive>` channel
2. A [Server](shisetsu/server.py) receives the message
  - deserializes it into a `Request` object from msgpack
  - looks for a function corresponding to the `Request`'s `headers` (aliased as `func`)
    - if found: runs that function, passing the arguments from the `Request`'s `body` (`body[0]` is `args`, `body[1]` is `kwargs`), and returns a `Response`
    - if not found, returns a `FAILURE_NOHANDLER` type `Failure`
  - `Response` is serialized into a msgpack message and passed back into the `<receive>` channel
3. The waiting `Client` receives the message
  - deserializes it from msgpack into the appropriate type
    - unsubscribe rom the `<receive>` channel
    - if `Response`: returns the response body
    - if `Failure`:
      - if `raise_on_failure` is set to `True` (default), raises a `ResponseFailure` exception with the `Failure`'s body as message
      - otherwise, returns the `Failure`'s body to the caller
---

Want to contribute to the protocol? Submit a [pull request](https://github.com/kixpanganiban/shisetsu/pulls/) or file an [issue](https://github.com/kixpanganiban/shisetsu/issues/).
