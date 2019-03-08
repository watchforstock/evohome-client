"""Tests for evohomeclient package"""
from datetime import datetime
import requests_mock
from . import EvohomeClient

UNAUTH_RESPONSE = '''[{
    "code": "Unauthorized",
    "message": "Unauthorized"
}]'''

TASK_ACCEPTED_LIST = '''[{"id": "123"}]'''
TASK_ACCEPTED = '''{"id": "123"}'''

VALID_SESSION_RESPONSE = '''{
  "sessionId": "EE32E3A8-1C09-4A5C-9572-24A088197A38",
  "userInfo": {
    "userID": 123456,
    "username": "username",
    "firstname": "Forename",
    "lastname": "Surname",
    "streetAddress": "Street Address",
    "city": "City",
    "state": "",
    "zipcode": "AB1 2CD",
    "country": "GB",
    "telephone": "",
    "userLanguage": "en-GB",
    "isActivated": true,
    "deviceCount": 0,
    "tenantID": 5,
    "securityQuestion1": "NotUsed",
    "securityQuestion2": "NotUsed",
    "securityQuestion3": "NotUsed",
    "latestEulaAccepted": false
  }
}'''

VALID_ZONE_RESPONSE = '''[
    {
        "locationID": 23456,
        "name": "Home",
        "streetAddress": "Street Address",
        "city": "City",
        "state": "",
        "country": "GB",
        "zipcode": "AB1 2CD",
        "type": "Residential",
        "hasStation": true,
        "devices": [
        {
            "gatewayId": 333444,
            "deviceID": 131313,
            "thermostatModelType": "DOMESTIC_HOT_WATER",
            "deviceType": 96,
            "name": "",
            "scheduleCapable": false,
            "holdUntilCapable": false,
            "thermostat": {
            "units": "Celsius",
            "indoorTemperature": 24.0100,
            "outdoorTemperature": 128.0000,
            "outdoorTemperatureAvailable": false,
            "outdoorHumidity": 128.0000,
            "outdootHumidityAvailable": false,
            "indoorHumidity": 128.0000,
            "indoorTemperatureStatus": "Measured",
            "indoorHumidityStatus": "NotAvailable",
            "outdoorTemperatureStatus": "NotAvailable",
            "outdoorHumidityStatus": "NotAvailable",
            "isCommercial": false,
            "allowedModes": [
                "DHWOn",
                "DHWOff"
            ],
            "deadband": 0.0000,
            "minHeatSetpoint": 5.0000,
            "maxHeatSetpoint": 30.0000,
            "minCoolSetpoint": 50.0000,
            "maxCoolSetpoint": 90.0000,
            "changeableValues": {
                "mode": "DHWOff",
                "status": "Scheduled"
            },
            "scheduleCapable": false,
            "vacationHoldChangeable": false,
            "vacationHoldCancelable": false,
            "scheduleHeatSp": 0.0000,
            "scheduleCoolSp": 0.0000
            },
            "alertSettings": {
            "deviceID": 131313,
            "tempHigherThanActive": false,
            "tempHigherThan": 100.0000,
            "tempHigherThanMinutes": 0,
            "tempLowerThanActive": false,
            "tempLowerThan": -50.0000,
            "tempLowerThanMinutes": 0,
            "faultConditionExistsActive": false,
            "faultConditionExistsHours": 0,
            "normalConditionsActive": true,
            "communicationLostActive": false,
            "communicationLostHours": 0,
            "thermostatAlertActive": false,
            "communicationFailureActive": true,
            "communicationFailureMinutes": 15,
            "deviceLostActive": false,
            "deviceLostHours": 0
            },
            "isUpgrading": false,
            "isAlive": true,
            "thermostatVersion": "03.00.10.06",
            "macID": "001122334455",
            "locationID": 23456,
            "domainID": 28111,
            "instance": 250
        },
        {
            "gatewayId": 333444,
            "deviceID": 121212,
            "thermostatModelType": "EMEA_ZONE",
            "deviceType": 96,
            "name": "RoomName",
            "scheduleCapable": false,
            "holdUntilCapable": false,
            "thermostat": {
            "units": "Celsius",
            "indoorTemperature": 17.5400,
            "outdoorTemperature": 128.0000,
            "outdoorTemperatureAvailable": false,
            "outdoorHumidity": 128.0000,
            "outdootHumidityAvailable": false,
            "indoorHumidity": 128.0000,
            "indoorTemperatureStatus": "Measured",
            "indoorHumidityStatus": "NotAvailable",
            "outdoorTemperatureStatus": "NotAvailable",
            "outdoorHumidityStatus": "NotAvailable",
            "isCommercial": false,
            "allowedModes": [
                "Heat",
                "Off"
            ],
            "deadband": 0.0000,
            "minHeatSetpoint": 5.0000,
            "maxHeatSetpoint": 35.0000,
            "minCoolSetpoint": 50.0000,
            "maxCoolSetpoint": 90.0000,
            "changeableValues": {
                "mode": "Off",
                "heatSetpoint": {
                "value": 15.0,
                "status": "Scheduled"
                },
                "vacationHoldDays": 0
            },
            "scheduleCapable": false,
            "vacationHoldChangeable": false,
            "vacationHoldCancelable": false,
            "scheduleHeatSp": 0.0000,
            "scheduleCoolSp": 0.0000
            },
            "alertSettings": {
            "deviceID": 121212,
            "tempHigherThanActive": true,
            "tempHigherThan": 30.0000,
            "tempHigherThanMinutes": 0,
            "tempLowerThanActive": true,
            "tempLowerThan": 5.0000,
            "tempLowerThanMinutes": 0,
            "faultConditionExistsActive": false,
            "faultConditionExistsHours": 0,
            "normalConditionsActive": true,
            "communicationLostActive": false,
            "communicationLostHours": 0,
            "communicationFailureActive": true,
            "communicationFailureMinutes": 15,
            "deviceLostActive": false,
            "deviceLostHours": 0
            },
            "isUpgrading": false,
            "isAlive": true,
            "thermostatVersion": "03.00.10.06",
            "macID": "001122334455",
            "locationID": 23456,
            "domainID": 28111,
            "instance": 10
        }
        ]
    }
    ]'''
