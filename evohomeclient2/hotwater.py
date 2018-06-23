import requests
import json

from .zone import ZoneBase

class HotWater(ZoneBase):

    def __init__(self, client, data=None):
        super(HotWater, self).__init__()
        self.client = client
        self.zone_type = 'domesticHotWater'
        if data is not None:
            self.__dict__.update(data)
            self.zoneId = self.dhwId

    def _set_dhw(self, data):
        headers = dict(self.client.headers())
        headers['Content-Type'] = 'application/json'
        url = 'https://tccna.honeywell.com/WebAPI/emea/api/v1/domesticHotWater/%s/state' % self.dhwId

        r = requests.put(url, data=json.dumps(data), headers=headers)

        if r.status_code != requests.codes.ok:
            r.raise_for_status()

    def set_dhw_on(self, until=None):
        if until is None:
            data = {"State":"On","Mode":"PermanentOverride","UntilTime":None}
        else:
            data = {"State":"On","Mode":"TemporaryOverride","UntilTime":until.strftime('%Y-%m-%dT%H:%M:%SZ')}
        self._set_dhw(data)

    def set_dhw_off(self, until=None):
        if until is None:
            data = {"State":"Off","Mode":"PermanentOverride","UntilTime":None}
        else:
            data = {"State":"Off","Mode":"TemporaryOverride","UntilTime":until.strftime('%Y-%m-%dT%H:%M:%SZ')}
        self._set_dhw(data)

    def set_dhw_auto(self):
        data =  {"State":"","Mode":"FollowSchedule","UntilTime":None}
        self._set_dhw(data)
