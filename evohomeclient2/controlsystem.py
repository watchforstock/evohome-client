"""Provides handling of a control system"""
from __future__ import print_function
import json
import requests

from .zone import Zone
from .hotwater import HotWater


class ControlSystem(object):
    """Provides handling of a control system"""

    def __init__(self, client, location, gateway, data=None):
        super(ControlSystem, self).__init__()

        self.client = client
        self.location = location
        self.gateway = gateway

        self._zones = []
        self.zones = self.zones_by_id = {}
        self.hotwater = None

        if data is not None:
            local_data = dict(data)
            del local_data['zones']

            self.__dict__.update(local_data)

            for _, z_data in enumerate(data['zones']):
                zone = Zone(client, z_data)
                self._zones.append(zone)
                self.zones[zone.name] = zone                                     # pylint: disable=no-member
                self.zones_by_id[zone.zoneId] = zone                             # pylint: disable=no-member

            if 'dhw' in data:
                self.hotwater = HotWater(client, data['dhw'])

    def _set_status(self, mode, until=None):

        headers = dict(self.client._headers())                                   # pylint: disable=no-member,protected-access
        headers['Content-Type'] = 'application/json'

        if until is None:
            data = {"SystemMode": mode, "TimeUntil": None, "Permanent": True}
        else:
            data = {
                "SystemMode": mode,
                "TimeUntil": "%sT00:00:00Z" % until.strftime('%Y-%m-%d'),
                "Permanent": False
            }

        response = requests.put('https://tccna.honeywell.com/WebAPI/emea/api/v1/temperatureControlSystem/%s/mode' %
                                self.systemId, data=json.dumps(data), headers=headers)  # pylint: disable=no-member

        response.raise_for_status()

    def set_status_normal(self):
        """Sets the system into normal mode"""
        self._set_status("Auto")

    def set_status_reset(self):
        """Resets the system into normal mode"""
        self._set_status("AutoWithReset")

    def set_status_custom(self, until=None):
        """Sets the system into custom mode"""
        self._set_status("Custom", until)

    def set_status_eco(self, until=None):
        """Sets the system into eco mode"""
        self._set_status("AutoWithEco", until)

    def set_status_away(self, until=None):
        """Sets the system into away mode"""
        self._set_status("Away", until)

    def set_status_dayoff(self, until=None):
        """Sets the system into dayoff mode"""
        self._set_status("DayOff", until)

    def set_status_heatingoff(self, until=None):
        """Sets the system into heating off mode"""
        self._set_status("HeatingOff", until)

    def temperatures(self):
        """Returns a generator with the details of each zone"""
        if self.hotwater:
            yield {'thermostat': 'DOMESTIC_HOT_WATER',
                   'id': self.hotwater.dhwId,                                    # pylint: disable=no-member
                   'name': '',
                   'temp': self.hotwater.temperatureStatus['temperature'],       # pylint: disable=no-member
                   'setpoint': ''}

        for zone in self._zones:
            zone_info = {'thermostat': 'EMEA_ZONE',
                         'id': zone.zoneId,
                         'name': zone.name,
                         'temp': None,
                         'setpoint': zone.setpointStatus['targetHeatTemperature']}

            if zone.temperatureStatus['isAvailable']:
                zone_info['temp'] = zone.temperatureStatus['temperature']
            yield zone_info

    def zone_schedules_backup(self, filename):
        """Backs up all zones on control system to the given file"""
        print("Backing up zone schedule to: %s" % (filename))

        schedules = {}

        if self.hotwater:
            print("Retrieving DHW schedule: %s" % self.hotwater.zoneId)
            schedule = self.hotwater.schedule()
            schedules[self.hotwater.zoneId] = {
                'name': 'Domestic Hot Water', 'schedule': schedule}

        for zone in self._zones:
            zone_id = zone.zoneId
            name = zone.name
            print("Retrieving zone schedule: %s - %s" % (zone_id, name))
            schedule = zone.schedule()
            schedules[zone_id] = {'name': name, 'schedule': schedule}

        schedule_db = json.dumps(schedules, indent=4)

        with open(filename, 'w') as file_output:
            file_output.write(schedule_db)

        print("Backed up zone schedule to: %s" % filename)

    def zone_schedules_restore(self, filename):
        """Restores all zones on control system from the given file"""
        print("Restoring zone schedules from: %s" % filename)
        with open(filename, 'r') as file_input:
            schedule_db = file_input.read()
            schedules = json.loads(schedule_db)
            for zone_id, zone_schedule in schedules.items():

                name = zone_schedule['name']
                zone_info = zone_schedule['schedule']
                print("Restoring schedule for: %s - %s" % (zone_id, name))

                if self.hotwater and self.hotwater.zoneId == zone_id:
                    self.hotwater.set_schedule(json.dumps(zone_info))
                else:
                    self.zones_by_id[zone_id].set_schedule(
                        json.dumps(zone_info))

        print("Restored zone schedules from: %s" % filename)
