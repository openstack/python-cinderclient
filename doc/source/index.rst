Python API
==========

In order to use the Python api directly, you must first obtain an auth token
and identify which endpoint you wish to speak to. Once you have done so, you
can use the API like so::

    >>> from cinderclient import client
    >>> cinder = client.Client('1', $OS_USER_NAME, $OS_PASSWORD, $OS_PROJECT_NAME, $OS_AUTH_URL)
    >>> cinder.volumes.list()
    []
    >>> myvol = cinder.volumes.create(display_name="test-vol", size=1)
    >>> myvol.id
    ce06d0a8-5c1b-4e2c-81d2-39eca6bbfb70
    >>> cinder.volumes.list()
    [<Volume: ce06d0a8-5c1b-4e2c-81d2-39eca6bbfb70>]
    >>> myvol.delete()

Alternatively, you can create a client instance using the keystoneauth session
API::

    >>> from keystoneauth1 import loading
    >>> from keystoneauth1 import session
    >>> from cinderclient import client
    >>> loader = loading.get_plugin_loader('password')
    >>> auth = loader.load_from_options(auth_url=AUTH_URL,
    ...                                 username=USERNAME,
    ...                                 password=PASSWORD,
    ...                                 project_id=PROJECT_ID,
    ...                                 user_domain_name=USER_DOMAIN_NAME)
    >>> sess = session.Session(auth=auth)
    >>> cinder = client.Client(VERSION, session=sess)
    >>> cinder.volumes.list()
    []

User Guides
~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   user/shell
   user/no_auth

Command-Line Reference
~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   cli/index
   cli/details

Developer Guides
~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   contributor/contributing
   contributor/functional_tests
   contributor/unit_tests

Release Notes
~~~~~~~~~~~~~

All python-cinderclient release notes can now be found on the `release notes`_
page.

.. _`release notes`: https://docs.openstack.org/releasenotes/python-cinderclient/

The following are kept for historical purposes.

1.4.0
-----

* Improved error reporting on reaching quota.
* Volume status management for volume migration.
* Added command to fetch specified backend capabilities.
* Added commands for modifying image metadata.
* Support for non-disruptive backup.
* Support for cloning consistency groups.

.. _1493612: https://bugs.launchpad.net/python-cinderclient/+bug/1493612
.. _1482988: https://bugs.launchpad.net/python-cinderclient/+bug/1482988
.. _1422046: https://bugs.launchpad.net/python-cinderclient/+bug/1422046
.. _1481478: https://bugs.launchpad.net/python-cinderclient/+bug/1481478
.. _1475430: https://bugs.launchpad.net/python-cinderclient/+bug/1475430

1.3.1
-----

* Fixed usage of the --debug option.
* Documentation and API example improvements.
* Set max volume size limit for the project.
* Added encryption-type-update to cinderclient.
* Added volume multi attach support.
* Support host-attach of volumes.

.. _1467628: https://bugs.launchpad.net/python-cinderclient/+bug/1467628
.. _1454436: https://bugs.launchpad.net/cinder/+bug/1454436
.. _1423884: https://bugs.launchpad.net/python-cinderclient/+bug/1423884

1.3.0
-----

* Revert version discovery support due to this breaking deployments using
  proxies. We will revisit this once the Kilo config option 'public_endpoint'
  has been available longer to allow these deployments to work again with
  version discovery available from the Cinder client.
* Add volume multi-attach support.
* Add encryption-type-update to update volume encryption types.

.. _1454276: http://bugs.launchpad.net/python-cinderclient/+bug/1454276
.. _1462104: http://bugs.launchpad.net/python-cinderclient/+bug/1462104
.. _1418580: http://bugs.launchpad.net/python-cinderclient/+bug/1418580
.. _1464160: http://bugs.launchpad.net/python-cinderclient/+bug/1464160

1.2.2
-----

* IMPORTANT: version discovery breaks deployments using proxies and has been
  reverted in v1.3.0 . Do not use this version.
* Update requirements to resolve conflicts with other OpenStack projects

1.2.1
-----

* IMPORTANT: version discovery breaks deployments using proxies and has been
  reverted in v1.3.0 . Do not use this version.
* Remove warnings about Keystone unable to contact endpoint for discovery.
* backup-create subcommand allows specifying --incremental to do an incremental
  backup.
* Modify consistency groups using the consisgroup-update subcommand. Change the
  name, description, add volumes, or remove volumes.
* Create consistency group from consistency group snapshot using the
  consisgroup-create-from-src subcommand.
* --force no longer needs a boolean to be specified.

.. _1341411: http://bugs.launchpad.net/python-cinderclient/+bug/1341411
.. _1429102: http://bugs.launchpad.net/python-cinderclient/+bug/1429102
.. _1447589: http://bugs.launchpad.net/python-cinderclient/+bug/1447589
.. _1447162: http://bugs.launchpad.net/python-cinderclient/+bug/1447162
.. _1448244: http://bugs.launchpad.net/python-cinderclient/+bug/1448244
.. _1244453: http://bugs.launchpad.net/python-cinderclient/+bug/1244453

1.2.0
-----

* IMPORTANT: version discovery breaks deployments using proxies and has been
  reverted in v1.3.0 . Do not use this version.
