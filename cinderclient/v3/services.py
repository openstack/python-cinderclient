# Copyright (c) 2013 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
service interface
"""

from cinderclient import api_versions
from cinderclient.v2 import services

Service = services.Service


class ServiceManager(services.ServiceManager):
    @api_versions.wraps("3.0")
    def server_api_version(self, url_append=""):
        """Returns the API Version supported by the server.

        :param url_append: String to append to url to obtain specific version
        :return: Returns response obj for a server that supports microversions.
                 Returns an empty list for Liberty and prior Cinder servers.
        """
        try:
            return self._get_with_base_url(url_append, response_key='versions')
        except LookupError:
            return []
