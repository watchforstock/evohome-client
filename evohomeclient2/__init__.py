from __future__ import print_function
import requests
import json
import codecs

import logging
logging.basicConfig()
requests_log = logging.getLogger("requests.packages.urllib3")

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client


class EvohomeClientInvalidPostData(Exception):
    pass


class EvohomeClient:
    def __init__(self, username, password, debug=False):

        if debug:
            http_client.HTTPConnection.debuglevel = 1
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True
        else:
            http_client.HTTPConnection.debuglevel = 0
            logging.getLogger().setLevel(logging.INFO)
            requests_log.setLevel(logging.INFO)
            requests_log.propagate = False

        self.username = username
        self.password = password
        self.reader = codecs.getdecoder("utf-8")
        self.access_token = None

        self._login()

    def _convert(self, object):
        return json.loads(self.reader(object)[0])

    def _get_location(self, location):
        if location is None:
            return self.installation_info[0]['locationInfo']['locationId']
        else:
            return location

    def _login(self):
        url = 'https://rs.alarmnet.com:443/TotalConnectComfort/Auth/OAuth/Token'
        headers = {
            'Authorization':	'Basic YjAxM2FhMjYtOTcyNC00ZGJkLTg4OTctMDQ4YjlhYWRhMjQ5OnRlc3Q=',
            'Accept': 'application/json, application/xml, text/json, text/x-json, text/javascript, text/xml'

        }
        data = {
            'Content-Type':	'application/x-www-form-urlencoded; charset=utf-8',
            'Host':	'rs.alarmnet.com/',
            'Cache-Control':'no-store no-cache',
            'Pragma':	'no-cache',
            'grant_type':	'password',
            'scope':	'EMEA-V1-Basic EMEA-V1-Anonymous EMEA-V1-Get-Current-User-Account',
            'Username':	self.username,
            'Password':	self.password,
            'Connection':	'Keep-Alive'
        }
        r = requests.post(url, data=data, headers=headers)
        self.access_token = self._convert(r.text)['access_token']
        self.headers = {
            'Authorization': 'bearer ' + self.access_token,
            'applicationId': 'b013aa26-9724-4dbd-8897-048b9aada249',
            'Accept': 'application/json, application/xml, text/json, text/x-json, text/javascript, text/xml'
        }
        self.user_account()
        self.installation()


    def user_account(self):
        r = requests.get('https://rs.alarmnet.com:443/TotalConnectComfort/WebAPI/emea/api/v1/userAccount', headers=self.headers)

        self.account_info = self._convert(r.text)
        return self.account_info

    def installation(self):
        r = requests.get('https://rs.alarmnet.com:443/TotalConnectComfort/WebAPI/emea/api/v1/location/installationInfo?userId=%s&includeTemperatureControlSystems=True' % self.account_info['userId'], headers=self.headers)

        self.installation_info = self._convert(r.text)
        self.system_id = self.installation_info[0]['gateways'][0]['temperatureControlSystems'][0]['systemId']

        return self.installation_info

    def full_installation(self, location=None):
        location = self._get_location(location)
        r = requests.get('https://rs.alarmnet.com:443/TotalConnectComfort/WebAPI/emea/api/v1/location/%s/installationInfo?includeTemperatureControlSystems=True' % location, headers=self.headers)
        return self._convert(r.text)

    def get_simple_zones(self, location=None):
        info = self.full_installation(location)
        zones = info['gateways'][0]['temperatureControlSystems'][0]['zones']

        return zones

    def gateway(self):
        r = requests.get('https://rs.alarmnet.com:443/TotalConnectComfort/WebAPI/emea/api/v1/gateway', headers=self.headers)
        return self._convert(r.text)

    def status(self, location=None):
        location = self._get_location(location)
        r = requests.get('https://rs.alarmnet.com:443/TotalConnectComfort/WebAPI/emea/api/v1/location/%s/status?includeTemperatureControlSystems=True' % location, headers=self.headers)
        return self._convert(r.text)

    def zone_schedule(self, zone):
        r = requests.get('https://rs.alarmnet.com:443/TotalConnectComfort/WebAPI/emea/api/v1/temperatureZone/%s/schedule' % zone, headers=self.headers)
        return self._convert(r.text)

    def set_zone_schedule(self, zone, zone_info):
        # must only POST json, otherwise server API handler raises exceptions
        try:
            t1 = json.loads(zone_info)
        except:
            raise EvohomeClientInvalidPostData('zone_info must be JSON')

        headers = dict(self.headers)
        headers['Content-Type'] = 'application/json'

        r = requests.put('https://rs.alarmnet.com:443/TotalConnectComfort/WebAPI/emea/api/v1/temperatureZone/%s/schedule' % zone, data=zone_info, headers=headers)
        return self._convert(r.text)

    def temperatures(self, location=None):
        status = self.status(location)

        if 'dhw' in status['gateways'][0]['temperatureControlSystems'][0]:
            dhw = status['gateways'][0]['temperatureControlSystems'][0]['dhw']
            yield {'thermostat': 'DOMESTIC_HOT_WATER',
                    'id': dhw['dhwId'],
                    'name': '',
                    'temp': dhw['temperatureStatus']['temperature']}

        for zone in status['gateways'][0]['temperatureControlSystems'][0]['zones']:
            yield {'thermostat': 'EMEA_ZONE',
                    'id': zone['zoneId'],
                    'name': zone['name'],
                    'temp': zone['temperatureStatus']['temperature']}

    def _set_status(self, mode, until=None):

        headers = dict(self.headers)
        headers['Content-Type'] = 'application/json'

        if until is None:
            data = {"SystemMode":mode,"TimeUntil":None,"Permanent":True}
        else:
            data = {"SystemMode":mode,"TimeUntil":"%sT00:00:00Z" % until.strftime('%Y-%m-%d'),"Permanent":False}
        r = requests.put('https://rs.alarmnet.com:443/TotalConnectComfort/WebAPI/emea/api/v1/temperatureControlSystem/%s/mode' % self.system_id, data=json.dumps(data), headers=headers)

    def set_status_normal(self):
        self._set_status(0)

    def set_status_custom(self, until=None):
        self._set_status(6, until)

    def set_status_eco(self, until=None):
        self._set_status(2, until)

    def set_status_away(self, until=None):
        self._set_status(3, until)

    def set_status_dayoff(self, until=None):
        self._set_status(4, until)

    def set_status_heatingoff(self, until=None):
        self._set_status(1, until)

    def _get_dhw_zone(self):
        status = self.status(location)
        return status['gateways'][0]['temperatureControlSystems'][0]['dhw']['dhwId']

    def _set_dhw(self, data):
        headers = dict(self.headers)
        headers['Content-Type'] = 'application/json'
        url = 'https://rs.alarmnet.com/TotalConnectComfort/WebAPI/emea/api/v1/domesticHotWater/%s/state' % self._get_dhw_zone()

        response = requests.put(url, data=json.dumps(data), headers=headers)


    def set_dhw_on(self, until=None):
        if until is None:
            data = {"State":1,"Mode":1,"UntilTime":None}
        else:
            data = {"State":1,"Mode":2,"UntilTime":until.strftime('%Y-%m-%dT%H:%M:%SZ')}
        self._set_dhw(data)

    def set_dhw_off(self, until=None):
        if until is None:
            data = {"State":0,"Mode":1,"UntilTime":None}
        else:
            data = {"State":0,"Mode":2,"UntilTime":until.strftime('%Y-%m-%dT%H:%M:%SZ')}
        self._set_dhw(data)

    def set_dhw_auto(self):
        data =  {"State":0,"Mode":0,"UntilTime":None}
        self._set_dhw(data)
