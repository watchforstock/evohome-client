Temperatures
============

Get all zone temperatures
-------------------------

.. code-block:: python

    for device in client.temperatures():
        print device

Calling this function returns a dictionary for each device which includes the sensor ID, the name of the sensor, the type of sensor and the current temperature reading
