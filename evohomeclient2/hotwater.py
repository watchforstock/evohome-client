"""Provides handling of the hot water zone"""
import json
import requests

from .zone import ZoneBase


class HotWater(ZoneBase):
    """Provides handling of the hot water zone"""

    def __init__(self, client, data=None):
        super(HotWater, self).__init__()
        self.client = client
        self.zone_type = 'domesticHotWater'
        if data is not None:
            self.__dict__.update(data)
            self.zoneId = self.dhwId  # pylint: disable=no-member

    def _set_dhw(self, data):
        # pylint: disable=protected-access
        headers = dict(self.client._headers())
        headers['Content-Type'] = 'application/json'
        url = 'https://tccna.honeywell.com/WebAPI/emea/api/v1/domesticHotWater/%s/state' % self.dhwId  # pylint: disable=no-member

        response = requests.put(url, data=json.dumps(data), headers=headers)

        if response.status_code != requests.codes.ok:  # pylint: disable=no-member
            response.raise_for_status()

    def set_dhw_on(self, until=None):
        """Sets the DHW on until a given time, or permanantly"""
        if until is None:
            data = {"State": "On", "Mode": "PermanentOverride", "UntilTime": None}
        else:
            data = {"State": "On", "Mode": "TemporaryOverride",
                    "UntilTime": until.strftime('%Y-%m-%dT%H:%M:%SZ')}
        self._set_dhw(data)

    def set_dhw_off(self, until=None):
        """Sets the DHW off until a given time, or permanantly"""
        if until is None:
            data = {"State": "Off", "Mode": "PermanentOverride", "UntilTime": None}
        else:
            data = {"State": "Off", "Mode": "TemporaryOverride",
                    "UntilTime": until.strftime('%Y-%m-%dT%H:%M:%SZ')}
        self._set_dhw(data)

    def set_dhw_auto(self):
        """Sets the DHW to follow the schedule"""
        data = {"State": "", "Mode": "FollowSchedule", "UntilTime": None}
        self._set_dhw(data)
