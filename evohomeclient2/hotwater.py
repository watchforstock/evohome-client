"""Provides handling of the hot water zone."""

import json

import requests

from .zone import ZoneBase


class HotWater(ZoneBase):
    """Provides handling of the hot water zone."""

    def __init__(self, client, data, timeout=30):
        super(HotWater, self).__init__(client, timeout)

        self.dhwId = None  # pylint: disable=invalid-name

        self.__dict__.update(data)

        self.name = ""
        self.zoneId = self.dhwId
        self.zone_type = "domesticHotWater"

    def _set_dhw(self, data):
        headers = dict(self.client._headers())  # pylint: disable=protected-access
        headers["Content-Type"] = "application/json"
        url = (
            "https://tccna.resideo.com/WebAPI/emea/api/v1"
            "/domesticHotWater/%s/state" % self.dhwId
        )

        response = requests.put(
            url, data=json.dumps(data), headers=headers, timeout=self.timeout
        )
        response.raise_for_status()

    def set_dhw_on(self, until=None):
        """Sets the DHW on until a given time, or permanently."""
        if until is None:
            data = {"Mode": "PermanentOverride", "State": "On", "UntilTime": None}
        else:
            data = {
                "Mode": "TemporaryOverride",
                "State": "On",
                "UntilTime": until.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }

        self._set_dhw(data)

    def set_dhw_off(self, until=None):
        """Sets the DHW off until a given time, or permanently."""
        if until is None:
            data = {"Mode": "PermanentOverride", "State": "Off", "UntilTime": None}
        else:
            data = {
                "Mode": "TemporaryOverride",
                "State": "Off",
                "UntilTime": until.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }

        self._set_dhw(data)

    def set_dhw_auto(self):
        """Sets the DHW to follow the schedule."""
        data = {"Mode": "FollowSchedule", "State": "", "UntilTime": None}

        self._set_dhw(data)

    def get_dhw_state(self):
        """Gets the DHW state."""
        url = (
            "https://tccna.honeywell.com/WebAPI/emea/api/v1/"
            "domesticHotWater/%s/status?" % self.dhwId
        )

        response = requests.get(
            url, headers=self.client._headers(), timeout=self.timeout
        )
        data = response.json()
        return data