VALID_ZONE_RESPONSE_NO_DHW = '''[
    {
        "locationID": 23456,
        "name": "Home",
        "streetAddress": "Street Address",
        "city": "City",
        "state": "",
        "country": "GB",
        "zipcode": "AB1 2CD",
        "type": "Residential",
        "hasStation": true,
        "devices": [
        {
            "gatewayId": 333444,
            "deviceID": 121212,
            "thermostatModelType": "EMEA_ZONE",
            "deviceType": 96,
            "name": "RoomName",
            "scheduleCapable": false,
            "holdUntilCapable": false,
            "thermostat": {
            "units": "Celsius",
            "indoorTemperature": 17.5400,
            "outdoorTemperature": 128.0000,
            "outdoorTemperatureAvailable": false,
            "outdoorHumidity": 128.0000,
            "outdootHumidityAvailable": false,
            "indoorHumidity": 128.0000,
            "indoorTemperatureStatus": "Measured",
            "indoorHumidityStatus": "NotAvailable",
            "outdoorTemperatureStatus": "NotAvailable",
            "outdoorHumidityStatus": "NotAvailable",
            "isCommercial": false,
            "allowedModes": [
                "Heat",
                "Off"
            ],
            "deadband": 0.0000,
            "minHeatSetpoint": 5.0000,
            "maxHeatSetpoint": 35.0000,
            "minCoolSetpoint": 50.0000,
            "maxCoolSetpoint": 90.0000,
            "changeableValues": {
                "mode": "Off",
                "heatSetpoint": {
                "value": 15.0,
                "status": "Scheduled"
                },
                "vacationHoldDays": 0
            },
            "scheduleCapable": false,
            "vacationHoldChangeable": false,
            "vacationHoldCancelable": false,
            "scheduleHeatSp": 0.0000,
            "scheduleCoolSp": 0.0000
            },
            "alertSettings": {
            "deviceID": 121212,
            "tempHigherThanActive": true,
            "tempHigherThan": 30.0000,
            "tempHigherThanMinutes": 0,
            "tempLowerThanActive": true,
            "tempLowerThan": 5.0000,
            "tempLowerThanMinutes": 0,
            "faultConditionExistsActive": false,
            "faultConditionExistsHours": 0,
            "normalConditionsActive": true,
            "communicationLostActive": false,
            "communicationLostHours": 0,
            "communicationFailureActive": true,
            "communicationFailureMinutes": 15,
            "deviceLostActive": false,
            "deviceLostHours": 0
            },
            "isUpgrading": false,
            "isAlive": true,
            "thermostatVersion": "03.00.10.06",
            "macID": "001122334455",
            "locationID": 23456,
            "domainID": 28111,
            "instance": 10
        }
        ]
    }
    ]'''


