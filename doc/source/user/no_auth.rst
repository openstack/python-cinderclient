============
Using noauth
============

Cinder Server side API setup
============================
The changes in the cinder.conf on your cinder-api node
are minimal, just set authstrategy to noauth::

    [DEFAULT]
    auth_strategy = noauth
    ...

Using cinderclient
------------------
To use the cinderclient you'll need to set the following env variables::

    OS_AUTH_TYPE=noauth
    CINDER_ENDPOINT=http://<cinder-api-url>:8776/v3
    OS_PROJECT_ID=foo
    OS_VOLUME_API_VERSION=3.10

Note that you can have multiple projects, however we don't currently do
any sort of authentication of ownership because, well that's the whole
point, it's noauth.

Each of these options can also be specified on the cmd line::

    cinder --os-auth-type=noauth \
    --os-endpoint=http://<cinder-api-url>:8776/v3 \
    --os-project-id=admin \
    --os-volume-api-version=3.10 list
