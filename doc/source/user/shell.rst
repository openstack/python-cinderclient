The :program:`cinder` shell utility
===================================

.. program:: cinder
.. highlight:: bash

The :program:`cinder` shell utility interacts with the OpenStack Cinder API
from the command line. It supports the entirety of the OpenStack Cinder API.

You'll need to provide :program:`cinder` with your OpenStack username and
API key. You can do this with the `--os-username`, `--os-password` and
`--os-tenant-name` options, but it's easier to just set them as environment
variables by setting two environment variables:

.. envvar:: OS_USERNAME or CINDER_USERNAME

    Your OpenStack Cinder username.

.. envvar:: OS_PASSWORD or CINDER_PASSWORD

    Your password.

.. envvar:: OS_PROJECT_NAME or CINDER_PROJECT_ID

    Project for work.

.. envvar:: OS_AUTH_URL or CINDER_URL

    The OpenStack API server URL.

.. envvar:: OS_VOLUME_API_VERSION

    The OpenStack Block Storage API version.

For example, in Bash you'd use::

    export OS_USERNAME=yourname
    export OS_PASSWORD=yadayadayada
    export OS_PROJECT_NAME=myproject
    export OS_AUTH_URL=http://auth.example.com:5000/v3
    export OS_VOLUME_API_VERSION=3

If OS_VOLUME_API_VERSION is not set, the highest version
supported by the server will be used.

If OS_VOLUME_API_VERSION exceeds the highest version
supported by the server, the highest version supported by
both the client and server will be used.  A warning
message is printed when this occurs.

From there, all shell commands take the form::

    cinder <command> [arguments...]

Run :program:`cinder help` to get a full list of all possible commands,
and run :program:`cinder help <command>` to get detailed help for that
command.
