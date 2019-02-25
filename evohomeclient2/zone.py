"""Provides handling of individual zones"""
import json
import requests
from .base import EvohomeBase, EvohomeClientInvalidPostData


class ZoneBase(EvohomeBase):
    """Provides the base for Zones"""

    def __init__(self):
        super(ZoneBase, self).__init__()
        self.name = ""
        self.zoneId = ""  # pylint: disable=invalid-name
        self.zone_type = ""

    def schedule(self):
        """Gets the schedule for the given zone"""
        response = requests.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/%s/%s/schedule' %
                                (self.zone_type, self.zoneId), headers=self.client._headers())  # pylint: disable=no-member,protected-access

        if response.status_code != requests.codes.ok:  # pylint: disable=no-member
            response.raise_for_status()

        mapping = [
            ('dailySchedules', 'DailySchedules'),
            ('dayOfWeek', 'DayOfWeek'),
            ('temperature', 'TargetTemperature'),
            ('timeOfDay', 'TimeOfDay'),
            ('switchpoints', 'Switchpoints'),
            ('dhwState', 'DhwState'),
        ]
        response_data = response.text
        for from_val, to_val in mapping:
            response_data = response_data.replace(from_val, to_val)

        data = self._convert(response_data)
        # change the day name string to a number offset (0 = Monday)
        for day_of_week, schedule in enumerate(data['DailySchedules']):
            schedule['DayOfWeek'] = day_of_week
        return data

    def set_schedule(self, zone_info):
        """Sets the schedule for this zone"""
        # must only POST json, otherwise server API handler raises exceptions

        try:
            json.loads(zone_info)
        except ValueError as error:
            raise EvohomeClientInvalidPostData(
                'zone_info must be valid JSON: ', error)

        # pylint: disable=no-member,protected-access
        headers = dict(self.client._headers())
        headers['Content-Type'] = 'application/json'
        response = requests.put('https://tccna.honeywell.com/WebAPI/emea/api/v1/%s/%s/schedule' %
                                (self.zone_type, self.zoneId), data=zone_info, headers=headers)

        if response.status_code != requests.codes.ok:  # pylint: disable=no-member
            response.raise_for_status()

        return self._convert(response.text)


class Zone(ZoneBase):
    """Provides the access to an individual zone"""

    def __init__(self, client, data=None):
        super(Zone, self).__init__()
        self.client = client
        self.zone_type = 'temperatureZone'
        if data is not None:
            self.__dict__.update(data)

    def set_temperature(self, temperature, until=None):
        """Sets the temperature of the given zone"""
        if until is None:
            data = {"HeatSetpointValue": temperature,
                    "SetpointMode": "PermanentOverride", "TimeUntil": None}
        else:
            data = {"HeatSetpointValue": temperature, "SetpointMode": "TemporaryOverride",
                    "TimeUntil": until.strftime('%Y-%m-%dT%H:%M:%SZ')}
        self._set_heat_setpoint(data)

    def _set_heat_setpoint(self, data):
        url = 'https://tccna.honeywell.com/WebAPI/emea/api/v1/temperatureZone/%s/heatSetpoint' % self.zoneId

        # pylint: disable=no-member,protected-access
        headers = dict(self.client._headers())
        headers['Content-Type'] = 'application/json'
        response = requests.put(url, json.dumps(data), headers=headers)

        if response.status_code != requests.codes.ok:  # pylint: disable=no-member
            response.raise_for_status()

    def cancel_temp_override(self):
        """Cancels an override to the zone temperature"""
        data = {"HeatSetpointValue": 0.0,
                "SetpointMode": "FollowSchedule", "TimeUntil": None}
        self._set_heat_setpoint(data)
