from cinderclient import client
from cinderclient.v1 import volumes
from cinderclient.v1 import volume_snapshots
from cinderclient.v1 import volume_types


class Client(object):
    """
    Top-level object to access the OpenStack Compute API.

    Create an instance with your creds::

        >>> client = Client(USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)

    Then call methods on its managers::

        >>> client.servers.list()
        ...
        >>> client.flavors.list()
        ...

    """

    # FIXME(jesse): project_id isn't required to authenticate
    def __init__(self, username, api_key, project_id, auth_url,
                 insecure=False, timeout=None, proxy_tenant_id=None,
                 proxy_token=None, region_name=None,
                 endpoint_type='publicURL', extensions=None,
                 service_type='compute', service_name=None,
                 volume_service_name=None):
        # FIXME(comstud): Rename the api_key argument above when we
        # know it's not being used as keyword argument
        password = api_key

        # extensions
        self.volumes = volumes.VolumeManager(self)
        self.volume_snapshots = volume_snapshots.SnapshotManager(self)
        self.volume_types = volume_types.VolumeTypeManager(self)

        # Add in any extensions...
        if extensions:
            for extension in extensions:
                if extension.manager_class:
                    setattr(self, extension.name,
                            extension.manager_class(self))

        self.client = client.HTTPClient(
            username,
            password,
            project_id,
            auth_url,
            insecure=insecure,
            timeout=timeout,
            proxy_token=proxy_token,
            proxy_tenant_id=proxy_tenant_id,
            region_name=region_name,
            endpoint_type=endpoint_type,
            service_type=service_type,
            service_name=service_name,
            volume_service_name=volume_service_name)

    def authenticate(self):
        """
        Authenticate against the server.

        Normally this is called automatically when you first access the API,
        but you can call this method to force authentication right now.

        Returns on success; raises :exc:`exceptions.Unauthorized` if the
        credentials are wrong.
        """
        self.client.authenticate()
