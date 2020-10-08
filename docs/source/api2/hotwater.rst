Hot Water
=========

Set hot water on
----------------

.. code-block:: python

    client.set_dhw_on() # Permanent

    from datetime import datetime
    client.set_dhw_on(datetime(2014,4,10,22,0,0)) # set on until 10 Apr 2014, 10pm
    
    

Set hot water off
-----------------

.. code-block:: python

    client.set_dhw_off() # Permanent

    from datetime import datetime
    client.set_dhw_off(datetime(2014,4,10,22,0,0)) # set off until 10 Apr 2014, 10pm

Set hot water to auto (cancel override)
---------------------------------------

.. code-block:: python

    client.set_dhw_auto()

Get hot water status
--------------------

.. code-block:: python

    client = EvohomeClient(username, password)
 
    dhw = client.locations[0]._gateways[0]._control_systems[0].hotwater.get_dhw_state()

    temp = dhw['temperatureStatus']['temperature']
    status = dhw['stateStatus']['state']
    mode = dhw['stateStatus']['mode']

    print("temperature {}".format(temp))
    print("status {}".format(status))
    print("mode {}".format(mode))

