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
configuration options `--os-username`, `--os-password`, `--os-tenant-name` or
`--os-tenant-id`, and `--os-auth-url` or set corresponding environment
variables::

    export OS_USERNAME=user
    export OS_PASSWORD=pass
    export OS_TENANT_NAME=myproject
    export OS_AUTH_URL=http://auth.example.com:5000/v3

You can select an API version to use by `--os-volume-api-version`
option or by setting corresponding environment variable::

    export OS_VOLUME_API_VERSION=3


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
