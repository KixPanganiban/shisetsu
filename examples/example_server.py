"""
Example usage of the Server class.
"""
import time

from shisetsu.server import Server

def main():
    """ Start a server on the 'time' Redis channel bound to the time class
    """
    server = Server('time', time)
    server.run()

if __name__ == '__main__':
    main()
