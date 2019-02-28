"""evohomeclient2 provides a client for the updated Evohome API.

   Further information at: https://evohome-client.readthedocs.io
   """
from __future__ import print_function
from datetime import datetime, timedelta
import logging
import requests

from .location import Location
from .base import EvohomeBase

logging.basicConfig()
_LOGGER = logging.getLogger(__name__)

HEADER_ACCEPT = (
    "application/json, application/xml, text/json, text/x-json, "
    "text/javascript, text/xml"
)
HEADER_AUTHORIZATION_BASIC = (
    "Basic "
    "NGEyMzEwODktZDJiNi00MWJkLWE1ZWItMTZhMGE0MjJiOTk5OjFhMTVjZGI4LTQyZGUtNDA3Y"
    "i1hZGQwLTA1OWY5MmM1MzBjYg=="
)
HEADER_BASIC_AUTH = {
    'Accept': HEADER_ACCEPT,
    'Authorization': HEADER_AUTHORIZATION_BASIC
}


class EvohomeClient(EvohomeBase):  # pylint: disable=too-many-instance-attributes
    """Provides access to the Evohome API."""

    # pylint: disable=too-many-arguments
    def __init__(self, username, password, debug=False, refresh_token=None,
                 access_token=None, access_token_expires=None):
        super(EvohomeClient, self).__init__(debug)

        if debug is not True:
            _LOGGER.debug("__init__(): Debug mode was not explicitly enabled.")

        self.username = username
        self.password = password

        self.refresh_token = refresh_token
        self.access_token = access_token
        self.access_token_expires = access_token_expires

        self.account_info = None
        self.locations = None
        self.installation_info = None
        self.system_id = None

        self._login()

    def _login(self):
        self.user_account()
        self.installation()

    def _headers(self):
        """Ensure the Authorization Header has a valid Access Token."""

        if self.access_token is None or self.access_token_expires is None:
            self._basic_login()

        elif datetime.now() > self.access_token_expires - timedelta(seconds=30):
            self._basic_login()

        return {'Accept': HEADER_ACCEPT,
                'Authorization': 'bearer ' + self.access_token}

    def _basic_login(self):
        """Obtain a (new) access token from the vendor.

        First, try using the refresh_token, if one is available, otherwise
        authenticate using the user credentials.
        """
        self.access_token = self.access_token_expires = None

        if self.refresh_token is not None:
            _LOGGER.debug("_basic_login(): Trying refresh_token...")
            credentials = {'grant_type': "refresh_token",
                           'scope': "EMEA-V1-Basic EMEA-V1-Anonymous",
                           'refresh_token': self.refresh_token}

            if not self._obtain_access_token(credentials):
                # invalid refresh_token, silently try username/password instead
                _LOGGER.warn("_basic_login(): Invalid refresh_token.")
                self.refresh_token = None

        if self.refresh_token is None:
            _LOGGER.debug("_basic_login(): Trying user credentials...")
            credentials = {'grant_type': "password",
                           'scope': "EMEA-V1-Basic EMEA-V1-Anonymous EMEA-V1-Get-Current-User-Account",
                           'Username': self.username,
                           'Password': self.password}

            if not self._obtain_access_token(credentials):
                raise ValueError("Bad Username/Password, unable to continue.")

    def _obtain_access_token(self, credentials):
        """Get an access token using the supplied credentials.

        Return False if this is not possible.
        """
        url = 'https://tccna.honeywell.com/Auth/OAuth/Token'
        payload = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'Host': 'rs.alarmnet.com/',
            'Cache-Control': 'no-store no-cache',
            'Pragma': 'no-cache',
            'Connection': 'Keep-Alive'
        }
        payload.update(credentials)  # merge the credentials into the payload

        response = requests.post(url, data=payload, headers=HEADER_BASIC_AUTH)

        if response.status_code == requests.codes.bad_request:                   # pylint: disable=no-member
            response_json = response.json()
            if 'error' in response_json:
                if response_json['error'] == 'invalid_grant':
                    return False
            raise requests.HTTPError(
                "Unable to obtain an Access Token: ", response_json)

        response.raise_for_status()

        try:  # validate the access token
            response_json = response.json()  # this may cause a ValueError

            # these may cause a KeyError
            self.access_token = response_json['access_token']
            self.access_token_expires = (
                datetime.now() + timedelta(seconds=response_json['expires_in']))
            self.refresh_token = response_json['refresh_token']

        except KeyError as error:
            raise KeyError("Unable to obtain an Access Token: ", error)

        except ValueError as error:
            raise ValueError("Unable to obtain an Access Token: ", error)

        return True

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

        if len(location._gateways) == 1:  # pylint: disable=protected-access
            gateway = location._gateways[0]  # pylint: disable=protected-access
        else:
            raise Exception("More than one gateway available")

        if len(gateway._control_systems) == 1:  # pylint: disable=protected-access
            control_system = gateway._control_systems[0]  # pylint: disable=protected-access
        else:
            raise Exception("More than one control system available")

        return control_system

    def user_account(self):
        """Return the user account information."""
        self.account_info = None

        url = 'https://tccna.honeywell.com/WebAPI/emea/api/v1/userAccount'

        response = requests.get(url, headers=self._headers())
        response.raise_for_status()

        self.account_info = response.json()
        return self.account_info

    def installation(self):
        """Return the details of the installation."""
        self.locations = []

        url = ("https://tccna.honeywell.com/WebAPI/emea/api/v1/location"
               "/installationInfo?userId=%s"
               "&includeTemperatureControlSystems=True"
               % self.account_info['userId'])

        response = requests.get(url, headers=self._headers())
        response.raise_for_status()

        self.installation_info = response.json()
        self.system_id = self.installation_info[0]['gateways'][0]['temperatureControlSystems'][0]['systemId']

        for loc_data in self.installation_info:
            self.locations.append(Location(self, loc_data))

        return self.installation_info

    def full_installation(self, location=None):
        """Return the full details of the installation."""
        url = ("https://tccna.honeywell.com/WebAPI/emea/api/v1/location"
               "/%s/installationInfo?includeTemperatureControlSystems=True"
               % self._get_location(location))

        response = requests.get(url, headers=self._headers())
        response.raise_for_status()

        return response.json()

    def gateway(self):
        """Return the detail of the gateway."""
        url = 'https://tccna.honeywell.com/WebAPI/emea/api/v1/gateway'

        response = requests.get(url, headers=self._headers())
        response.raise_for_status()

        return response.json()

    def set_status_normal(self):
        """Set the system into normal heating mode."""
        return self._get_single_heating_system().set_status_normal()

    def set_status_reset(self):
        """Reset the system mode."""
        return self._get_single_heating_system().set_status_reset()

    def set_status_custom(self, until=None):
        """Set the system into custom heating mode."""
        return self._get_single_heating_system().set_status_custom(until)

    def set_status_eco(self, until=None):
        """Set the system into eco heating mode."""
        return self._get_single_heating_system().set_status_eco(until)

    def set_status_away(self, until=None):
        """Set the system into away heating mode."""
        return self._get_single_heating_system().set_status_away(until)

    def set_status_dayoff(self, until=None):
        """Set the system into day off heating mode."""
        return self._get_single_heating_system().set_status_dayoff(until)

    def set_status_heatingoff(self, until=None):
        """Set the system into heating off heating mode."""
        return self._get_single_heating_system().set_status_heatingoff(until)

    def temperatures(self):
        """Return the current zone temperatures and set points."""
        return self._get_single_heating_system().temperatures()

    def zone_schedules_backup(self, filename):
        """Back up the current system configuration to the given file."""
        return self._get_single_heating_system().zone_schedules_backup(filename)

    def zone_schedules_restore(self, filename):
        """Restore the current system configuration from the given file."""
        return self._get_single_heating_system().zone_schedules_restore(filename)
