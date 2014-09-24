Python API
==========
In order to use the python api directly, you must first obtain an auth token and identify which endpoint you wish to speak to. Once you have done so, you can use the API like so::

    >>> from cinderclient import client
    >>> cinder = client.Client('1', $OS_USER_NAME, $OS_PASSWORD, $OS_TENANT_NAME, $OS_AUTH_URL)
    >>> cinder.volumes.list()
    []
    >>> myvol = cinder.volumes.create(display_name="test-vol", size=1)
    >>> myvol.id
    ce06d0a8-5c1b-4e2c-81d2-39eca6bbfb70
    >>> cinder.volumes.list()
    [<Volume: ce06d0a8-5c1b-4e2c-81d2-39eca6bbfb70>]
    >>>myvol.delete

Command-line Tool
=================
In order to use the CLI, you must provide your OpenStack username, password, tenant, and auth endpoint. Use the corresponding configuration options (``--os-username``, ``--os-password``, ``--os-tenant-id``, and ``--os-auth-url``) or set them in environment variables::

    export OS_USERNAME=user
    export OS_PASSWORD=pass
    export OS_TENANT_ID=b363706f891f48019483f8bd6503c54b
    export OS_AUTH_URL=http://auth.example.com:5000/v2.0

Once you've configured your authentication parameters, you can run ``cinder help`` to see a complete listing of available commands.

See also :doc:`/man/cinder`.


Release Notes
=============

MASTER
-----

1.1.1
------
.. _1370152 http://bugs.launchpad.net/python-cinderclient/+bug/1370152

1.1.0
------

* Add support for ConsistencyGroups
* Use Adapter from keystoneclient
* Add support for Replication feature
* Add pagination for Volume List

.. _1325773 http://bugs.launchpad.net/python-cinderclient/+bug/1325773
.. _1333257 http://bugs.launchpad.net/python-cinderclient/+bug/1333257
.. _1268480 http://bugs.launchpad.net/python-cinderclient/+bug/1268480
.. _1275025 http://bugs.launchpad.net/python-cinderclient/+bug/1275025
.. _1258489 http://bugs.launchpad.net/python-cinderclient/+bug/1258489
.. _1241682 http://bugs.launchpad.net/python-cinderclient/+bug/1241682
.. _1203471 http://bugs.launchpad.net/python-cinderclient/+bug/1203471
.. _1210874 http://bugs.launchpad.net/python-cinderclient/+bug/1210874
.. _1200214 http://bugs.launchpad.net/python-cinderclient/+bug/1200214
.. _1130572 http://bugs.launchpad.net/python-cinderclient/+bug/1130572
.. _1156994 http://bugs.launchpad.net/python-cinderclient/+bug/1156994

** Note Connection refused --> Connection error commit: c9e7818f3f90ce761ad8ccd09181c705880a4266
** Note Mask Passwords in log output commit: 80582f2b860b2dadef7ae07bdbd8395bf03848b1

1.0.9
------
.. _1255905: http://bugs.launchpad.net/python-cinderclient/+bug/1255905
.. _1267168: http://bugs.launchpad.net/python-cinderclient/+bug/1267168
.. _1284540: http://bugs.launchpad.net/python-cinderclient/+bug/1284540

1.0.8
-----
* Add support for reset-state on multiple volumes or snapshots at once
* Add volume retype command

.. _966329: https://bugs.launchpad.net/python-cinderclient/+bug/966329
.. _1256043: https://bugs.launchpad.net/python-cinderclient/+bug/1256043
.. _1254951: http://bugs.launchpad.net/python-cinderclient/+bug/1254951
.. _1254587: http://bugs.launchpad.net/python-cinderclient/+bug/1254587
.. _1253142: http://bugs.launchpad.net/python-cinderclient/+bug/1253142
.. _1252665: http://bugs.launchpad.net/python-cinderclient/+bug/1252665
.. _1255876: http://bugs.launchpad.net/python-cinderclient/+bug/1255876
.. _1251385: http://bugs.launchpad.net/python-cinderclient/+bug/1251385
.. _1264415: http://bugs.launchpad.net/python-cinderclient/+bug/1264415
.. _1258489: http://bugs.launchpad.net/python-cinderclient/+bug/1258489
.. _1248519: http://bugs.launchpad.net/python-cinderclient/+bug/1248519
.. _1257747: http://bugs.launchpad.net/python-cinderclient/+bug/1257747

1.0.7
-----
* Add support for read-only volumes
* Add support for setting snapshot metadata
* Deprecate volume-id arg to backup restore in favor of --volume
* Add quota-usage command
* Fix exception deprecation warning message
* Report error when no args supplied to rename cmd

