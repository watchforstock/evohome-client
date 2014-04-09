System modes
============

Evohome supports a number of different modes and the client API has the ability to switch between them.

To set the system back to the normal or auto status call:

.. code-block:: python

    client.set_status_normal()
    
To enable one of the other modes use one of the calls below. These calls are also able to take a datetime object to specify when to enable the mode until.

.. warning:: 

    Only the date part of the datetime object will be used.
    
.. code-block:: python

    client.set_status_custom() # Use the custom program

    client.set_status_eco() # Reduce all temperatures by 3 degrees

    client.set_status_away() # Heating and hot water off

    client.set_status_dayoff() # Use weekend profile

    client.set_status_heatingoff() # Heating off, hot water on
