from .bitly_api import Connection, BitlyError, Error
from .bitly_api_v4 import Connection as v4Connection
from .bitly_api_v4 import BitlyError as v4BitlyError
from .bitly_api_v4 import Error as v4Error

__version__ = '0.4'
__author__ = "Allen Dolph <allen@kleinerperkins.com>"
__all__ = ["Connection", "BitlyError", "Error", "v4Connection", "v4BitlyError", "v4Error"]
__doc__ = """
This is a python library for the bitly api

all methods raise BitlyError on an unexpected response, or a problem with input
format
"""