.. _1241941: http://bugs.launchpad.net/python-cinderclient/+bug/1241941
.. _1242816: http://bugs.launchpad.net/python-cinderclient/+bug/1242816
.. _1233311: http://bugs.launchpad.net/python-cinderclient/+bug/1233311
.. _1227307: http://bugs.launchpad.net/python-cinderclient/+bug/1227307
.. _1240151: http://bugs.launchpad.net/python-cinderclient/+bug/1240151
.. _1241682: http://bugs.launchpad.net/python-cinderclient/+bug/1241682


1.0.6
-----
* Add support for multiple endpoints
* Add response info for backup command
* Add metadata option to cinder list command
* Add timeout parameter for requests
* Add update action for snapshot metadata
* Add encryption metadata support
* Add volume migrate support
* Add support for QoS specs

.. _1221104: http://bugs.launchpad.net/python-cinderclient/+bug/1221104
.. _1220590: http://bugs.launchpad.net/python-cinderclient/+bug/1220590
.. _1220147: http://bugs.launchpad.net/python-cinderclient/+bug/1220147
.. _1214176: http://bugs.launchpad.net/python-cinderclient/+bug/1214176
.. _1210874: http://bugs.launchpad.net/python-cinderclient/+bug/1210874
.. _1210296: http://bugs.launchpad.net/python-cinderclient/+bug/1210296
.. _1210292: http://bugs.launchpad.net/python-cinderclient/+bug/1210292
.. _1207635: http://bugs.launchpad.net/python-cinderclient/+bug/1207635
.. _1207609: http://bugs.launchpad.net/python-cinderclient/+bug/1207609
.. _1207260: http://bugs.launchpad.net/python-cinderclient/+bug/1207260
.. _1206968: http://bugs.launchpad.net/python-cinderclient/+bug/1206968
.. _1203471: http://bugs.launchpad.net/python-cinderclient/+bug/1203471
.. _1200214: http://bugs.launchpad.net/python-cinderclient/+bug/1200214
.. _1195014: http://bugs.launchpad.net/python-cinderclient/+bug/1195014

1.0.5
-----
* Add CLI man page
* Add Availability Zone list command
* Add support for scheduler-hints
* Add support to extend volumes
* Add support to reset state on volumes and snapshots
* Add snapshot support for quota class

.. _1190853: http://bugs.launchpad.net/python-cinderclient/+bug/1190853
.. _1190731: http://bugs.launchpad.net/python-cinderclient/+bug/1190731
.. _1169455: http://bugs.launchpad.net/python-cinderclient/+bug/1169455
.. _1188452: http://bugs.launchpad.net/python-cinderclient/+bug/1188452
.. _1180393: http://bugs.launchpad.net/python-cinderclient/+bug/1180393
.. _1182678: http://bugs.launchpad.net/python-cinderclient/+bug/1182678
.. _1179008: http://bugs.launchpad.net/python-cinderclient/+bug/1179008
.. _1180059: http://bugs.launchpad.net/python-cinderclient/+bug/1180059
.. _1170565: http://bugs.launchpad.net/python-cinderclient/+bug/1170565

1.0.4
-----
* Added suport for backup-service commands
.. _1163546: http://bugs.launchpad.net/python-cinderclient/+bug/1163546
.. _1161857: http://bugs.launchpad.net/python-cinderclient/+bug/1161857
.. _1160898: http://bugs.launchpad.net/python-cinderclient/+bug/1160898
.. _1161857: http://bugs.launchpad.net/python-cinderclient/+bug/1161857
.. _1156994: http://bugs.launchpad.net/python-cinderclient/+bug/1156994

1.0.3
-----

* Added support for V2 Cinder API
* Corected upload-volume-to-image help messaging
* Align handling of metadata args for all methods
* Update OSLO version
* Correct parsing of volume metadata
* Enable force delete of volumes and snapshots in error state
* Implement clone volume API call
* Add list-extensions call to cinderclient
* Add bootable column to list output
* Add retries to cinderclient operations
* Add Type/Extra-Specs support
* Add volume and snapshot rename commands
.. _1155655: http://bugs.launchpad.net/python-cinderclient/+bug/1155655
.. _1130730: http://bugs.launchpad.net/python-cinderclient/+bug/1130730
.. _1068521: http://bugs.launchpad.net/python-cinderclient/+bug/1068521
.. _1052161: http://bugs.launchpad.net/python-cinderclient/+bug/1052161
.. _1071003: http://bugs.launchpad.net/python-cinderclient/+bug/1071003
.. _1065275: http://bugs.launchpad.net/python-cinderclient/+bug/1065275
.. _1053432: http://bugs.launchpad.net/python-cinderclient/+bug/1053432
