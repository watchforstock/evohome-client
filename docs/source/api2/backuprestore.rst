Backup and Restore
==================

With thanks to Andrew Blake for adding

Backup your zone schedules
--------------------------

.. code-block:: python

    client.zone_schedules_backup('filename.json')

Restore your zone schedules
---------------------------

.. code-block:: python

    client.zone_schedules_restore('filename.json')
