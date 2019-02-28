"""Provide base capability for evohomeclient"""
import json
import codecs
import logging

logging.basicConfig()
_LOGGER = logging.getLogger(__name__)
REQUESTS_LOGGER = logging.getLogger("requests.packages.urllib3")

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client


class EvohomeClientInvalidPostData(Exception):
    """Used when data has been incorrectly sent"""


class EvohomeBase(object):  # pylint: disable=too-few-public-methods
    """Base class for evohomeclient"""

    def __init__(self, debug=False):
        self.reader = codecs.getdecoder("utf-8")

        if debug is True:
            _LOGGER.setLevel(logging.DEBUG)
            _LOGGER.debug("__init__(): Debug mode is explicitly enabled.")
            REQUESTS_LOGGER.setLevel(logging.DEBUG)
            REQUESTS_LOGGER.propagate = True
            http_client.HTTPConnection.debuglevel = 1

    def _convert(self, obj):  # pylint: disable=no-self-use
        return json.loads(obj)