@requests_mock.Mocker()
def test_429_returned_raises_exception(mock):  # pylint: disable=invalid-name
    """test that exception is raised for a 429 error"""
    mock.post('http://localhost:5050/WebAPI/api/Session', status_code=429, text='''[
  {
    "code": "TooManyRequests",
    "message": "Request count limitation exceeded, please try again later."
  }
]''')

    try:
        client = EvohomeClient("username", "password",
                               hostname="http://localhost:5050")
        list(client.temperatures())
        # Shouldn't get here
        assert False
    # pylint: disable=bare-except
    except:
        assert True


@requests_mock.Mocker()
def test_valid_login(mock):
    """test valid path"""
    mock.post('http://localhost:5050/WebAPI/api/Session',
              text=VALID_SESSION_RESPONSE)
    mock.get('http://localhost:5050/WebAPI/api/locations?userId=123456&allData=True',
             text=VALID_ZONE_RESPONSE)

    client = EvohomeClient("username", "password",
                           hostname="http://localhost:5050")
    data = list(client.temperatures())

    assert len(data) == 2
    # assert x[1].name == "RoomName"

    assert data == [{'thermostat': 'DOMESTIC_HOT_WATER', 'id': 131313, 'name': '', 'temp': 24.01, 'setpoint': 0, 'status': 'Scheduled', 'mode': 'DHWOff'}, {
        'thermostat': 'EMEA_ZONE', 'id': 121212, 'name': 'RoomName', 'temp': 17.54, 'setpoint': 15.0, 'status': 'Scheduled', 'mode': 'Off'}]


@requests_mock.Mocker()
def test_expired_sessionid(mock):
    """test expired sessionid"""
    mock.post('http://localhost:5050/WebAPI/api/Session',
              text=VALID_SESSION_RESPONSE)
    mock.get('http://localhost:5050/WebAPI/api/locations?userId=123456&allData=True',
             [{'text': UNAUTH_RESPONSE, 'status_code': 401}, {'text': VALID_ZONE_RESPONSE, 'status_code': 200}])

    client = EvohomeClient("username", "password",
                           hostname="http://localhost:5050", user_data={"userInfo": {"userID": "123456"}, "sessionId": "sessionhere"})
    data = list(client.temperatures())

    assert len(data) == 2
    # assert x[1].name == "RoomName"

    assert data == [{'thermostat': 'DOMESTIC_HOT_WATER', 'id': 131313, 'name': '', 'temp': 24.01, 'setpoint': 0, 'status': 'Scheduled', 'mode': 'DHWOff'}, {
        'thermostat': 'EMEA_ZONE', 'id': 121212, 'name': 'RoomName', 'temp': 17.54, 'setpoint': 15.0, 'status': 'Scheduled', 'mode': 'Off'}]


@requests_mock.Mocker()
def test_get_zone_modes(mock):
    """test get zone modes"""
    mock.get('http://localhost:5050/WebAPI/api/locations?userId=123456&allData=True',
             text=VALID_ZONE_RESPONSE)
    client = EvohomeClient("username", "password",
                           hostname="http://localhost:5050", user_data={"userInfo": {"userID": "123456"}, "sessionId": "sessionhere"})
    modes = client.get_modes("RoomName")

    modes2 = client.get_modes(121212)

    assert modes == modes2 == [
        "Heat",
        "Off"
    ]


