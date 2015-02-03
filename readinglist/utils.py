try:
    import simplejson as json
except ImportError:  # pragma: no cover
    import json  # NOQA

import ast
import os
import time
from binascii import hexlify

from colander import null


# removes whitespace, newlines, and tabs from the beginning/end of a string
strip_whitespace = lambda v: v.strip(' \t\n\r') if v is not null else v

msec_time = lambda: int(time.time() * 1000.0)  # floor

# Get a classname from a class.
classname = lambda c: c.__class__.__name__.lower()


def random_bytes_hex(bytes_length):
    """Return a hexstring of bytes_length cryptographic-friendly random bytes.

    """
    return hexlify(os.urandom(bytes_length)).decode('utf-8')


def native_value(value):
    """Convert string value to native python values."""
    if value.lower() in ['on', 'true', 'yes', '1']:
        value = True
    elif value.lower() in ['off', 'false', 'no', '0']:
        value = False
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value


def Enum(**enums):
    return type('Enum', (), enums)


COMPARISON = Enum(
    LT='<',
    MIN='>=',
    MAX='<=',
    NOT='!=',
    EQ='==',
    GT='>',
)