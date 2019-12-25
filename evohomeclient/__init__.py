"""evohomeclient2 provides a client for the oiginal Evohome API.

Further information at: https://evohome-client.readthedocs.io
"""
import codecs
import json
import logging
import time
import sys

import requests

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client

# Are we are dealing with Python 2 or 3
_VER = sys.version_info
#: Python 2.x?
IS_PY2 = (_VER[0] == 2)
#: Python 3.x?
IS_PY3 = (_VER[0] == 3)

logging.basicConfig()
_LOGGER = logging.getLogger(__name__)


class EvohomeClient(object):  # pylint: disable=useless-object-inheritance
    """Provides a client to access the Honeywell Evohome system"""
    # pylint: disable=too-many-instance-attributes,too-many-arguments

    def __init__(self, username, password, debug=False, user_data=None,
                 hostname="https://tccna.honeywell.com"):
        """Constructor. Takes the username and password for the service.

        If user_data is given then this will be used to try and reduce
        the number of calls to the authentication service which is known
        to be rate limited.
        """
        if debug is True:
            _LOGGER.setLevel(logging.DEBUG)
            _LOGGER.debug("Debug mode is explicitly enabled.")

            requests_logger = logging.getLogger("requests.packages.urllib3")
            requests_logger.setLevel(logging.DEBUG)
            requests_logger.propagate = True

            http_client.HTTPConnection.debuglevel = 1
        else:
            _LOGGER.debug(
                "Debug mode is not explicitly enabled "
                "(but may be enabled elsewhere)."
            )

        self.username = username
        self.password = password

        self.user_data = user_data
        self.hostname = hostname

        self.full_data = None
        self.gateway_data = None
        self.reader = codecs.getdecoder("utf-8")

        self.location_id = ""
        self.devices = {}
        self.named_devices = {}
        self.postdata = {}
        self.headers = {}

    def _convert(self, content):
        return json.loads(self.reader(content)[0])

    def _populate_full_data(self, force_refresh=False):
        if self.full_data is None or force_refresh:
            self._populate_user_info()

            user_id = self.user_data['userInfo']['userID']
            session_id = self.user_data['sessionId']

            url = (self.hostname + "/WebAPI/api/locations"
                   "?userId=%s&allData=True" % user_id)
            self.headers['sessionId'] = session_id

            response = self._do_request('get', url, json.dumps(self.postdata))

            self.full_data = self._convert(response.content)[0]

            self.location_id = self.full_data['locationID']

            self.devices = {}
            self.named_devices = {}

            for device in self.full_data['devices']:
                self.devices[device['deviceID']] = device
                self.named_devices[device['name']] = device

    def _populate_user_info(self):
        if self.user_data is None:
            url = self.hostname + "/WebAPI/api/Session"
            self.postdata = {'Username': self.username,
                             'Password': self.password,
                             'ApplicationId': '91db1612-73fd-4500-91b2-e63b069b185c'}
            self.headers = {'content-type': 'application/json'}

            response = self._do_request(
                'post', url, data=json.dumps(self.postdata), retry=False)

            self.user_data = self._convert(response.content)

        return self.user_data

    def temperatures(self, force_refresh=False):
        """Retrieve the current details for each zone. Returns a generator."""
        self._populate_full_data(force_refresh)
        for device in self.full_data['devices']:
            set_point = 0
            status = ""
            if 'heatSetpoint' in device['thermostat']['changeableValues']:
                set_point = float(
                    device['thermostat']['changeableValues']["heatSetpoint"]["value"])
                status = device['thermostat']['changeableValues']["heatSetpoint"]["status"]
            else:
                status = device['thermostat']['changeableValues']['status']
            yield {'thermostat': device['thermostatModelType'],
                   'id': device['deviceID'],
                   'name': device['name'],
                   'temp': float(device['thermostat']['indoorTemperature']),
                   'setpoint': set_point,
                   'status': status,
                   'mode': device['thermostat']['changeableValues']['mode']}

    def get_modes(self, zone):
        """Returns the set of modes the device can be assigned."""
        self._populate_full_data()
        device = self._get_device(zone)
        return device['thermostat']['allowedModes']

    def _get_device(self, zone):
        if isinstance(zone, str) or (IS_PY2 and isinstance(zone, basestring)):   # noqa: F821; pylint: disable=undefined-variable
            device = self.named_devices[zone]
        else:
            device = self.devices[zone]
        return device

    def _get_task_status(self, task_id):
        self._populate_full_data()
        url = (self.hostname + "/WebAPI/api/commTasks"
               "?commTaskId=%s" % task_id)

        response = self._do_request('get', url)

        return self._convert(response.content)['state']

    def _get_task_id(self, response):
        ret = self._convert(response.content)

        if isinstance(ret, list):
            task_id = ret[0]['id']
        else:
            task_id = ret['id']
        return task_id

    def _do_request(self, method, url, data=None, retry=True):
        if method == 'get':
            func = requests.get
        elif method == 'put':
            func = requests.put
        elif method == 'post':
            func = requests.post

        response = func(url, data=data, headers=self.headers)

        # catch 401/unauthorized since we may retry
        if response.status_code == requests.codes.unauthorized and retry:        # pylint: disable=no-member
            # Attempt to refresh sessionId if it has expired
            if 'code' in response.text:  # don't use response.json() here!
                if response.json()[0]['code'] == "Unauthorized":
                    _LOGGER.debug("Session expired, re-authenticating...")
                    # Get a new sessionId
                    self.user_data = None
                    self._populate_user_info()
                    # Set headers with new sessionId
                    session_id = self.user_data['sessionId']
                    self.headers['sessionId'] = session_id
                    _LOGGER.debug("sessionId = %s", session_id)

                    response = func(url, data=data, headers=self.headers)

        # display error message if the vendor provided one
        if response.status_code != requests.codes.ok:                            # pylint: disable=no-member
            if 'code' in response.text:  # don't use response.json()!
                message = ("HTTP Status = " + str(response.status_code) +
                           ", Response = " + response.text)
                raise requests.HTTPError(message)

        response.raise_for_status()

        return response

    def _set_status(self, status, until=None):
        self._populate_full_data()
        url = (self.hostname + "/WebAPI/api/evoTouchSystems"
               "?locationId=%s" % self.location_id)

        if until is None:
            data = {"QuickAction": status, "QuickActionNextTime": None}
        else:
            data = {
                "QuickAction": status,
                "QuickActionNextTime": until.strftime('%Y-%m-%dT%H:%M:%SZ')
            }

        response = self._do_request('put', url, json.dumps(data))

        task_id = self._get_task_id(response)

        while self._get_task_status(task_id) != 'Succeeded':
            time.sleep(1)

    def set_status_normal(self):
        """Sets the system to normal operation."""
        self._set_status('Auto')

    def set_status_custom(self, until=None):
        """Sets the system to the custom programme."""
        self._set_status('Custom', until)

    def set_status_eco(self, until=None):
        """Sets the system to the eco mode."""
        self._set_status('AutoWithEco', until)

    def set_status_away(self, until=None):
        """Sets the system to the away mode."""
        self._set_status('Away', until)

    def set_status_dayoff(self, until=None):
        """Sets the system to the day off mode."""
        self._set_status('DayOff', until)

    def set_status_heatingoff(self, until=None):
        """Sets the system to the heating off mode."""
        self._set_status('HeatingOff', until)

    def _get_device_id(self, zone):
        device = self._get_device(zone)
        return device['deviceID']

    def _set_heat_setpoint(self, zone, data):
        self._populate_full_data()

        device_id = self._get_device_id(zone)

        url = (self.hostname + "/WebAPI/api/devices"
               "/%s/thermostat/changeableValues/heatSetpoint" % device_id)

        response = self._do_request('put', url, json.dumps(data))

        task_id = self._get_task_id(response)

        while self._get_task_status(task_id) != 'Succeeded':
            time.sleep(1)

    def set_temperature(self, zone, temperature, until=None):
        """Sets the temperature of the given zone."""
        if until is None:
            data = {"Value": temperature, "Status": "Hold", "NextTime": None}
        else:
            data = {"Value": temperature,
                    "Status": "Temporary",
                    "NextTime": until.strftime('%Y-%m-%dT%H:%M:%SZ')}

        self._set_heat_setpoint(zone, data)

    def cancel_temp_override(self, zone):
        """Removes an existing temperature override."""
        data = {"Value": None, "Status": "Scheduled", "NextTime": None}
        self._set_heat_setpoint(zone, data)

    def _get_dhw_zone(self):
        for device in self.full_data['devices']:
            if device['thermostatModelType'] == 'DOMESTIC_HOT_WATER':
                return device['deviceID']
        return None

    def _set_dhw(self, status="Scheduled", mode=None, next_time=None):
        """Set DHW to On, Off or Auto, either indefinitely, or until a
        specified time.
        """
        data = {"Status": status,
                "Mode": mode,
                "NextTime": next_time,
                "SpecialModes": None,
                "HeatSetpoint": None,
                "CoolSetpoint": None}

        self._populate_full_data()
        dhw_zone = self._get_dhw_zone()
        if dhw_zone is None:
            raise Exception('No DHW zone reported from API')
        url = (self.hostname + "/WebAPI/api/devices"
               "/%s/thermostat/changeableValues" % dhw_zone)

        response = self._do_request('put', url, json.dumps(data))

        task_id = self._get_task_id(response)

        while self._get_task_status(task_id) != 'Succeeded':
            time.sleep(1)

    def set_dhw_on(self, until=None):
        """Set DHW to on, either indefinitely, or until a specified time.

        When On, the DHW controller will work to keep its target temperature
        at/above its target temperature.  After the specified time, it will
        revert to its scheduled behaviour.
        """

        time_until = None if until is None else until.strftime(
            '%Y-%m-%dT%H:%M:%SZ')

        self._set_dhw(status="Hold", mode="DHWOn", next_time=time_until)

    def set_dhw_off(self, until=None):
        """Set DHW to on, either indefinitely, or until a specified time.

        When Off, the DHW controller will ignore its target temperature. After
        the specified time, it will revert to its scheduled behaviour.
        """

        time_until = None if until is None else until.strftime(
            '%Y-%m-%dT%H:%M:%SZ')

        self._set_dhw(status="Hold", mode="DHWOff", next_time=time_until)

    def set_dhw_auto(self):
        """Set DHW to On or Off, according to its schedule."""
        self._set_dhw(status="Scheduled")
