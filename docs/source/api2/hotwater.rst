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

