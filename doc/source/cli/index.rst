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
configuration options `--os-username`, `--os-password`, `--os-project-name` or
`--os-project-id`, and `--os-auth-url` or set corresponding environment
variables::

    export OS_USERNAME=user
    export OS_PASSWORD=pass
    export OS_PROJECT_NAME=myproject
    export OS_AUTH_URL=http://auth.example.com:5000/v3

You can select an API version to use by `--os-volume-api-version` option or by
setting corresponding environment variable::

    export OS_VOLUME_API_VERSION=3


OPTIONS
=======

To get a list of available commands and options run::

    cinder help

To get usage and options of a command::

    cinder help <command>

You can see more details about the Cinder Command-Line Client at
:doc:`details`.

EXAMPLES
========

Get information about volume create command::

    cinder help create

List all the volumes::

    cinder list

Create new volume::

    cinder create 1 --name volume01

Describe a specific volume::

    cinder show 65d23a41-b13f-4345-ab65-918a4b8a6fe6

Create a snapshot::

    cinder snapshot-create 65d23a41-b13f-4345-ab65-918a4b8a6fe6 \
                           --name qt-snap


BUGS
====

Cinder client is hosted in Launchpad so you can view current bugs at
https://bugs.launchpad.net/python-cinderclient/.
