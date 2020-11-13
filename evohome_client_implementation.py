from evohomeclient2 import EvohomeClient;
import pyodbc;
from datetime import datetime;
import time;
import configparser;

config = configparser.ConfigParser()

config.read("config.ini")

databasename = config.get('DB', 'dbname');
server = config.get('DB', 'dbserver');
driver = config.get('DB', 'dbdriver'); 

username = config.get('evohome', 'username');
password = config.get('evohome', 'password');

CONNECTION_STRING = 'DRIVER=' + driver + '; SERVER=' + server + '; DATABASE=' + databasename + '; Trusted_Connection=yes';

def insert_zones(thermostat, id, name, temp, setpoint):
    cursor = connection.cursor();
    sSQL = '''
        INSERT INTO 
        dbo.Zones (uid, timestamp, thermostat, id, [name], temp, setpoint) 
        VALUES (NEWID(), CURRENT_TIMESTAMP, \'''' + thermostat + '''\', \'''' + id + '''\', \'''' + name + '''\', \'''' + str(temp) + '''\', \'''' + str(setpoint) + '''\')
    '''

    cursor.execute(sSQL);
    
    print('id: ' + id + ' inserted')
    
    cursor.commit();

# Infinite loop every 5 minutes, send temperatures to sql
while True:
    connection = pyodbc.connect(CONNECTION_STRING);

    try:
        client = EvohomeClient(username, password, debug=True)
    except ValueError:
        try:
            client = EvohomeClient(username, password, debug=True)
        except ValueError:
            print("Error when connecting to internet, please try again")


    for device in client.temperatures():
        print(device)
        insert_zones(thermostat=device['thermostat'], id=device['id'], name=device['name'], temp=device['temp'], setpoint=device['setpoint'])

    connection.close();

    print ("Going to sleep for 5 minutes")
    time.sleep(300)