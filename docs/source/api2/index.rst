Evohome Client - Version 2
==========================

Instantiating the client
------------------------

.. code-block:: python

    from evohomeclient2 import EvohomeClient

    client = EvohomeClient('username', 'password')

To debug the communications, instantiate the client with the debug flag set:

.. code-block:: python

    from evohomeclient2 import EvohomeClient

    client = EvohomeClient('username', 'password', debug=True)


Contents:

.. toctree::
   :maxdepth: 2

   temperature
   hotwater
   modes
   schedule
   backuprestore
