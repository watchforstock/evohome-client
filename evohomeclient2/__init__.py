from __future__ import print_function
from datetime import datetime, timedelta
import requests

from .location import Location
from .base import EvohomeBase

HEADER_ACCEPT = ("application/json, application/xml, text/json, text/x-json, "
                 "text/javascript, text/xml")
HEADER_AUTHORIZATION_BASIC = (
    "Basic "
    "NGEyMzEwODktZDJiNi00MWJkLWE1ZWItMTZhMGE0MjJiOTk5OjFhMTVjZGI4LTQyZGUtNDA3Y"
    "i1hZGQwLTA1OWY5MmM1MzBjYg=="
)


class EvohomeClient(EvohomeBase):
    def __init__(self, username, password, debug=False, access_token=None,
                 access_token_expires=None):
        super(EvohomeClient, self).__init__(debug)

        self.username = username
        self.password = password

        self.access_token = access_token
        self.access_token_expires = access_token_expires
        self.refresh_token = None

        self.account_info = None
        self.system_id = None
        self.locations = None
        self.installation_info = None

        self._login()

    def _get_location(self, location):
        if location is None:
            return self.installation_info[0]['locationInfo']['locationId']
        return location

    def _get_single_heating_system(self):
        # This allows a shortcut for some systems
        location = None
        gateway = None
        control_system = None

        if len(self.locations) == 1:
            location = self.locations[0]
        else:
            raise Exception("More than one location available")

        if len(location._gateways) == 1:                                         # pylint: disable=protected-access
            gateway = location._gateways[0]                                      # pylint: disable=protected-access
        else:
            raise Exception("More than one gateway available")

        if len(gateway._control_systems) == 1:                                   # pylint: disable=protected-access
            control_system = gateway._control_systems[0]                         # pylint: disable=protected-access
        else:
            raise Exception("More than one control system available")

        return control_system

    def _basic_login(self):
        self.access_token = None
        self.access_token_expires = None

        url = 'https://tccna.honeywell.com/Auth/OAuth/Token'
        headers = {
            'Authorization': HEADER_AUTHORIZATION_BASIC,
            'Accept': HEADER_ACCEPT
        }
        data = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'Host': 'rs.alarmnet.com/',
            'Cache-Control': 'no-store no-cache',
            'Pragma': 'no-cache',
            'grant_type': 'password',
            'scope': 'EMEA-V1-Basic EMEA-V1-Anonymous EMEA-V1-Get-Current-User-Account',
            'Username': self.username,
            'Password': self.password,
            'Connection': 'Keep-Alive'
        }

        response = requests.post(url, data=data, headers=headers)
        if response.status_code != requests.codes.ok:                            # pylint: disable=no-member
            response.raise_for_status()

        data = self._convert(response.text)

        self.refresh_token = data['refresh_token']
        self.access_token = data['access_token']
        self.access_token_expires = (datetime.now() +
                                     timedelta(seconds=data['expires_in']))

    def _login(self):
        self.user_account()
        self.installation()

    def headers(self):
        if self.access_token is None or self.access_token_expires is None:
            # token is invalid
            self._basic_login()
        elif datetime.now() > self.access_token_expires - timedelta(seconds=30):
            # token has expired
            self._basic_login()

        return {'Accept': HEADER_ACCEPT,
                'Authorization': 'bearer ' + self.access_token}

    def user_account(self):
        self.account_info = None

        url = 'https://tccna.honeywell.com/WebAPI/emea/api/v1/userAccount'

        response = requests.get(url, headers=self.headers())
        if response.status_code != requests.codes.ok:                            # pylint: disable=no-member
            response.raise_for_status()

        self.account_info = self._convert(response.text)
        return self.account_info

    def installation(self):
        self.locations = []

        url = ("https://tccna.honeywell.com/WebAPI/emea/api/v1/location"
               "/installationInfo?userId=%s"
               "&includeTemperatureControlSystems=True"
               % self.account_info['userId'])

        response = requests.get(url, headers=self.headers())
        if response.status_code != requests.codes.ok:                            # pylint: disable=no-member
            response.raise_for_status()

        self.installation_info = self._convert(response.text)
        self.system_id = self.installation_info[0]['gateways'][0]['temperatureControlSystems'][0]['systemId']

        for loc_data in self.installation_info:
            self.locations.append(Location(self, loc_data))

        return self.installation_info

    def full_installation(self, location=None):
        url = ("https://tccna.honeywell.com/WebAPI/emea/api/v1/location"
               "/%s/installationInfo?includeTemperatureControlSystems=True"
               % self._get_location(location))

        response = requests.get(url, headers=self.headers())
        if response.status_code != requests.codes.ok:                            # pylint: disable=no-member
            response.raise_for_status()

        return self._convert(response.text)

    def gateway(self):
        url = 'https://tccna.honeywell.com/WebAPI/emea/api/v1/gateway'

        response = requests.get(url, headers=self.headers())
        if response.status_code != requests.codes.ok:                            # pylint: disable=no-member
            response.raise_for_status()

        return self._convert(response.text)

    def set_status_normal(self):
        return self._get_single_heating_system().set_status_normal()

    def set_status_reset(self):
        return self._get_single_heating_system().set_status_reset()

    def set_status_custom(self, until=None):
        return self._get_single_heating_system().set_status_custom(until)

    def set_status_eco(self, until=None):
        return self._get_single_heating_system().set_status_eco(until)

    def set_status_away(self, until=None):
        return self._get_single_heating_system().set_status_away(until)

    def set_status_dayoff(self, until=None):
        return self._get_single_heating_system().set_status_dayoff(until)

    def set_status_heatingoff(self, until=None):
        return self._get_single_heating_system().set_status_heatingoff(until)

    def temperatures(self):
        return self._get_single_heating_system().temperatures()

    def zone_schedules_backup(self, filename):
        return self._get_single_heating_system().zone_schedules_backup(filename)  # noqa: E501;  pylint: line-to-long

    def zone_schedules_restore(self, filename):
        return self._get_single_heating_system().zone_schedules_restore(filename)  # noqa: E501;  pylint: line-to-long
