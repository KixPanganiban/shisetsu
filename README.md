# Shisetsu
Shisetsu is an RPC-like protocol on top of Redis that aims to be as simple and easy to use as possible while maintaining extensibility and configurability. The primary goal of Shisetsu is to be easy to implement in other languages without having to dive into the nitty gritty of channels, socket programming, serialization, et cetera (though of course, there's no stopping you) -- all you need is [msgpack](https://github.com/msgpack) and [Redis](http://redis.io/) (with PubSub) support.

This is the Python implementation of Shisetsu. Both this implementation and the protocol itself are still in beta, and should **not** be used in production due to lack of security features. Right now, this serves more as a proof-of-concept than anything else.

# Quick Start

1. Install Redis and start the Redis server
2. Clone Shisetsu, install requirements with `pip install -r requirements.txt`
3. Open up a Python terminal

To start a Shisetsu Server:
```python
from shisetsu.server import Server
import time

# Create a Server on the 'time' Redis channel bound to the time module
s = Server('time', time)
s.run()
```

To call `time.clock()` on the server:
```python
from shisetsu.client import Client

# Send requests to the 'time' Redis channel
c = Client('time')
c.call('clock')
```
or, alternatively
```python
from shisetsu.client import CallableClient

c = CallableClient('time')
c.clock()
```

# Protocol Specs

See [PROTOCOL.md](PROTOCOL.md).

# Future Plans (soon)

- [ ] Client Timeout
- [ ] Middlewares
- [ ] Tests
- [ ] Release on PyPi
- [ ] Authorization/authentication support
- [ ] Async (Python 3 `async`/`await`?)
- [ ] [Request more](https://github.com/KixPanganiban/shisetsu/issues/)

# Future Plans (far future)

- [ ] Implementations in other languages\*
- [ ] Performance optimizations
- [ ] Other brokers beside Redis

> \*I can probably implement JavaScript (NodeJS), Elixir, and PHP versions myself.

# Contributing

If there's anything listed (or not listed) above that you wish to implement, or if you wish to submit an improvement or fix, feel free to send a [pull request](https://github.com/KixPanganiban/shisetsu/pulls/). Please follow [Git Flow](https://guides.github.com/introduction/flow/).

# License

See [LICENSE](LICENSE).
