"""
shisetsu.logger
<github.com/kixpanganiban>

Contains `Logger`.
"""
import logging


class Logger(object):
    """A thin wrapper around the `logging` module to make it easier to set up
    and share logger configuration.
    """

    def __init__(self, name, level=logging.INFO):
        self.instance = logging.getLogger(name)
        basic_formatter = logging.Formatter(logging.BASIC_FORMAT)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(basic_formatter)
        self.instance.addHandler(stream_handler)
        self.instance.setLevel(level)

    def get(self):
        """Return the logger instance bound to this.
        """
        return self.instance

