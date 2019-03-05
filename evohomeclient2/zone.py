"""Provides handling of individual zones"""
import json

import requests


class ZoneBase(object):                                                          # pylint: disable=useless-object-inheritance
    """Provides the base for Zones"""

    def __init__(self, client):
        self.client = client
        self.name = None
        self.zoneId = None                                                       # pylint: disable=invalid-name
        self.zone_type = None

    def schedule(self):
        """Gets the schedule for the given zone"""
        response = requests.get(
            "https://tccna.honeywell.com/WebAPI/emea/api/v1"
            "/%s/%s/schedule" % (self.zone_type, self.zoneId),
            headers=self.client._headers()                                       # pylint: disable=no-member,protected-access
        )
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

        data = json.loads(response_data)
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
            raise ValueError("zone_info must be valid JSON: ", error)

        headers = dict(self.client._headers())                                   # pylint: disable=protected-access
        headers['Content-Type'] = 'application/json'

        response = requests.put(
            "https://tccna.honeywell.com/WebAPI/emea/api/v1"
            "/%s/%s/schedule" % (self.zone_type, self.zoneId),
            data=zone_info, headers=headers
        )
        response.raise_for_status()

        return response.json()


class Zone(ZoneBase):
    """Provides the access to an individual zone."""

    def __init__(self, client, data):
        super(Zone, self).__init__(client)

        self.__dict__.update(data)

        self.zone_type = 'temperatureZone'

    def set_temperature(self, temperature, until=None):
        """Sets the temperature of the given zone"""
        if until is None:
            data = {"SetpointMode": "PermanentOverride",
                    "HeatSetpointValue": temperature,
                    "TimeUntil": None}
        else:
            data = {"SetpointMode": "TemporaryOverride",
                    "HeatSetpointValue": temperature,
                    "TimeUntil": until.strftime('%Y-%m-%dT%H:%M:%SZ')}

        self._set_heat_setpoint(data)

    def _set_heat_setpoint(self, data):
        url = (
            "https://tccna.honeywell.com/WebAPI/emea/api/v1"
            "/temperatureZone/%s/heatSetpoint" % self.zoneId
        )

        headers = dict(self.client._headers())                                   # pylint: disable=protected-access
        headers['Content-Type'] = 'application/json'

        response = requests.put(url, json.dumps(data), headers=headers)
        response.raise_for_status()

    def cancel_temp_override(self):
        """Cancels an override to the zone temperature"""
        data = {"SetpointMode": "FollowSchedule",
                "HeatSetpointValue": 0.0,
                "TimeUntil": None}

        self._set_heat_setpoint(data)
