import requests
import json

class EvohomeClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.userData = None
        
    def userinfo(self):
        if self.userData is None:
            url = 'https://rs.alarmnet.com/TotalConnectComfort/WebAPI/api/Session'
            self.postdata = {'Username':self.username,'Password':self.password,'ApplicationId':'91db1612-73fd-4500-91b2-e63b069b185c'}
            self.headers = {'content-type':'application/json'}

            response = requests.post(url,data=json.dumps(self.postdata),headers=self.headers)

            self.userData = json.loads(response.content)
            
        return self.userData
        
    def temperatures(self):
        self.userinfo()
        userId = self.userData['userInfo']['userID']
        sessionId = self.userData['sessionId']

        url = 'https://rs.alarmnet.com/TotalConnectComfort/WebAPI/api/locations?userId=%s&allData=True' % userId

        self.headers['sessionId'] = sessionId

        response = requests.get(url,data=json.dumps(self.postdata),headers=self.headers)

        self.fullData = json.loads(response.content)[0]
        for device in self.fullData['devices']:
            yield {'thermostat': device['thermostatModelType'],
                    'id': device['deviceID'],
                    'name': device['name'],
                    'temp': device['thermostat']['indoorTemperature']}

USERNAME = 'USERNAME'
PASSWORD = 'PASSWORD'

if __name__ == '__main__':
    client = EvohomeClient(USERNAME, PASSWORD)
    for val in client.temperatures():
        print val
