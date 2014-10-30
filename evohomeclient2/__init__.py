from __future__ import print_function
import requests
import json
import codecs

class EvohomeClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.reader = codecs.getdecoder("utf-8")
        self.access_token = None

    def _convert(self, object):
        return json.loads(self.reader(object)[0])

    def _get_location(self, location):
        if location is None:
            return self.installation_info[0]['locationInfo']['locationId']
        else:
            return location

    def login(self):
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
        r = requests.put('/TotalConnectComfort/WebAPI/emea/api/v1/temperatureZone/%s/schedule' % zone, data=zone_info, headers=self.headers)
        return self._convert(r.text)
