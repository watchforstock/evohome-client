"""Provides handling of a control system."""
import json
import logging

import requests

from .zone import Zone
from .hotwater import HotWater

_LOGGER = logging.getLogger(__name__)


class ControlSystem(object):                                                     # pylint: disable=useless-object-inheritance, too-many-instance-attributes
    """Provides handling of a control system."""

    def __init__(self, client, location, gateway, data=None):
        self.client = client
        self.location = location
        self.gateway = gateway

        self._zones = []
        self.zones = {}
        self.zones_by_id = {}
        self.hotwater = None
        self.systemId = None                                                     # pylint: disable=invalid-name

        if data is not None:
            local_data = dict(data)
            del local_data['zones']
            self.__dict__.update(local_data)

            for z_data in data['zones']:
                zone = Zone(client, z_data)
                self._zones.append(zone)
                self.zones[zone.name] = zone
                self.zones_by_id[zone.zoneId] = zone

            if 'dhw' in data:
                self.hotwater = HotWater(client, data['dhw'])

    def _set_status(self, mode, until=None):
        headers = dict(self.client._headers())                                   # pylint: disable=protected-access
        headers['Content-Type'] = 'application/json'

        if until is None:
            data = {"SystemMode": mode, "TimeUntil": None, "Permanent": True}
        else:
            data = {
                "SystemMode": mode,
                "TimeUntil": until.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "Permanent": False
            }

        response = requests.put(
            "https://tccna.honeywell.com/WebAPI/emea/api/v1"
            "/temperatureControlSystem/%s/mode" % self.systemId,
            data=json.dumps(data), headers=headers
        )
        response.raise_for_status()

    def set_status(self, mode, until=None):
        """Set the system to a mode, either indefinitely, or for a set time."""
        self._set_status(mode, until)

    def set_status_normal(self):
        """Set the system into normal mode."""
        self._set_status("Auto")

    def set_status_reset(self):
        """Reset the system into normal mode.

        This will also set all the zones to FollowSchedule mode.
        """
        self._set_status("AutoWithReset")

    def set_status_custom(self, until=None):
        """Set the system into custom mode."""
        self._set_status("Custom", until)

    def set_status_eco(self, until=None):
        """Set the system into eco mode."""
        self._set_status("AutoWithEco", until)

    def set_status_away(self, until=None):
        """Set the system into away mode."""
        self._set_status("Away", until)

    def set_status_dayoff(self, until=None):
        """Set the system into dayoff mode."""
        self._set_status("DayOff", until)

    def set_status_heatingoff(self, until=None):
        """Set the system into heating off mode."""
        self._set_status("HeatingOff", until)

    def temperatures(self):
        """Return a generator with the details of each zone."""
        self.location.status()

        if self.hotwater:
            yield {
                'thermostat': 'DOMESTIC_HOT_WATER',
                'id': self.hotwater.dhwId,
                'name': '',
                'temp': self.hotwater.temperatureStatus['temperature'],          # pylint: disable=no-member
                'setpoint': ''
            }

        for zone in self._zones:
            zone_info = {
                'thermostat': 'EMEA_ZONE',
                'id': zone.zoneId,
                'name': zone.name,
                'temp': None,
                'setpoint': zone.setpointStatus['targetHeatTemperature']
            }

            if zone.temperatureStatus['isAvailable']:
                zone_info['temp'] = zone.temperatureStatus['temperature']
            yield zone_info

    def zone_schedules_backup(self, filename):
        """Backup all zones on control system to the given file."""
        _LOGGER.info("Backing up schedules from ControlSystem: %s (%s)...",
                     self.systemId, self.location.name)

        schedules = {}

        if self.hotwater:
            _LOGGER.info("Retrieving DHW schedule: %s...",
                         self.hotwater.zoneId)

            schedule = self.hotwater.schedule()
            schedules[self.hotwater.zoneId] = {
                'name': 'Domestic Hot Water',
                'schedule': schedule}

        for zone in self._zones:
            zone_id = zone.zoneId
            name = zone.name

            _LOGGER.info("Retrieving Zone schedule: %s - %s", zone_id, name)

            schedule = zone.schedule()
            schedules[zone_id] = {'name': name, 'schedule': schedule}

        schedule_db = json.dumps(schedules, indent=4)

        _LOGGER.info("Writing to backup file: %s...", filename)
        with open(filename, 'w') as file_output:
            file_output.write(schedule_db)

        _LOGGER.info("Backup completed.")

    def zone_schedules_restore(self, filename):
        """Restore all zones on control system from the given file."""
        _LOGGER.info("Restoring schedules to ControlSystem %s (%s)...",
                     self.systemId, self.location)

        _LOGGER.info("Reading from backup file: %s...", filename)
        with open(filename, 'r') as file_input:
            schedule_db = file_input.read()
            schedules = json.loads(schedule_db)

            for zone_id, zone_schedule in schedules.items():
                name = zone_schedule['name']
                zone_info = zone_schedule['schedule']

                _LOGGER.info("Restoring schedule for: %s - %s...",
                             zone_id, name)

                if self.hotwater and self.hotwater.zoneId == zone_id:
                    self.hotwater.set_schedule(json.dumps(zone_info))
                else:
                    self.zones_by_id[zone_id].set_schedule(
                        json.dumps(zone_info))

        _LOGGER.info("Restore completed.")