* Add metadata during snapshot create.
* Add TTY password entry when no password is environment vars or --os-password.
* Ability to set backup quota in quota-update subcommand.
* Force the client to use a particular Cinder API endpoint with --bypass-url.
* Create a volume from an image by image name.
* New type-default subcommand will display the default volume type.
* New type-update subcommand allows updating a volume type's description.
* type-list subcommand displays volume type description.
* type-create subcommand allows setting the description.
* Show pools to a backend when doing a service-list subcommand.
* List and update consistency group quotas.
* Create volume types that are non-public and have particular project access.
* -d is available as a shorter option to --debug.
* transfer-list subcommand has an option for --all-tenants.
* --sort option available instead of --sort-key and --sort-dir. E.q. --sort
  <key>[:<direction>].
* Volume type name can now be updated via subcommand type-update.
* bash completion gives subcommands when using 'cinder help'.
* Version discovery is now available. You no longer need a volumev2 service
  type in your keystone catalog.
* Filter by tenant in list subcommand.

.. _1373662: http://bugs.launchpad.net/python-cinderclient/+bug/1373662
.. _1376311: http://bugs.launchpad.net/python-cinderclient/+bug/1376311
.. _1368910: http://bugs.launchpad.net/python-cinderclient/+bug/1368910
.. _1374211: http://bugs.launchpad.net/python-cinderclient/+bug/1374211
.. _1379505: http://bugs.launchpad.net/python-cinderclient/+bug/1379505
.. _1282324: http://bugs.launchpad.net/python-cinderclient/+bug/1282324
.. _1358926: http://bugs.launchpad.net/python-cinderclient/+bug/1358926
.. _1342192: http://bugs.launchpad.net/python-cinderclient/+bug/1342192
.. _1386232: http://bugs.launchpad.net/python-cinderclient/+bug/1386232
.. _1402846: http://bugs.launchpad.net/python-cinderclient/+bug/1402846
.. _1373766: http://bugs.launchpad.net/python-cinderclient/+bug/1373766
.. _1403902: http://bugs.launchpad.net/python-cinderclient/+bug/1403902
.. _1377823: http://bugs.launchpad.net/python-cinderclient/+bug/1377823
.. _1350702: http://bugs.launchpad.net/python-cinderclient/+bug/1350702
.. _1357559: http://bugs.launchpad.net/python-cinderclient/+bug/1357559
.. _1341424: http://bugs.launchpad.net/python-cinderclient/+bug/1341424
.. _1365273: http://bugs.launchpad.net/python-cinderclient/+bug/1365273
.. _1404020: http://bugs.launchpad.net/python-cinderclient/+bug/1404020
.. _1380729: http://bugs.launchpad.net/python-cinderclient/+bug/1380729
.. _1417273: http://bugs.launchpad.net/python-cinderclient/+bug/1417273
.. _1420238: http://bugs.launchpad.net/python-cinderclient/+bug/1420238
.. _1421210: http://bugs.launchpad.net/python-cinderclient/+bug/1421210
.. _1351084: http://bugs.launchpad.net/python-cinderclient/+bug/1351084
.. _1366289: http://bugs.launchpad.net/python-cinderclient/+bug/1366289
.. _1309086: http://bugs.launchpad.net/python-cinderclient/+bug/1309086
.. _1379486: http://bugs.launchpad.net/python-cinderclient/+bug/1379486
.. _1422244: http://bugs.launchpad.net/python-cinderclient/+bug/1422244
.. _1399747: http://bugs.launchpad.net/python-cinderclient/+bug/1399747
.. _1431693: http://bugs.launchpad.net/python-cinderclient/+bug/1431693
.. _1428764: http://bugs.launchpad.net/python-cinderclient/+bug/1428764

** Python 2.4 support removed.

** --sort-key and --sort-dir are deprecated. Use --sort instead.

** A dash will be displayed of None when there is no data to display under
   a column.

1.1.1
------

.. _1370152: http://bugs.launchpad.net/python-cinderclient/+bug/1370152

1.1.0
------

* Add support for ConsistencyGroups
* Use Adapter from keystoneclient
* Add support for Replication feature
* Add pagination for Volume List
* Note Connection refused --> Connection error commit:
  c9e7818f3f90ce761ad8ccd09181c705880a4266
* Note Mask Passwords in log output commit:
  80582f2b860b2dadef7ae07bdbd8395bf03848b1


.. _1325773: http://bugs.launchpad.net/python-cinderclient/+bug/1325773
.. _1333257: http://bugs.launchpad.net/python-cinderclient/+bug/1333257
.. _1268480: http://bugs.launchpad.net/python-cinderclient/+bug/1268480
.. _1275025: http://bugs.launchpad.net/python-cinderclient/+bug/1275025
.. _1258489: http://bugs.launchpad.net/python-cinderclient/+bug/1258489
.. _1241682: http://bugs.launchpad.net/python-cinderclient/+bug/1241682
.. _1203471: http://bugs.launchpad.net/python-cinderclient/+bug/1203471
.. _1210874: http://bugs.launchpad.net/python-cinderclient/+bug/1210874
.. _1200214: http://bugs.launchpad.net/python-cinderclient/+bug/1200214
.. _1130572: http://bugs.launchpad.net/python-cinderclient/+bug/1130572
.. _1156994: http://bugs.launchpad.net/python-cinderclient/+bug/1156994

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

* Added support for backup-service commands

.. _1163546: http://bugs.launchpad.net/python-cinderclient/+bug/1163546
.. _1161857: http://bugs.launchpad.net/python-cinderclient/+bug/1161857
.. _1160898: http://bugs.launchpad.net/python-cinderclient/+bug/1160898
.. _1161857: http://bugs.launchpad.net/python-cinderclient/+bug/1161857
.. _1156994: http://bugs.launchpad.net/python-cinderclient/+bug/1156994

1.0.3
-----

* Added support for V2 Cinder API
* Corrected upload-volume-to-image help messaging
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
