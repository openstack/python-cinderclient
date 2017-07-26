==============================
:program:`cinder` CLI man page
==============================

.. program:: cinder
.. highlight:: bash


SYNOPSIS
========

:program:`cinder` [options] <command> [command-options]

:program:`cinder help`

:program:`cinder help` <command>


DESCRIPTION
===========

The :program:`cinder` command line utility interacts with OpenStack Block
Storage Service (Cinder).

In order to use the CLI, you must provide your OpenStack username, password,
project (historically called tenant), and auth endpoint. You can use
configuration options :option:`--os-username`, :option:`--os-password`,
:option:`--os-tenant-name` or :option:`--os-tenant-id`, and
:option:`--os-auth-url` or set corresponding environment variables::

    export OS_USERNAME=user
    export OS_PASSWORD=pass
    export OS_TENANT_NAME=myproject
    export OS_AUTH_URL=http://auth.example.com:5000/v2.0

You can select an API version to use by :option:`--os-volume-api-version`
option or by setting corresponding environment variable::

    export OS_VOLUME_API_VERSION=2


OPTIONS
=======

To get a list of available commands and options run::

    cinder help

To get usage and options of a command::

    cinder help <command>


BUGS
====

Cinder client is hosted in Launchpad so you can view current bugs at
https://bugs.launchpad.net/python-cinderclient/.
