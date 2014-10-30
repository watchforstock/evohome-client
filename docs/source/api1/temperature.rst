Temperatures
============

Get all zone temperatures
-------------------------

.. code-block:: python

    for device in client.temperatures():
        print device
        
Calling this function returns a dictionary for each device which includes the sensor ID, the name of the sensor, the type of sensor and the current temperature reading

The temperatures are cached so if you want to request updated values, you can force a refresh:

.. code-block:: python

    for device in client.temperatures(force_refresh=True):
        print device

Specifying a zone
-----------------

Zones can be specified either as a string with the name of zone (case sensitive) or based on the ID of the sensor.

Both of these can be found by running the command above to list the current configuration of the system.

.. code-block:: python

    zone = 'House'
    
    # or
    
    zone = 31234

Setting a zone temperature
--------------------------
    
.. code-block:: python

    temperature = 19.0
    client.set_temperature(zone, temperature) # set permanent
    
    from datetime import datetime
    client.set_temperature(zone, temperature, datetime(2014,4,10,22,0,0)) # set temperature until 10 Apr 2014, 10pm
    
Cancelling the temperature override
-----------------------------------
    
.. code-block:: python

    client.cancel_temp_override(zone)
    
    