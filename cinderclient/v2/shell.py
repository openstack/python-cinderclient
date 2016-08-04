# Copyright (c) 2013-2014 OpenStack Foundation
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from cinderclient.v3.shell import *  # flake8: noqa
from cinderclient import utils

utils.retype_method('volumev3', 'volumev2', globals())

# Below is shameless hack for unit tests
# TODO remove after deciding if unit tests are moved to /v3/ dir

def _treeizeAvailabilityZone(zone):
    """Builds a tree view for availability zones."""
    AvailabilityZone = availability_zones.AvailabilityZone

    az = AvailabilityZone(zone.manager,
                          copy.deepcopy(zone._info), zone._loaded)
    result = []

    # Zone tree view item
    az.zoneName = zone.zoneName
    az.zoneState = ('available'
                    if zone.zoneState['available'] else 'not available')
    az._info['zoneName'] = az.zoneName
    az._info['zoneState'] = az.zoneState
    result.append(az)

    if getattr(zone, "hosts", None) and zone.hosts is not None:
        for (host, services) in zone.hosts.items():
            # Host tree view item
            az = AvailabilityZone(zone.manager,
                                  copy.deepcopy(zone._info), zone._loaded)
            az.zoneName = '|- %s' % host
            az.zoneState = ''
            az._info['zoneName'] = az.zoneName
            az._info['zoneState'] = az.zoneState
            result.append(az)

            for (svc, state) in services.items():
                # Service tree view item
                az = AvailabilityZone(zone.manager,
                                      copy.deepcopy(zone._info), zone._loaded)
                az.zoneName = '| |- %s' % svc
                az.zoneState = '%s %s %s' % (
                               'enabled' if state['active'] else 'disabled',
                               ':-)' if state['available'] else 'XXX',
                               state['updated_at'])
                az._info['zoneName'] = az.zoneName
                az._info['zoneState'] = az.zoneState
                result.append(az)
    return result


# TODO(e0ne): remove copy-paste of this function in a next cinderclient release
def _print_volume_image(image):
    utils.print_dict(image[1]['os-volume_upload_image'])


@utils.arg('volume',
           metavar='<volume>',
           help='Name or ID of volume to snapshot.')
@utils.arg('--force',
           metavar='<True|False>',
           const=True,
           nargs='?',
           default=False,
           help='Enables or disables upload of '
           'a volume that is attached to an instance. '
           'Default=False. '
           'This option may not be supported by your cloud.')
@utils.arg('--container-format',
           metavar='<container-format>',
           default='bare',
           help='Container format type. '
                'Default is bare.')
@utils.arg('--container_format',
           help=argparse.SUPPRESS)
@utils.arg('--disk-format',
           metavar='<disk-format>',
           default='raw',
           help='Disk format type. '
                'Default is raw.')
@utils.arg('--disk_format',
           help=argparse.SUPPRESS)
@utils.arg('image_name',
           metavar='<image-name>',
           help='The new image name.')
@utils.arg('--image_name',
           help=argparse.SUPPRESS)
@utils.service_type('volumev2')
def do_upload_to_image(cs, args):
    """Uploads volume to Image Service as an image."""
    volume = utils.find_volume(cs, args.volume)
    _print_volume_image(volume.upload_to_image(args.force,
                                               args.image_name,
                                               args.container_format,
                                               args.disk_format))

@utils.arg('host',
           metavar='<host>',
           help='Cinder host on which to list manageable volumes; '
                'takes the form: host@backend-name#pool')
@utils.arg('--detailed',
           metavar='<detailed>',
           default=True,
           help='Returned detailed information (default true).')
@utils.arg('--marker',
           metavar='<marker>',
           default=None,
           help='Begin returning volumes that appear later in the volume '
                'list than that represented by this volume id. '
                'Default=None.')
@utils.arg('--limit',
           metavar='<limit>',
           default=None,
           help='Maximum number of volumes to return. Default=None.')
@utils.arg('--offset',
           metavar='<offset>',
           default=None,
           help='Number of volumes to skip after marker. Default=None.')
@utils.arg('--sort',
           metavar='<key>[:<direction>]',
           default=None,
           help=(('Comma-separated list of sort keys and directions in the '
                  'form of <key>[:<asc|desc>]. '
                  'Valid keys: %s. '
                  'Default=None.') % ', '.join(base.SORT_KEY_VALUES)))
@utils.service_type('volumev2')
def do_manageable_list(cs, args):
    """Lists all manageable volumes."""
    detailed = strutils.bool_from_string(args.detailed)
    volumes = cs.volumes.list_manageable(host=args.host, detailed=detailed,
                                         marker=args.marker, limit=args.limit,
                                         offset=args.offset, sort=args.sort)
    columns = ['reference', 'size', 'safe_to_manage']
    if detailed:
        columns.extend(['reason_not_safe', 'cinder_id', 'extra_info'])
    utils.print_list(volumes, columns, sortby_index=None)


@utils.arg('host',
           metavar='<host>',
           help='Cinder host on which to list manageable snapshots; '
                'takes the form: host@backend-name#pool')
@utils.arg('--detailed',
           metavar='<detailed>',
           default=True,
           help='Returned detailed information (default true).')
@utils.arg('--marker',
           metavar='<marker>',
           default=None,
           help='Begin returning volumes that appear later in the volume '
                'list than that represented by this volume id. '
                'Default=None.')
@utils.arg('--limit',
           metavar='<limit>',
           default=None,
           help='Maximum number of volumes to return. Default=None.')
@utils.arg('--offset',
           metavar='<offset>',
           default=None,
           help='Number of volumes to skip after marker. Default=None.')
@utils.arg('--sort',
           metavar='<key>[:<direction>]',
           default=None,
           help=(('Comma-separated list of sort keys and directions in the '
                  'form of <key>[:<asc|desc>]. '
                  'Valid keys: %s. '
                  'Default=None.') % ', '.join(base.SORT_KEY_VALUES)))
@utils.service_type('volumev2')
def do_snapshot_manageable_list(cs, args):
    """Lists all manageable snapshots."""
    detailed = strutils.bool_from_string(args.detailed)
    snapshots = cs.volume_snapshots.list_manageable(host=args.host,
                                                    detailed=detailed,
                                                    marker=args.marker,
                                                    limit=args.limit,
                                                    offset=args.offset,
                                                    sort=args.sort)
    columns = ['reference', 'size', 'safe_to_manage', 'source_reference']
    if detailed:
        columns.extend(['reason_not_safe', 'cinder_id', 'extra_info'])
    utils.print_list(snapshots, columns, sortby_index=None)
