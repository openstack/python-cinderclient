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


Release Notes
=============

1.1.0
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