@requests_mock.Mocker()
def test_set_status(mock):
    """test that statuses can be set correctly"""
    mock.get('http://localhost:5050/WebAPI/api/locations?userId=123456&allData=True',
             text=VALID_ZONE_RESPONSE)
    mock.put('http://localhost:5050/WebAPI/api/evoTouchSystems?locationId=23456',
             text=TASK_ACCEPTED)
    mock.get('http://localhost:5050/WebAPI/api/commTasks?commTaskId=123',
             [{"status_code": 200, "text": """{"state":"pending"}"""}, {"status_code": 200, "text": """{"state":"Succeeded"}"""}])
    client = EvohomeClient("username", "password",
                           hostname="http://localhost:5050", user_data={"userInfo": {"userID": "123456"}, "sessionId": "sessionhere"})
    client.set_status_normal()
    client.set_status_custom()
    client.set_status_eco()
    client.set_status_away()
    client.set_status_dayoff()
    client.set_status_heatingoff(datetime(2019, 10, 10, 10, 10, 10))


@requests_mock.Mocker()
def test_zone_temp(mock):
    """test that zone temps can be set correctly"""
    mock.get('http://localhost:5050/WebAPI/api/locations?userId=123456&allData=True',
             text=VALID_ZONE_RESPONSE)
    mock.put(
        'http://localhost:5050/WebAPI/api/devices/121212/thermostat/changeableValues/heatSetpoint', text=TASK_ACCEPTED)
    mock.put(
        'http://localhost:5050/WebAPI/api/devices/131313/thermostat/changeableValues', text=TASK_ACCEPTED_LIST)
    mock.get('http://localhost:5050/WebAPI/api/commTasks?commTaskId=123',
             [{"status_code": 200, "text": """{"state":"pending"}"""}, {"status_code": 200, "text": """{"state":"Succeeded"}"""}])
    client = EvohomeClient("username", "password",
                           hostname="http://localhost:5050", user_data={"userInfo": {"userID": "123456"}, "sessionId": "sessionhere"})
    client.set_temperature("RoomName", 25)
    client.set_temperature(
        "RoomName", 25, until=datetime(2019, 10, 10, 10, 10, 10))
    client.cancel_temp_override("RoomName")

    mock.get('http://localhost:5050/WebAPI/api/commTasks?commTaskId=123',
             [{"status_code": 200, "text": """{"state":"pending"}"""}, {"status_code": 200, "text": """{"state":"Succeeded"}"""}])
    client.set_dhw_on()
    client.set_dhw_off(datetime(2019, 10, 10, 10, 10, 10))
    client.set_dhw_auto()


@requests_mock.Mocker()
def test_zone_temp_no_dhw(mock):
    """test that zone temps can be set correctly"""
    mock.get('http://localhost:5050/WebAPI/api/locations?userId=123456&allData=True',
             text=VALID_ZONE_RESPONSE_NO_DHW)
    mock.put(
        'http://localhost:5050/WebAPI/api/devices/121212/thermostat/changeableValues/heatSetpoint', text=TASK_ACCEPTED_LIST)
    mock.put(
        'http://localhost:5050/WebAPI/api/devices/131313/thermostat/changeableValues', text=TASK_ACCEPTED_LIST)
    mock.get('http://localhost:5050/WebAPI/api/commTasks?commTaskId=123',
             [{"status_code": 200, "text": """{"state":"pending"}"""}, {"status_code": 200, "text": """{"state":"Succeeded"}"""}])
    client = EvohomeClient("username", "password",
                           hostname="http://localhost:5050", user_data={"userInfo": {"userID": "123456"}, "sessionId": "sessionhere"}, debug=True)
    try:
        client.set_dhw_on()
        assert False
    except:  # pylint: disable=bare-except
        pass
