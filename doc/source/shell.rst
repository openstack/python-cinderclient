The :program:`cinder` shell utility
=========================================

.. program:: cinder
.. highlight:: bash

The :program:`cinder` shell utility interacts with OpenStack Nova API
from the command line. It supports the entirety of the OpenStack Nova API.

First, you'll need an OpenStack Nova account and an API key. You get this
by using the `cinder-manage` command in OpenStack Nova.

You'll need to provide :program:`cinder` with your OpenStack username and
API key. You can do this with the :option:`--os-username`, :option:`--os-password`
and :option:`--os-tenant-id` options, but it's easier to just set them as
environment variables by setting two environment variables:

.. envvar:: OS_USERNAME

    Your OpenStack Nova username.

.. envvar:: OS_PASSWORD

    Your password.

.. envvar:: OS_TENANT_NAME

    Project for work.

.. envvar:: OS_AUTH_URL

    The OpenStack API server URL.

.. envvar:: OS_COMPUTE_API_VERSION

    The OpenStack API version.

For example, in Bash you'd use::

    export OS_USERNAME=yourname
    export OS_PASSWORD=yadayadayada
    export OS_TENANT_NAME=myproject
    export OS_AUTH_URL=http://...
    export OS_COMPUTE_API_VERSION=1.1
    
From there, all shell commands take the form::
    
    cinder <command> [arguments...]

Run :program:`cinder help` to get a full list of all possible commands,
and run :program:`cinder help <command>` to get detailed help for that
command.
