========================
Team and repository tags
========================

.. image:: https://governance.openstack.org/tc/badges/python-cinderclient.svg
    :target: https://governance.openstack.org/tc/reference/tags/index.html

.. Change things from this point on

Python bindings to the OpenStack Cinder API
===========================================

.. image:: https://img.shields.io/pypi/v/python-cinderclient.svg
    :target: https://pypi.org/project/python-cinderclient/
    :alt: Latest Version

This is a client for the OpenStack Cinder API. There's a Python API (the
``cinderclient`` module), and a command-line script (``cinder``). Each
implements 100% of the OpenStack Cinder API.

See the `OpenStack CLI Reference`_ for information on how to use the ``cinder``
command-line tool. You may also want to look at the
`OpenStack API documentation`_.

.. _OpenStack CLI Reference: https://docs.openstack.org/python-openstackclient/latest/cli/
.. _OpenStack API documentation: https://docs.openstack.org/api-quick-start/

The project is hosted on `Launchpad`_, where bugs can be filed. The code is
hosted on `OpenStack`_. Patches must be submitted using `Gerrit`_.

.. _OpenStack: https://opendev.org/openstack/python-cinderclient
.. _Launchpad: https://launchpad.net/python-cinderclient
.. _Gerrit: https://docs.openstack.org/infra/manual/developers.html#development-workflow

* License: Apache License, Version 2.0
* `PyPi`_ - package installation
* `Online Documentation`_
* `Blueprints`_ - feature specifications
* `Bugs`_ - issue tracking
* `Source`_
* `Specs`_
* `How to Contribute`_

.. _PyPi: https://pypi.org/project/python-cinderclient
.. _Online Documentation: https://docs.openstack.org/python-cinderclient/latest/
.. _Blueprints: https://blueprints.launchpad.net/python-cinderclient
.. _Bugs: https://bugs.launchpad.net/python-cinderclient
.. _Source: https://opendev.org/openstack/python-cinderclient
.. _How to Contribute: https://docs.openstack.org/infra/manual/developers.html
.. _Specs: https://specs.openstack.org/openstack/cinder-specs/


.. contents:: Contents:
   :local:

Command-line API
----------------

Installing this package gets you a shell command, ``cinder``, that you
can use to interact with any Rackspace compatible API (including OpenStack).

You'll need to provide your OpenStack username and password. You can do this
with the ``--os-username``, ``--os-password`` and  ``--os-tenant-name``
params, but it's easier to just set them as environment variables::

    export OS_USERNAME=openstack
    export OS_PASSWORD=yadayada
    export OS_TENANT_NAME=myproject

You will also need to define the authentication url with ``--os-auth-url``
and the version of the API with ``--os-volume-api-version``. Or set them as
environment variables as well. Since Block Storage API V2 is officially
deprecated, you are encouraged to set ``OS_VOLUME_API_VERSION=3``. If you
are using Keystone, you need to set the ``OS_AUTH_URL`` to the keystone
endpoint::

    export OS_AUTH_URL=http://controller:5000/v3
    export OS_VOLUME_API_VERSION=3

Since Keystone can return multiple regions in the Service Catalog, you
can specify the one you want with ``--os-region-name`` (or
``export OS_REGION_NAME``). It defaults to the first in the list returned.

