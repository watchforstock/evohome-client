"""Provide base capability for evohomeclient"""
import json
import codecs
import logging
logging.basicConfig()
REQUESTS_LOG = logging.getLogger("requests.packages.urllib3")

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

        if debug:
            http_client.HTTPConnection.debuglevel = 1
            logging.getLogger(__name__).setLevel(logging.DEBUG)
            REQUESTS_LOG.setLevel(logging.DEBUG)
            REQUESTS_LOG.propagate = True
        else:
            http_client.HTTPConnection.debuglevel = 0
            logging.getLogger(__name__).setLevel(logging.INFO)
            REQUESTS_LOG.setLevel(logging.INFO)
            REQUESTS_LOG.propagate = False

    def _convert(self, obj):  # pylint: disable=no-self-use
        return json.loads(obj)
