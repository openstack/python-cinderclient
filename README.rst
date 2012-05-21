Python bindings to the OpenStack Volume API
===========================================

This is a client for the OpenStack Volume API. There's a Python API (the
``cinderclient`` module), and a command-line script (``cinder``). Each
implements 100% of the OpenStack Volume API.

[PENDING] `Full documentation is available`__.

__ http://packages.python.org/python-cinderclient/

You'll also probably want to read `OpenStack Compute Developer Guide API`__ --
the first bit, at least -- to get an idea of the concepts. Rackspace is doing
the cloud hosting thing a bit differently from Amazon, and if you get the
concepts this library should make more sense.

__ http://docs.openstack.org/api/

The project is hosted on `Launchpad`_, where bugs can be filed. The code is
hosted on `Github`_. Patches must be submitted using `Gerrit`_, *not* Github
pull requests.

.. _Github: https://github.com/openstack/python-cinderclient
.. _Launchpad: https://launchpad.net/python-cinderclient
.. _Gerrit: http://wiki.openstack.org/GerritWorkflow

This code a fork of `Jacobian's python-cloudservers`__ If you need API support
for the Rackspace API solely or the BSD license, you should use that repository.
python-client is licensed under the Apache License like the rest of OpenStack.

__ http://github.com/jacobian/python-cloudservers

.. contents:: Contents:
   :local:

Command-line API
----------------

Installing this package gets you a shell command, ``cinder``, that you
can use to interact with any Rackspace compatible API (including OpenStack).

You'll need to provide your OpenStack username and password. You can do this
with the ``--os_username``, ``--os_password`` and  ``--os_tenant_name``
params, but it's easier to just set them as environment variables::

    export OS_USERNAME=openstack
    export OS_PASSWORD=yadayada
    export OS_TENANT_NAME=myproject

You will also need to define the authentication url with ``--os_auth_url``
and the version of the API with ``--version``.  Or set them as an environment
variables as well::

    export OS_AUTH_URL=http://example.com:8774/v1.1/
    export OS_COMPUTE_API_VERSION=1.1

If you are using Keystone, you need to set the CINDER_URL to the keystone
endpoint::

    export OS_AUTH_URL=http://example.com:5000/v2.0/

Since Keystone can return multiple regions in the Service Catalog, you
can specify the one you want with ``--os_region_name`` (or
``export OS_REGION_NAME``). It defaults to the first in the list returned.

You'll find complete documentation on the shell by running
``cinder help``::

    usage: cinder [--debug] [--os_username OS_USERNAME] [--os_password OS_PASSWORD]
                [--os_tenant_name OS_TENANT_NAME] [--os_auth_url OS_AUTH_URL]
                [--os_region_name OS_REGION_NAME] [--service_type SERVICE_TYPE]
                [--service_name SERVICE_NAME] [--endpoint_type ENDPOINT_TYPE]
                [--version VERSION] [--username USERNAME]
                [--region_name REGION_NAME] [--apikey APIKEY]
                [--projectid PROJECTID] [--url URL]
                <subcommand> ...

    Command-line interface to the OpenStack Nova API.

    Positional arguments:
      <subcommand>
        create              Add a new volume.
        credentials         Show user credentials returned from auth
        delete              Remove a volume.
        endpoints           Discover endpoints that get returned from the
                            authenticate services
        list                List all the volumes.
        show                Show details about a volume.
        snapshot-create     Add a new snapshot.
        snapshot-delete     Remove a snapshot.
        snapshot-list       List all the snapshots.
        snapshot-show       Show details about a snapshot.
        type-create         Create a new volume type.
        type-delete         Delete a specific flavor
        type-list           Print a list of available 'volume types'.
        bash-completion     Prints all of the commands and options to stdout so
                            that the
        help                Display help about this program or one of its
                            subcommands.

    Optional arguments:
      --debug               Print debugging output
      --os_username OS_USERNAME
                            Defaults to env[OS_USERNAME].
      --os_password OS_PASSWORD
                            Defaults to env[OS_PASSWORD].
      --os_tenant_name OS_TENANT_NAME
                            Defaults to env[OS_TENANT_NAME].
      --os_auth_url OS_AUTH_URL
                            Defaults to env[OS_AUTH_URL].
      --os_region_name OS_REGION_NAME
                            Defaults to env[OS_REGION_NAME].
      --service_type SERVICE_TYPE
                            Defaults to compute for most actions
      --service_name SERVICE_NAME
                            Defaults to env[CINDER_SERVICE_NAME]
      --endpoint_type ENDPOINT_TYPE
                            Defaults to env[CINDER_ENDPOINT_TYPE] or publicURL.
      --os_compute_api_version VERSION
                            Accepts 1.1, defaults to env[OS_COMPUTE_API_VERSION].
      --username USERNAME   Deprecated
      --region_name REGION_NAME
                            Deprecated
      --apikey APIKEY, --password APIKEY
                            Deprecated
      --projectid PROJECTID, --tenant_name PROJECTID
                            Deprecated
      --url URL, --auth_url URL
                            Deprecated

    See "cinder help COMMAND" for help on a specific command.

Python API
----------

[PENDING] There's also a `complete Python API`__.

__ http://packages.python.org/python-cinderclient/

Quick-start using keystone::

    # use v2.0 auth with http://example.com:5000/v2.0/")
    >>> from cinderclient.v1 import client
    >>> nt = client.Client(USER, PASS, TENANT, AUTH_URL, service_type="compute")
    >>> nt.flavors.list()
    [...]
    >>> nt.servers.list()
    [...]
    >>> nt.keypairs.list()
    [...]

What's new?
-----------

[PENDING] See `the release notes <http://packages.python.org/python-cinderclient/releases.html>`_.