You'll find complete documentation on the shell by running
``cinder help``::

    usage: cinder [--version] [-d] [--os-auth-system <auth-system>]
                  [--service-type <service-type>] [--service-name <service-name>]
                  [--volume-service-name <volume-service-name>]
                  [--os-endpoint-type <os-endpoint-type>]
                  [--endpoint-type <endpoint-type>]
                  [--os-volume-api-version <volume-api-ver>]
                  [--retries <retries>]
                  [--profile HMAC_KEY] [--os-auth-strategy <auth-strategy>]
                  [--os-username <auth-user-name>] [--os-password <auth-password>]
                  [--os-tenant-name <auth-tenant-name>]
                  [--os-tenant-id <auth-tenant-id>] [--os-auth-url <auth-url>]
                  [--os-user-id <auth-user-id>]
                  [--os-user-domain-id <auth-user-domain-id>]
                  [--os-user-domain-name <auth-user-domain-name>]
                  [--os-project-id <auth-project-id>]
                  [--os-project-name <auth-project-name>]
                  [--os-project-domain-id <auth-project-domain-id>]
                  [--os-project-domain-name <auth-project-domain-name>]
                  [--os-region-name <region-name>] [--os-token <token>]
                  [--os-url <url>] [--insecure] [--os-cacert <ca-certificate>]
                  [--os-cert <certificate>] [--os-key <key>] [--timeout <seconds>]
                  <subcommand> ...

    Command-line interface to the OpenStack Cinder API.

    Positional arguments:
      <subcommand>
        absolute-limits     Lists absolute limits for a user.
        api-version         Display the server API version information. (Supported
                            by API versions 3.0 - 3.latest)
        availability-zone-list
                            Lists all availability zones.
        backup-create       Creates a volume backup.
        backup-delete       Removes one or more backups.
        backup-export       Export backup metadata record.
        backup-import       Import backup metadata record.
        backup-list         Lists all backups.
        backup-reset-state  Explicitly updates the backup state.
        backup-restore      Restores a backup.
        backup-show         Shows backup details.
        cgsnapshot-create   Creates a cgsnapshot.
        cgsnapshot-delete   Removes one or more cgsnapshots.
        cgsnapshot-list     Lists all cgsnapshots.
        cgsnapshot-show     Shows cgsnapshot details.
        consisgroup-create  Creates a consistency group.
        consisgroup-create-from-src
                            Creates a consistency group from a cgsnapshot or a
                            source CG.
        consisgroup-delete  Removes one or more consistency groups.
        consisgroup-list    Lists all consistency groups.
        consisgroup-show    Shows details of a consistency group.
        consisgroup-update  Updates a consistency group.
        create              Creates a volume.
        credentials         Shows user credentials returned from auth.
        delete              Removes one or more volumes.
        encryption-type-create
                            Creates encryption type for a volume type. Admin only.
        encryption-type-delete
                            Deletes encryption type for a volume type. Admin only.
        encryption-type-list
                            Shows encryption type details for volume types. Admin
                            only.
        encryption-type-show
                            Shows encryption type details for a volume type. Admin
                            only.
        encryption-type-update
                            Update encryption type information for a volume type
                            (Admin Only).
        endpoints           Discovers endpoints registered by authentication
                            service.
        extend              Attempts to extend size of an existing volume.
        extra-specs-list    Lists current volume types and extra specs.
        failover-host       Failover a replicating cinder-volume host.
        force-delete        Attempts force-delete of volume, regardless of state.
        freeze-host         Freeze and disable the specified cinder-volume host.
        get-capabilities    Show backend volume stats and properties. Admin only.
        get-pools           Show pool information for backends. Admin only.
        image-metadata      Sets or deletes volume image metadata.
        image-metadata-show
                            Shows volume image metadata.
        list                Lists all volumes.
        manage              Manage an existing volume.
        metadata            Sets or deletes volume metadata.
        metadata-show       Shows volume metadata.
        metadata-update-all
                            Updates volume metadata.
        migrate             Migrates volume to a new host.
        qos-associate       Associates qos specs with specified volume type.
        qos-create          Creates a qos specs.
        qos-delete          Deletes a specified qos specs.
        qos-disassociate    Disassociates qos specs from specified volume type.
        qos-disassociate-all
                            Disassociates qos specs from all its associations.
        qos-get-association
                            Lists all associations for specified qos specs.
        qos-key             Sets or unsets specifications for a qos spec.
        qos-list            Lists qos specs.
        qos-show            Shows qos specs details.
        quota-class-show    Lists quotas for a quota class.
        quota-class-update  Updates quotas for a quota class.
        quota-defaults      Lists default quotas for a tenant.
        quota-delete        Delete the quotas for a tenant.
        quota-show          Lists quotas for a tenant.
        quota-update        Updates quotas for a tenant.
        quota-usage         Lists quota usage for a tenant.
        rate-limits         Lists rate limits for a user.
        readonly-mode-update
                            Updates volume read-only access-mode flag.
        rename              Renames a volume.
        reset-state         Explicitly updates the volume state in the Cinder
                            database.
        retype              Changes the volume type for a volume.
        service-disable     Disables the service.
        service-enable      Enables the service.
        service-list        Lists all services. Filter by host and service binary.
                            (Supported by API versions 3.0 - 3.latest)
        set-bootable        Update bootable status of a volume.
        show                Shows volume details.
        snapshot-create     Creates a snapshot.
        snapshot-delete     Removes one or more snapshots.
        snapshot-list       Lists all snapshots.
        snapshot-manage     Manage an existing snapshot.
        snapshot-metadata   Sets or deletes snapshot metadata.
        snapshot-metadata-show
                            Shows snapshot metadata.
        snapshot-metadata-update-all
                            Updates snapshot metadata.
        snapshot-rename     Renames a snapshot.
        snapshot-reset-state
                            Explicitly updates the snapshot state.
        snapshot-show       Shows snapshot details.
        snapshot-unmanage   Stop managing a snapshot.
        thaw-host           Thaw and enable the specified cinder-volume host.
        transfer-accept     Accepts a volume transfer.
        transfer-create     Creates a volume transfer.
        transfer-delete     Undoes a transfer.
        transfer-list       Lists all transfers.
        transfer-show       Shows transfer details.
        type-access-add     Adds volume type access for the given project.
        type-access-list    Print access information about the given volume type.
        type-access-remove  Removes volume type access for the given project.
        type-create         Creates a volume type.
        type-default        List the default volume type.
        type-delete         Deletes volume type or types.
        type-key            Sets or unsets extra_spec for a volume type.
        type-list           Lists available 'volume types'.
        type-show           Show volume type details.
        type-update         Updates volume type name, description, and/or
                            is_public.
        unmanage            Stop managing a volume.
        upload-to-image     Uploads volume to Image Service as an image.
        version-list        List all API versions. (Supported by API versions 3.0
                            - 3.latest)
        bash-completion     Prints arguments for bash_completion.
        help                Shows help about this program or one of its
                            subcommands.
        list-extensions

    Optional arguments:
      --version             show program's version number and exit
      -d, --debug           Shows debugging output.
      --os-auth-system <auth-system>
                            Defaults to env[OS_AUTH_SYSTEM].
      --service-type <service-type>
                            Service type. For most actions, default is volume.
      --service-name <service-name>
                            Service name. Default=env[CINDER_SERVICE_NAME].
      --volume-service-name <volume-service-name>
                            Volume service name.
                            Default=env[CINDER_VOLUME_SERVICE_NAME].
      --os-endpoint
                            Use this API endpoint instead of the Service Catalog.
                            Default=env[CINDER_ENDPOINT]
      --os-endpoint-type <os-endpoint-type>
                            Endpoint type, which is publicURL or internalURL.
                            Default=env[OS_ENDPOINT_TYPE] or nova
                            env[CINDER_ENDPOINT_TYPE] or publicURL.
      --endpoint-type <endpoint-type>
                            DEPRECATED! Use --os-endpoint-type.
      --os-volume-api-version <volume-api-ver>
                            Block Storage API version. Accepts X, X.Y (where X is
                            major and Y is minor
                            part).Default=env[OS_VOLUME_API_VERSION].
      --retries <retries>   Number of retries.
      --profile HMAC_KEY    HMAC key to use for encrypting context data for
                            performance profiling of operation. This key needs to
                            match the one configured on the cinder api server.
                            Without key the profiling will not be triggered even
                            if osprofiler is enabled on server side.
                            Defaults to env[OS_PROFILE].
      --os-auth-strategy <auth-strategy>
                            Authentication strategy (Env: OS_AUTH_STRATEGY,
                            default keystone). For now, any other value will
                            disable the authentication.
      --os-username <auth-user-name>
                            OpenStack user name. Default=env[OS_USERNAME].
      --os-password <auth-password>
                            Password for OpenStack user. Default=env[OS_PASSWORD].
      --os-tenant-name <auth-tenant-name>
                            Tenant name. Default=env[OS_TENANT_NAME].
      --os-tenant-id <auth-tenant-id>
                            ID for the tenant. Default=env[OS_TENANT_ID].
      --os-auth-url <auth-url>
                            URL for the authentication service.
                            Default=env[OS_AUTH_URL].
      --os-user-id <auth-user-id>
                            Authentication user ID (Env: OS_USER_ID).
      --os-user-domain-id <auth-user-domain-id>
                            OpenStack user domain ID. Defaults to
                            env[OS_USER_DOMAIN_ID].
      --os-user-domain-name <auth-user-domain-name>
                            OpenStack user domain name. Defaults to
                            env[OS_USER_DOMAIN_NAME].
      --os-project-id <auth-project-id>
                            Another way to specify tenant ID. This option is
                            mutually exclusive with --os-tenant-id. Defaults to
                            env[OS_PROJECT_ID].
      --os-project-name <auth-project-name>
                            Another way to specify tenant name. This option is
                            mutually exclusive with --os-tenant-name. Defaults to
                            env[OS_PROJECT_NAME].
      --os-project-domain-id <auth-project-domain-id>
                            Defaults to env[OS_PROJECT_DOMAIN_ID].
      --os-project-domain-name <auth-project-domain-name>
                            Defaults to env[OS_PROJECT_DOMAIN_NAME].
      --os-region-name <region-name>
                            Region name. Default=env[OS_REGION_NAME].
      --os-token <token>    Defaults to env[OS_TOKEN].
      --os-url <url>        Defaults to env[OS_URL].

    API Connection Options:
      Options controlling the HTTP API Connections

      --insecure            Explicitly allow client to perform "insecure" TLS
                            (https) requests. The server's certificate will not be
                            verified against any certificate authorities. This
                            option should be used with caution.
      --os-cacert <ca-certificate>
                            Specify a CA bundle file to use in verifying a TLS
                            (https) server certificate. Defaults to
                            env[OS_CACERT].
      --os-cert <certificate>
                            Defaults to env[OS_CERT].
      --os-key <key>        Defaults to env[OS_KEY].
      --timeout <seconds>   Set request timeout (in seconds).

    Run "cinder help SUBCOMMAND" for help on a subcommand.

If you want to get a particular version API help message, you can add
``--os-volume-api-version <volume-api-ver>`` in help command, like
this::

    cinder --os-volume-api-version 3.28 help

Python API(Application Programming Interface)
----------

There's also a complete Python API, but it has not yet been documented.

Quick-start using keystone::

    # use v3 auth with http://controller:5000/v3
    >>> from cinderclient.v3 import client
    >>> nt = client.Client(USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)
    >>> nt.volumes.list()
    [...]

See release notes and more at `<https://docs.openstack.org/python-cinderclient/latest/>`_.
