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
1.0.6
-----
* Add support for multiple endpoints
* Add response info for backup command
* Add metadata option to cinder list command
* Add timeout parameter for requests
* Add update action for snapshot metadata
* Add encryption metadata support
* Add volume migrate support

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
