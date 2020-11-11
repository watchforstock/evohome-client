from evohomeclient2 import EvohomeClient

# Add username and password here
#client = EvohomeClient('username', 'password', debug=True)

for device in client.temperatures():
    print(device)