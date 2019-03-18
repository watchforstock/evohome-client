"""Test evohomeclient2"""
import requests_mock
from . import EvohomeClient

INSTALLATION_DATA = '''[{
    "locationInfo": {
        "locationId": "locationId"
    },
    "gateways": [
        {
            "gatewayInfo": {
                "location": "location",
                "gatewayId": "gatewayId"
            },
            "temperatureControlSystems": [
                {
                    "systemId": "sysId",
                     "zones": []
                }
            ]
        }
    ]
}]'''
INSTALLATION_DATA_MULTIPLE = '''[{
    "locationInfo": {
        "locationId": "locationId"
    },
    "gateways": [
        {
            "gatewayInfo": {
                "location": "location",
                "gatewayId": "gatewayId"
            },
            "temperatureControlSystems": [
                {
                    "systemId": "sysId",
                    "zones": []
                }
            ]
        },
        {
            "gatewayInfo": {
                "location": "location",
                "gatewayId": "gatewayId"
            },
            "temperatureControlSystems": [
                {
                    "systemId": "sysId",
                    "zones": []
                }
            ]
        }
    ]
}]'''

LOCATION_DATA = '''{
    "locationInfo": {
        "locationId": "locationId"
    },
    "gateways": [
        {
                "gatewayId": "gatewayId",
            "gatewayInfo": {
                "location": "location"
            },
            "temperatureControlSystems": [
                {
                    "systemId": "sysId",
                    "zones": [],
                    "systemModeStatus": "active",
                    "activeFaults": []
                }
            ]
        }
    ]
}'''
LOCATION_DATA_MULTIPLE = '''{
    "locationInfo": {
        "locationId": "locationId"
    },
    "gateways": [
        {
                "gatewayId": "gatewayId",
            "gatewayInfo": {
                "location": "location"
            },
            "temperatureControlSystems": [
                {
                    "systemId": "sysId",
                    "zones": [],
                    "systemModeStatus": "active",
                    "activeFaults": []
                }
            ]
        },
        {
                "gatewayId": "gatewayId",
            "gatewayInfo": {
                "location": "location"
            },
            "temperatureControlSystems": [
                {
                    "systemId": "sysId",
                    "zones": [],
                    "systemModeStatus": "active",
                    "activeFaults": []
                }
            ]
        }
    ]
}'''

AUTH_RESPONSE = '''
  {
    "access_token": "1234",
    "expires_in": 30,
    "refresh_token": "refresh"
  }
'''

USER_RESPONSE = '''
  {
    "name": "name",
    "userId": "userId"
  }
'''

GATEWAY_RESPONSE = '''
{}
'''

@requests_mock.Mocker()
def test_user_account(mock):  # pylint: disable=invalid-name
    """test that user account is successful"""
    mock.post('https://tccna.honeywell.com/Auth/OAuth/Token', status_code=200, text=AUTH_RESPONSE)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/userAccount', status_code=200, text=USER_RESPONSE)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/location/installationInfo?userId=userId&includeTemperatureControlSystems=True', status_code=200, text=INSTALLATION_DATA)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/location/locationId/status?includeTemperatureControlSystems=True', status_code=200, text=LOCATION_DATA)

   # try:
    client = EvohomeClient("username", "password")
    print(client)
    info = client.user_account()
    assert info['name'] == 'name'
    assert info['userId'] == 'userId'

@requests_mock.Mocker()
def test_temperatures(mock):  # pylint: disable=invalid-name
    """test that user account is successful"""
    mock.post('https://tccna.honeywell.com/Auth/OAuth/Token', status_code=200, text=AUTH_RESPONSE)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/userAccount', status_code=200, text=USER_RESPONSE)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/location/installationInfo?userId=userId&includeTemperatureControlSystems=True', status_code=200, text=INSTALLATION_DATA)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/location/locationId/status?includeTemperatureControlSystems=True', status_code=200, text=LOCATION_DATA)

   # try:
    client = EvohomeClient("username", "password")
    print(client)
    list(client.temperatures())

@requests_mock.Mocker()
def test_gateway(mock):  # pylint: disable=invalid-name
    """test that user account is successful"""
    mock.post('https://tccna.honeywell.com/Auth/OAuth/Token', status_code=200, text=AUTH_RESPONSE)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/userAccount', status_code=200, text=USER_RESPONSE)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/location/installationInfo?userId=userId&includeTemperatureControlSystems=True', status_code=200, text=INSTALLATION_DATA)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/location/locationId/status?includeTemperatureControlSystems=True', status_code=200, text=LOCATION_DATA)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/gateway', status_code=200, text=GATEWAY_RESPONSE)

   # try:
    client = EvohomeClient("username", "password")
    client.gateway()

@requests_mock.Mocker()
def test_single_settings(mock):
    """Test can change different statuses"""
    mock.post('https://tccna.honeywell.com/Auth/OAuth/Token', status_code=200, text=AUTH_RESPONSE)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/userAccount', status_code=200, text=USER_RESPONSE)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/location/installationInfo?userId=userId&includeTemperatureControlSystems=True', status_code=200, text=INSTALLATION_DATA)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/location/locationId/status?includeTemperatureControlSystems=True', status_code=200, text=LOCATION_DATA)
    mock.put('https://tccna.honeywell.com/WebAPI/emea/api/v1/temperatureControlSystem/sysId/mode', status_code=200, text='')
    client = EvohomeClient("username", "password", debug=True)

    client.set_status_away()
    client.set_status_eco()
    client.set_status_custom()
    client.set_status_dayoff()
    client.set_status_heatingoff()
    client.set_status_reset()
    client.set_status_normal()

@requests_mock.Mocker()
def test_multi_zone_failure(mock):
    """Confirm that exception is thrown for multiple locations"""
    mock.post('https://tccna.honeywell.com/Auth/OAuth/Token', status_code=200, text=AUTH_RESPONSE)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/userAccount', status_code=200, text=USER_RESPONSE)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/location/installationInfo?userId=userId&includeTemperatureControlSystems=True', status_code=200, text=INSTALLATION_DATA_MULTIPLE)
    mock.get('https://tccna.honeywell.com/WebAPI/emea/api/v1/location/locationId/status?includeTemperatureControlSystems=True', status_code=200, text=LOCATION_DATA_MULTIPLE)
    mock.put('https://tccna.honeywell.com/WebAPI/emea/api/v1/temperatureControlSystem/sysId/mode', status_code=200, text='')
    client = EvohomeClient("username", "password", debug=True)

    try:
        client.set_status_away()
        assert False # shouldn't get here
    # pylint: disable=bare-except
    except:
        assert True
