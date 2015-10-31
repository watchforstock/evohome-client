Temperatures
============

Get all zone temperatures
-------------------------

.. code-block:: python

    for device in client.temperatures():
        print device

Calling this function returns a dictionary for each device which includes the sensor ID, the name of the sensor, the type of sensor and the current temperature reading

Set a zone temperature
----------------------

.. code-block:: python

    ec = EvohomeClient(username, password)
    
    zone = ec.locations[0]._gateways[0]._control_systems[0].zones['Kitchen']

    zone.set_temperature(18.0)
    
    # or to specify an end date/time
    from datetime import datetime
    dt = datetime(2015, 11, 1, 18, 0, 0)
    zone.set_temperature(18.0, dt)
