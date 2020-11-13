from evohomeclient2 import EvohomeClient;
import pyodbc;
from datetime import datetime;
import configparser;

config = configparser.ConfigParser()

config.read("config.ini")

databasename = config.get('DB', 'dbname');
server = config.get('DB', 'dbserver');
driver = config.get('DB', 'dbdriver'); 

username = config.get('evohome', 'username');
password = config.get('evohome', 'password');

CONNECTION_STRING = 'DRIVER=' + driver + '; SERVER=' + server + '; DATABASE=' + databasename + '; Trusted_Connection=yes';
connection = pyodbc.connect(CONNECTION_STRING);

client = EvohomeClient(username, password, debug=True)

def insert_zones(thermostat, id, name, temp, setpoint):
    cursor = connection.cursor();
    sSQL = '''
        INSERT INTO 
        dbo.Zones (uid, timestamp, thermostat, id, [name], temp, setpoint) 
        VALUES (NEWID(), CURRENT_TIMESTAMP, \'''' + thermostat + '''\', \'''' + id + '''\', \'''' + name + '''\', \'''' + str(temp) + '''\', \'''' + str(setpoint) + '''\')
    '''
    
    print(sSQL);
    
    cursor.execute(sSQL);
    
    print('id: ' + id + ' inserted')
    
    cursor.commit();

for device in client.temperatures():
    print(device)
    insert_zones(thermostat=device['thermostat'], id=device['id'], name=device['name'], temp=device['temp'], setpoint=device['setpoint'])

connection.close();