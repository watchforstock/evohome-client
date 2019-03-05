"""Provides handling of the hot water zone."""
import json

import requests

from .zone import ZoneBase


class HotWater(ZoneBase):
    """Provides handling of the hot water zone."""

    def __init__(self, client, data):
        super(HotWater, self).__init__(client)

        self.dhwId = None                                                        # pylint: disable=invalid-name

        self.__dict__.update(data)

        self.name = ""
        self.zoneId = self.dhwId
        self.zone_type = 'domesticHotWater'

    def _set_dhw(self, data):
        headers = dict(self.client._headers())                                   # pylint: disable=protected-access
        headers['Content-Type'] = 'application/json'
        url = (
            "https://tccna.honeywell.com/WebAPI/emea/api/v1"
            "/domesticHotWater/%s/state" % self.dhwId
        )

        response = requests.put(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()

    def set_dhw_on(self, until=None):
        """Sets the DHW on until a given time, or permanently."""
        if until is None:
            data = {"Mode": "PermanentOverride",
                    "State": "On",
                    "UntilTime": None}
        else:
            data = {"Mode": "TemporaryOverride",
                    "State": "On",
                    "UntilTime": until.strftime('%Y-%m-%dT%H:%M:%SZ')}

        self._set_dhw(data)

    def set_dhw_off(self, until=None):
        """Sets the DHW off until a given time, or permanently."""
        if until is None:
            data = {"Mode": "PermanentOverride",
                    "State": "Off",
                    "UntilTime": None}
        else:
            data = {"Mode": "TemporaryOverride",
                    "State": "Off",
                    "UntilTime": until.strftime('%Y-%m-%dT%H:%M:%SZ')}

        self._set_dhw(data)

    def set_dhw_auto(self):
        """Sets the DHW to follow the schedule."""
        data = {"Mode": "FollowSchedule",
                "State": "",
                "UntilTime": None}

        self._set_dhw(data)
