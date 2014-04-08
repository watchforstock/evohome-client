import requests
import json

class EvohomeClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.user_data = None
        self.full_data = None
        
    def _populate_full_data(self):
        if self.full_data is None:
            self._populate_user_info()
            userId = self.user_data['userInfo']['userID']
            sessionId = self.user_data['sessionId']

            url = 'https://rs.alarmnet.com/TotalConnectComfort/WebAPI/api/locations?userId=%s&allData=True' % userId

            self.headers['sessionId'] = sessionId

            response = requests.get(url,data=json.dumps(self.postdata),headers=self.headers)

            self.full_data = json.loads(response.content)[0]
            
            self.devices = {}
            self.named_devices = {}
            
            for device in self.full_data['devices']:
                self.devices[device['deviceID']] = device
                self.named_devices[device['name']] = device
                

    def _populate_user_info(self):
        if self.user_data is None:
            url = 'https://rs.alarmnet.com/TotalConnectComfort/WebAPI/api/Session'
            self.postdata = {'Username':self.username,'Password':self.password,'ApplicationId':'91db1612-73fd-4500-91b2-e63b069b185c'}
            self.headers = {'content-type':'application/json'}

            response = requests.post(url,data=json.dumps(self.postdata),headers=self.headers)

            self.user_data = json.loads(response.content)
            
        return self.user_data
        
    def temperatures(self):
        self._populate_full_data()
        for device in self.full_data['devices']:
            yield {'thermostat': device['thermostatModelType'],
                    'id': device['deviceID'],
                    'name': device['name'],
                    'temp': device['thermostat']['indoorTemperature']}

    def get_modes(self, zone):
        self._populate_full_data()
        
        if isinstance(zone, basestring):
            device = self.named_devices[zone]
        else:
            device = self.devices[zone]
            
        return device['thermostat']['allowedModes']
                    
    def set_mode(self, zone, mode, until=None):
        pass