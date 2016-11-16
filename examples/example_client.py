"""
Example usage of the CallableClient class.
"""
from shisetsu.client import CallableClient

def main():
    """ Call `clock` on the time sever
    """
    client = CallableClient('time')
    print client.clock()

if __name__ == '__main__':
    main()
