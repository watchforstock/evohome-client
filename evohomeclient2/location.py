"""Provides handling of a location."""
import requests

from .gateway import Gateway


class Location(object):                                                          # pylint: disable=too-few-public-methods,useless-object-inheritance
    """Provides handling of a location."""

    def __init__(self, client, data=None):
        self.client = client
        self._gateways = []
        self.gateways = {}
        self.locationId = None                                                   # pylint: disable=invalid-name

        if data is not None:
            self.__dict__.update(data['locationInfo'])

            for gw_data in data['gateways']:
                gateway = Gateway(client, self, gw_data)
                self._gateways.append(gateway)
                self.gateways[gateway.gatewayId] = gateway                       # pylint: disable=no-member

            self.status()

    def status(self):
        """Retrieves the location status."""
        response = requests.get(
            "https://tccna.honeywell.com/WebAPI/emea/api/v1/"
            "location/%s/status?includeTemperatureControlSystems=True" %
            self.locationId,
            headers=self.client._headers()                                       # pylint: disable=protected-access
        )
        response.raise_for_status()
        data = response.json()

        # Now feed into other elements
        for gw_data in data['gateways']:
            gateway = self.gateways[gw_data['gatewayId']]

            for sys in gw_data["temperatureControlSystems"]:
                system = gateway.control_systems[sys['systemId']]

                system.__dict__.update(
                    {'systemModeStatus': sys['systemModeStatus'],
                     'activeFaults': sys['activeFaults']})

                if 'dhw' in sys:
                    system.hotwater.__dict__.update(sys['dhw'])

                for zone_data in sys["zones"]:
                    zone = system.zones[zone_data['name']]
                    zone.__dict__.update(zone_data)

        return data
