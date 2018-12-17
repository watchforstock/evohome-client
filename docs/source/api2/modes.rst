System modes
============

The evohome controller supports a number of different modes and the client API has the ability to switch between them.

To understand system modes, you should appreciate the relationship between the controller and its temperature zones.  

Zones can perform as instructed by the controller in some manner relative to their schedule (e.g. see the economy mode, below), or simply do their own thing. 

If behaving only as instructed by the controller, they are in FollowSchedule mode. Otherwise, they ignore their schedule altogether, and this can be for a set period of time (they will revert to FollowSchedule after that), or indefinitely; these zone modes are called TemporaryOverride, and PemanentOverride respectively. 

Set system mode to Auto
-----------------------

To set the system back to the normal status (aka Auto mode) call either of:

.. code-block:: python

    client.set_status_normal()
    
    client.set_status_reset() # Also set all zones to FollowSchedule mode

The difference between these two is how temperature zones are affected. In either case, zones in TemporaryOverride mode will be reset to FollowSchedule mode.  

With ``set_status_reset``, zones in PermanentOverride mode are also reset to FollowSchedule mode.  

Set system mode to a Mode
-------------------------

To enable one of the other modes use one of the calls below. These calls are also able to take a datetime object to specify when to enable the mode until.

.. note:: 
   For some modes, only the date part of the datetime object will be used.
    
.. code-block:: python

    client.set_status_custom(until=None) # Use the custom program

    client.set_status_eco(until=None) # Reduce all temperatures by 3 degrees

    client.set_status_away(until=None) # Heating and hot water off

    client.set_status_dayoff(until=None) # Use weekend profile

    client.set_status_heatingoff(until=None) # Heating off, hot water on

    # or to specify an end date/time
    from datetime import datetime
    dt = datetime(2015, 11, 1, 18, 0, 0)
    client.set_status_eco(until=dt)
