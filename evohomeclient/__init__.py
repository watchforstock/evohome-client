from __future__ import print_function

import codecs
import json
import logging
import time
import sys
import requests

logging.basicConfig()
REQUESTS_LOG = logging.getLogger("requests.packages.urllib3")

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client


# stole this from requests library. To determine whether we are dealing
# with Python 2 or 3
_VER = sys.version_info
#: Python 2.x?
IS_PY2 = (_VER[0] == 2)
#: Python 3.x?
IS_PY3 = (_VER[0] == 3)


class EvohomeClient:
    # pylint: disable=too-many-instance-attributes
    def __init__(self, username, password, debug=False, user_data=None):
        self.username = username
        self.password = password
        self.user_data = user_data
        self.full_data = None
        self.gateway_data = None
        self.reader = codecs.getdecoder("utf-8")

        self.location_id = None
        self.devices = None
        self.named_devices = None
        self.postdata = None
        self.headers = None

        if debug is True:
            http_client.HTTPConnection.debuglevel = 1
            logging.getLogger(__name__).setLevel(logging.DEBUG)
            REQUESTS_LOG.setLevel(logging.DEBUG)
            REQUESTS_LOG.propagate = True
        else:
            http_client.HTTPConnection.debuglevel = 0
            logging.getLogger(__name__).setLevel(logging.INFO)
            REQUESTS_LOG.setLevel(logging.INFO)
            REQUESTS_LOG.propagate = False

    def _convert(self, content):
        return json.loads(self.reader(content)[0])

    def _populate_full_data(self, force_refresh=False):
        if self.full_data is None or force_refresh:
            self._populate_user_info()

            try:
                user_id = self.user_data['userInfo']['userID']
                session_id = self.user_data['sessionId']
            except Exception as error:
                raise Exception('Invalid user_data: %s' % repr(self.user_data)) from error

            url = ("https://tccna.honeywell.com/WebAPI/api/locations"
                   "?userId=%s&allData=True" % user_id)
            self.headers['sessionId'] = session_id

            response = requests.get(url,
                                    data=json.dumps(self.postdata),
                                    headers=self.headers)

            self.full_data = self._convert(response.content)[0]

            try:
                self.location_id = self.full_data['locationID']

                self.devices = {}
                self.named_devices = {}

                for device in self.full_data['devices']:
                    self.devices[device['deviceID']] = device
                    self.named_devices[device['name']] = device

            except Exception as error:
                raise Exception('Invalid full_data: %s' % repr(self.full_data)) from error

    def _populate_gateway_info(self):
        self._populate_full_data()
        if self.gateway_data is None:
            url = ("https://tccna.honeywell.com/WebAPI/api/gateways"
                   "?locationId=%s&allData=False" % self.location_id)

            response = requests.get(url, headers=self.headers)

            self.gateway_data = self._convert(response.content)[0]

    def _populate_user_info(self):
        if self.user_data is None:
            url = "https://tccna.honeywell.com/WebAPI/api/Session"
            self.postdata = {'Username': self.username,
                             'Password': self.password,
                             'ApplicationId': '91db1612-73fd-4500-91b2-e63b069b185c'}
            self.headers = {'content-type': 'application/json'}

            response = requests.post(url,
                                     data=json.dumps(self.postdata),
                                     headers=self.headers)

            self.user_data = self._convert(response.content)

        return self.user_data

    def temperatures(self, force_refresh=False):
        self._populate_full_data(force_refresh)
        for device in self.full_data['devices']:
            set_point = 0
            if 'heatSetpoint' in device['thermostat']['changeableValues']:
                set_point = float(device['thermostat']['changeableValues']["heatSetpoint"]["value"])
            yield {'thermostat': device['thermostatModelType'],
                   'id': device['deviceID'],
                   'name': device['name'],
                   'temp': float(device['thermostat']['indoorTemperature']),
                   'setpoint': set_point}

    def get_modes(self, zone):
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
        url = ("https://tccna.honeywell.com/WebAPI/api/commTasks"
               "?commTaskId=%s" % task_id)

        response = requests.get(url, headers=self.headers)

        return self._convert(response.content)['state']

    def _get_task_id(self, response):
        ret = self._convert(response.content)

        if isinstance(ret, list):
            task_id = ret[0]['id']
        else:
            task_id = ret['id']
        return task_id

    def _set_status(self, status, until=None):
        self._populate_full_data()
        url = ("https://tccna.honeywell.com/WebAPI/api/evoTouchSystems"
               "?locationId=%s" % self.location_id)

        if until is None:
            data = {"QuickAction": status, "QuickActionNextTime": None}
        else:
            data = {"QuickAction": status, "QuickActionNextTime": "%sT00:00:00Z" % until.strftime('%Y-%m-%d')}

        response = requests.put(url,
                                data=json.dumps(data),
                                headers=self.headers)

        task_id = self._get_task_id(response)

        while self._get_task_status(task_id) != 'Succeeded':
            time.sleep(1)

    def set_status_normal(self):
        self._set_status('Auto')

    def set_status_custom(self, until=None):
        self._set_status('Custom', until)

    def set_status_eco(self, until=None):
        self._set_status('AutoWithEco', until)

    def set_status_away(self, until=None):
        self._set_status('Away', until)

    def set_status_dayoff(self, until=None):
        self._set_status('DayOff', until)

    def set_status_heatingoff(self, until=None):
        self._set_status('HeatingOff', until)

    def _get_device_id(self, zone):
        device = self._get_device(zone)
        return device['deviceID']

    def _set_heat_setpoint(self, zone, data):
        self._populate_full_data()

        device_id = self._get_device_id(zone)

        url = ("https://tccna.honeywell.com/WebAPI/api/devices"
               "/%s/thermostat/changeableValues/heatSetpoint" % device_id)

        response = requests.put(url, json.dumps(data), headers=self.headers)

        task_id = self._get_task_id(response)

        while self._get_task_status(task_id) != 'Succeeded':
            time.sleep(1)

    def set_temperature(self, zone, temperature, until=None):
        if until is None:
            data = {"Value": temperature, "Status": "Hold", "NextTime": None}
        else:
            data = {"Value": temperature,
                    "Status": "Temporary",
                    "NextTime": until.strftime('%Y-%m-%dT%H:%M:%SZ')}

        self._set_heat_setpoint(zone, data)

    def cancel_temp_override(self, zone):
        data = {"Value": None, "Status": "Scheduled", "NextTime": None}
        self._set_heat_setpoint(zone, data)

    def _get_dhw_zone(self):
        for device in self.full_data['devices']:
            if device['thermostatModelType'] == 'DOMESTIC_HOT_WATER':
                return device['deviceID']
        return None

    def _set_dhw(self, status="Scheduled", mode=None, next_time=None):
        data = {"Status": status,
                "Mode": mode,
                "NextTime": next_time,
                "SpecialModes": None,
                "HeatSetpoint": None,
                "CoolSetpoint": None}

        self._populate_full_data()
        url = ("https://tccna.honeywell.com/WebAPI/api/devices"
               "/%s/thermostat/changeableValues" % self._get_dhw_zone())

        response = requests.put(url,
                                data=json.dumps(data),
                                headers=self.headers)

        task_id = self._get_task_id(response)

        while self._get_task_status(task_id) != 'Succeeded':
            time.sleep(1)

    def set_dhw_on(self, until=None):
        timex = None if until is None else until.strftime('%Y-%m-%dT%H:%M:%SZ')

        self._set_dhw(status="Hold", mode="DHWOn", next_time=timex)

    def set_dhw_off(self, until=None):
        timex = None if until is None else until.strftime('%Y-%m-%dT%H:%M:%SZ')

        self._set_dhw(status="Hold", mode="DHWOff", next_time=timex)

    def set_dhw_auto(self):
        self._set_dhw(status="Scheduled")
