# Copyright 2013 OpenStack LLC.
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

from __future__ import print_function

import argparse
import copy
import os
import sys
import time

import six

from cinderclient import exceptions
from cinderclient import utils
from cinderclient.v2 import availability_zones


def _poll_for_status(poll_fn, obj_id, action, final_ok_states,
                     poll_period=5, show_progress=True):
    """Block while action is performed, periodically printing progress."""
    def print_progress(progress):
        if show_progress:
            msg = ('\rInstance %(action)s... %(progress)s%% complete'
                   % dict(action=action, progress=progress))
        else:
            msg = '\rInstance %(action)s...' % dict(action=action)

        sys.stdout.write(msg)
        sys.stdout.flush()

    print()
    while True:
        obj = poll_fn(obj_id)
        status = obj.status.lower()
        progress = getattr(obj, 'progress', None) or 0
        if status in final_ok_states:
            print_progress(100)
            print("\nFinished")
            break
        elif status == "error":
            print("\nError %(action)s instance" % {'action': action})
            break
        else:
            print_progress(progress)
            time.sleep(poll_period)


def _find_volume(cs, volume):
    """Get a volume by ID."""
    return utils.find_resource(cs.volumes, volume)


def _find_volume_snapshot(cs, snapshot):
    """Get a volume snapshot by ID."""
    return utils.find_resource(cs.volume_snapshots, snapshot)


def _find_backup(cs, backup):
    """Get a backup by ID."""
    return utils.find_resource(cs.backups, backup)


def _find_transfer(cs, transfer):
    """Get a transfer by ID."""
    return utils.find_resource(cs.transfers, transfer)


def _print_volume_snapshot(snapshot):
    utils.print_dict(snapshot._info)


def _print_volume_image(image):
    utils.print_dict(image[1]['os-volume_upload_image'])


def _translate_keys(collection, convert):
    for item in collection:
        keys = list(item.__dict__.keys())
        for from_key, to_key in convert:
            if from_key in keys and to_key not in keys:
                setattr(item, to_key, item._info[from_key])


def _translate_volume_keys(collection):
    convert = [('volumeType', 'volume_type')]
    _translate_keys(collection, convert)


def _translate_volume_snapshot_keys(collection):
    convert = [('volumeId', 'volume_id')]
    _translate_keys(collection, convert)


def _translate_availability_zone_keys(collection):
    convert = [('zoneName', 'name'), ('zoneState', 'status')]
    _translate_keys(collection, convert)


def _extract_metadata(args):
    metadata = {}
    for metadatum in args.metadata[0]:
        # unset doesn't require a val, so we have the if/else
        if '=' in metadatum:
            (key, value) = metadatum.split('=', 1)
        else:
            key = metadatum
            value = None

        metadata[key] = value
    return metadata


@utils.arg('--all-tenants',
           dest='all_tenants',
           metavar='<0|1>',
           nargs='?',
           type=int,
           const=1,
           default=0,
           help='Display information from all tenants (Admin only).')
@utils.arg('--all_tenants',
           nargs='?',
           type=int,
           const=1,
           help=argparse.SUPPRESS)
@utils.arg('--name',
           metavar='<name>',
           default=None,
           help='Filter results by name')
@utils.arg('--display-name',
           help=argparse.SUPPRESS)
@utils.arg('--status',
           metavar='<status>',
           default=None,
           help='Filter results by status')
@utils.service_type('volume')
def do_list(cs, args):
    """List all the volumes."""
    # NOTE(thingee): Backwards-compatibility with v1 args
    if args.display_name is not None:
        args.name = args.display_name

    all_tenants = int(os.environ.get("ALL_TENANTS", args.all_tenants))
    search_opts = {
        'all_tenants': all_tenants,
        'name': args.name,
        'status': args.status,
    }
    volumes = cs.volumes.list(search_opts=search_opts)
    _translate_volume_keys(volumes)

    # Create a list of servers to which the volume is attached
    for vol in volumes:
        servers = [s.get('server_id') for s in vol.attachments]
        setattr(vol, 'attached_to', ','.join(map(str, servers)))

    utils.print_list(volumes, ['ID', 'Status', 'Name',
                     'Size', 'Volume Type', 'Bootable', 'Attached to'])


@utils.arg('volume',
           metavar='<volume>',
           help='ID of the volume.')
@utils.service_type('volume')
def do_show(cs, args):
    """Show details about a volume."""
    info = dict()
    volume = _find_volume(cs, args.volume)
    info.update(volume._info)

    info.pop('links', None)
    utils.print_dict(info)


@utils.arg('size',
           metavar='<size>',
           type=int,
           help='Size of volume in GB')
@utils.arg('--snapshot-id',
           metavar='<snapshot-id>',
           default=None,
           help='Create volume from snapshot id (Optional, Default=None)')
@utils.arg('--snapshot_id',
           help=argparse.SUPPRESS)
@utils.arg('--source-volid',
           metavar='<source-volid>',
           default=None,
           help='Create volume from volume id (Optional, Default=None)')
@utils.arg('--source_volid',
           help=argparse.SUPPRESS)
@utils.arg('--image-id',
           metavar='<image-id>',
           default=None,
           help='Create volume from image id (Optional, Default=None)')
@utils.arg('--image_id',
           help=argparse.SUPPRESS)
@utils.arg('--name',
           metavar='<name>',
           default=None,
           help='Volume name (Optional, Default=None)')
@utils.arg('--display-name',
           help=argparse.SUPPRESS)
@utils.arg('--display_name',
           help=argparse.SUPPRESS)
@utils.arg('--description',
           metavar='<description>',
           default=None,
           help='Volume description (Optional, Default=None)')
@utils.arg('--display-description',
           help=argparse.SUPPRESS)
@utils.arg('--display_description',
           help=argparse.SUPPRESS)
@utils.arg('--volume-type',
           metavar='<volume-type>',
           default=None,
           help='Volume type (Optional, Default=None)')
@utils.arg('--volume_type',
           help=argparse.SUPPRESS)
@utils.arg('--availability-zone',
           metavar='<availability-zone>',
           default=None,
           help='Availability zone for volume (Optional, Default=None)')
@utils.arg('--availability_zone',
           help=argparse.SUPPRESS)
@utils.arg('--metadata',
           type=str,
           nargs='*',
           metavar='<key=value>',
           help='Metadata key=value pairs (Optional, Default=None)',
           default=None)
@utils.arg('--hint',
           metavar='<key=value>',
           dest='scheduler_hints',
           action='append',
           default=[],
           help='Scheduler hint like in nova')
@utils.service_type('volume')
def do_create(cs, args):
    """Add a new volume."""
    # NOTE(thingee): Backwards-compatibility with v1 args
    if args.display_name is not None:
        args.name = args.display_name

    if args.display_description is not None:
        args.description = args.display_description

    volume_metadata = None
    if args.metadata is not None:
        volume_metadata = _extract_metadata(args)

    #NOTE(N.S.): take this piece from novaclient
    hints = {}
    if args.scheduler_hints:
        for hint in args.scheduler_hints:
            key, _sep, value = hint.partition('=')
            # NOTE(vish): multiple copies of the same hint will
            #             result in a list of values
            if key in hints:
                if isinstance(hints[key], six.string_types):
                    hints[key] = [hints[key]]
                hints[key] += [value]
            else:
                hints[key] = value
    #NOTE(N.S.): end of the taken piece

    volume = cs.volumes.create(args.size,
                               args.snapshot_id,
                               args.source_volid,
                               args.name,
                               args.description,
                               args.volume_type,
                               availability_zone=args.availability_zone,
                               imageRef=args.image_id,
                               metadata=volume_metadata,
                               scheduler_hints=hints)

    info = dict()
    volume = cs.volumes.get(volume.id)
    info.update(volume._info)

    info.pop('links', None)
    utils.print_dict(info)


@utils.arg('volume',
           metavar='<volume>',
           help='ID of the volume to delete.')
@utils.service_type('volume')
def do_delete(cs, args):
    """Remove a volume."""
    volume = _find_volume(cs, args.volume)
    volume.delete()


@utils.arg('volume',
           metavar='<volume>',
           help='ID of the volume to delete.')
@utils.service_type('volume')
def do_force_delete(cs, args):
    """Attempt forced removal of a volume, regardless of its state."""
    volume = _find_volume(cs, args.volume)
    volume.force_delete()


@utils.arg('volume', metavar='<volume>', help='ID of the volume to modify.')
@utils.arg('--state', metavar='<state>', default='available',
           help=('Indicate which state to assign the volume. Options include '
                 'available, error, creating, deleting, error_deleting. If no '
                 'state is provided, available will be used.'))
@utils.service_type('volume')
def do_reset_state(cs, args):
    """Explicitly update the state of a volume."""
    volume = _find_volume(cs, args.volume)
    volume.reset_state(args.state)


@utils.arg('volume',
           metavar='<volume>',
           help='ID of the volume to rename.')
@utils.arg('name',
           nargs='?',
           metavar='<name>',
           help='New name for the volume.')
@utils.arg('--description', metavar='<description>',
           help='Optional volume description. (Default=None)',
           default=None)
@utils.arg('--display-description',
           help=argparse.SUPPRESS)
@utils.arg('--display_description',
           help=argparse.SUPPRESS)
@utils.service_type('volume')
def do_rename(cs, args):
    """Rename a volume."""
    kwargs = {}

    if args.name is not None:
        kwargs['name'] = args.name
    if args.display_description is not None:
        kwargs['description'] = args.display_description
    elif args.description is not None:
        kwargs['description'] = args.description

    _find_volume(cs, args.volume).update(**kwargs)


@utils.arg('volume',
           metavar='<volume>',
           help='ID of the volume to update metadata on.')
@utils.arg('action',
           metavar='<action>',
           choices=['set', 'unset'],
           help="Actions: 'set' or 'unset'")
@utils.arg('metadata',
           metavar='<key=value>',
           nargs='+',
           action='append',
           default=[],
           help='Metadata to set/unset (only key is necessary on unset)')
@utils.service_type('volume')
def do_metadata(cs, args):
    """Set or Delete metadata on a volume."""
    volume = _find_volume(cs, args.volume)
    metadata = _extract_metadata(args)

    if args.action == 'set':
        cs.volumes.set_metadata(volume, metadata)
    elif args.action == 'unset':
        cs.volumes.delete_metadata(volume, list(metadata.keys()))


@utils.arg('--all-tenants',
           dest='all_tenants',
           metavar='<0|1>',
           nargs='?',
           type=int,
           const=1,
           default=0,
           help='Display information from all tenants (Admin only).')
@utils.arg('--all_tenants',
           nargs='?',
           type=int,
           const=1,
           help=argparse.SUPPRESS)
@utils.arg('--name',
           metavar='<name>',
           default=None,
           help='Filter results by name')
@utils.arg('--display-name',
           help=argparse.SUPPRESS)
@utils.arg('--display_name',
           help=argparse.SUPPRESS)
@utils.arg('--status',
           metavar='<status>',
           default=None,
           help='Filter results by status')
@utils.arg('--volume-id',
           metavar='<volume-id>',
           default=None,
           help='Filter results by volume-id')
@utils.arg('--volume_id',
           help=argparse.SUPPRESS)
@utils.service_type('volume')
def do_snapshot_list(cs, args):
    """List all the snapshots."""
    all_tenants = int(os.environ.get("ALL_TENANTS", args.all_tenants))

    if args.display_name is not None:
        args.name = args.display_name

    search_opts = {
        'all_tenants': all_tenants,
        'display_name': args.name,
        'status': args.status,
        'volume_id': args.volume_id,
    }

    snapshots = cs.volume_snapshots.list(search_opts=search_opts)
    _translate_volume_snapshot_keys(snapshots)
    utils.print_list(snapshots,
                     ['ID', 'Volume ID', 'Status', 'Name', 'Size'])


@utils.arg('snapshot',
           metavar='<snapshot>',
           help='ID of the snapshot.')
@utils.service_type('volume')
def do_snapshot_show(cs, args):
    """Show details about a snapshot."""
    snapshot = _find_volume_snapshot(cs, args.snapshot)
    _print_volume_snapshot(snapshot)


@utils.arg('volume-id',
           metavar='<volume-id>',
           help='ID of the volume to snapshot')
@utils.arg('--force',
           metavar='<True|False>',
           help='Optional flag to indicate whether '
           'to snapshot a volume even if it\'s '
           'attached to an instance. (Default=False)',
           default=False)
@utils.arg('--name',
           metavar='<name>',
           default=None,
           help='Optional snapshot name. (Default=None)')
@utils.arg('--display-name',
           help=argparse.SUPPRESS)
@utils.arg('--display_name',
           help=argparse.SUPPRESS)
@utils.arg('--description',
           metavar='<description>',
           default=None,
           help='Optional snapshot description. (Default=None)')
@utils.arg('--display-description',
           help=argparse.SUPPRESS)
@utils.arg('--display_description',
           help=argparse.SUPPRESS)
@utils.service_type('volume')
def do_snapshot_create(cs, args):
    """Add a new snapshot."""
    if args.display_name is not None:
        args.name = args.display_name

    if args.display_description is not None:
        args.description = args.display_description

    snapshot = cs.volume_snapshots.create(args.volume_id,
                                          args.force,
                                          args.name,
                                          args.description)
    _print_volume_snapshot(snapshot)


@utils.arg('snapshot-id',
           metavar='<snapshot-id>',
           help='ID of the snapshot to delete.')
@utils.service_type('volume')
def do_snapshot_delete(cs, args):
    """Remove a snapshot."""
    snapshot = _find_volume_snapshot(cs, args.snapshot_id)
    snapshot.delete()


@utils.arg('snapshot', metavar='<snapshot>', help='ID of the snapshot.')
@utils.arg('name', nargs='?', metavar='<name>',
           help='New name for the snapshot.')
@utils.arg('--description', metavar='<description>',
           help='Optional snapshot description. (Default=None)',
           default=None)
@utils.arg('--display-description',
           help=argparse.SUPPRESS)
@utils.arg('--display_description',
           help=argparse.SUPPRESS)
@utils.service_type('volume')
def do_snapshot_rename(cs, args):
    """Rename a snapshot."""
    kwargs = {}

    if args.name is not None:
        kwargs['name'] = args.name

    if args.description is not None:
        kwargs['description'] = args.description
    elif args.display_description is not None:
        kwargs['description'] = args.display_description

    _find_volume_snapshot(cs, args.snapshot).update(**kwargs)


@utils.arg('snapshot', metavar='<snapshot>',
           help='ID of the snapshot to modify.')
@utils.arg('--state', metavar='<state>',
           default='available',
           help=('Indicate which state to assign the snapshot. '
                 'Options include available, error, creating, '
                 'deleting, error_deleting. If no state is provided, '
                 'available will be used.'))
@utils.service_type('snapshot')
def do_snapshot_reset_state(cs, args):
    """Explicitly update the state of a snapshot."""
    snapshot = _find_volume_snapshot(cs, args.snapshot)
    snapshot.reset_state(args.state)


def _print_volume_type_list(vtypes):
    utils.print_list(vtypes, ['ID', 'Name'])


def _print_type_and_extra_specs_list(vtypes):
    formatters = {'extra_specs': _print_type_extra_specs}
    utils.print_list(vtypes, ['ID', 'Name', 'extra_specs'], formatters)


@utils.service_type('volume')
def do_type_list(cs, args):
    """Print a list of available 'volume types'."""
    vtypes = cs.volume_types.list()
    _print_volume_type_list(vtypes)


@utils.service_type('volume')
def do_extra_specs_list(cs, args):
    """Print a list of current 'volume types and extra specs' (Admin Only)."""
    vtypes = cs.volume_types.list()
    _print_type_and_extra_specs_list(vtypes)


@utils.arg('name',
           metavar='<name>',
           help="Name of the new volume type")
@utils.service_type('volume')
def do_type_create(cs, args):
    """Create a new volume type."""
    vtype = cs.volume_types.create(args.name)
    _print_volume_type_list([vtype])


@utils.arg('id',
           metavar='<id>',
           help="Unique ID of the volume type to delete")
@utils.service_type('volume')
def do_type_delete(cs, args):
    """Delete a specific volume type."""
    cs.volume_types.delete(args.id)


@utils.arg('vtype',
           metavar='<vtype>',
           help="Name or ID of the volume type")
@utils.arg('action',
           metavar='<action>',
           choices=['set', 'unset'],
           help="Actions: 'set' or 'unset'")
@utils.arg('metadata',
           metavar='<key=value>',
           nargs='+',
           action='append',
           default=[],
           help='Extra_specs to set/unset (only key is necessary on unset)')
@utils.service_type('volume')
def do_type_key(cs, args):
    "Set or unset extra_spec for a volume type."""
    vtype = _find_volume_type(cs, args.vtype)
    keypair = _extract_metadata(args)

    if args.action == 'set':
        vtype.set_keys(keypair)
    elif args.action == 'unset':
        vtype.unset_keys(list(keypair.keys()))


def do_endpoints(cs, args):
    """Discover endpoints that get returned from the authenticate services."""
    catalog = cs.client.service_catalog.catalog
    for e in catalog['access']['serviceCatalog']:
        utils.print_dict(e['endpoints'][0], e['name'])


def do_credentials(cs, args):
    """Show user credentials returned from auth."""
    catalog = cs.client.service_catalog.catalog
    utils.print_dict(catalog['access']['user'], "User Credentials")
    utils.print_dict(catalog['access']['token'], "Token")


_quota_resources = ['volumes', 'snapshots', 'gigabytes']


def _quota_show(quotas):
    quota_dict = {}
    for resource in quotas._info.keys():
        good_name = False
        for name in _quota_resources:
            if resource.startswith(name):
                good_name = True
        if not good_name:
            continue
        quota_dict[resource] = getattr(quotas, resource, None)
    utils.print_dict(quota_dict)


def _quota_update(manager, identifier, args):
    updates = {}
    for resource in _quota_resources:
        val = getattr(args, resource, None)
        if val is not None:
            if args.volume_type:
                resource = resource + '_%s' % args.volume_type
            updates[resource] = val

    if updates:
        manager.update(identifier, **updates)


@utils.arg('tenant',
           metavar='<tenant_id>',
           help='UUID of tenant to list the quotas for.')
@utils.service_type('volume')
def do_quota_show(cs, args):
    """List the quotas for a tenant."""

    _quota_show(cs.quotas.get(args.tenant))


@utils.arg('tenant',
           metavar='<tenant_id>',
           help='UUID of tenant to list the default quotas for.')
@utils.service_type('volume')
def do_quota_defaults(cs, args):
    """List the default quotas for a tenant."""

    _quota_show(cs.quotas.defaults(args.tenant))


@utils.arg('tenant',
           metavar='<tenant_id>',
           help='UUID of tenant to set the quotas for.')
@utils.arg('--volumes',
           metavar='<volumes>',
           type=int, default=None,
           help='New value for the "volumes" quota.')
@utils.arg('--snapshots',
           metavar='<snapshots>',
           type=int, default=None,
           help='New value for the "snapshots" quota.')
@utils.arg('--gigabytes',
           metavar='<gigabytes>',
           type=int, default=None,
           help='New value for the "gigabytes" quota.')
@utils.arg('--volume-type',
           metavar='<volume_type_name>',
           default=None,
           help='Volume type (Optional, Default=None)')
@utils.service_type('volume')
def do_quota_update(cs, args):
    """Update the quotas for a tenant."""

    _quota_update(cs.quotas, args.tenant, args)


@utils.arg('class_name',
           metavar='<class>',
           help='Name of quota class to list the quotas for.')
@utils.service_type('volume')
def do_quota_class_show(cs, args):
    """List the quotas for a quota class."""

    _quota_show(cs.quota_classes.get(args.class_name))


@utils.arg('class-name',
           metavar='<class-name>',
           help='Name of quota class to set the quotas for.')
@utils.arg('--volumes',
           metavar='<volumes>',
           type=int, default=None,
           help='New value for the "volumes" quota.')
@utils.arg('--snapshots',
           metavar='<snapshots>',
           type=int, default=None,
           help='New value for the "snapshots" quota.')
@utils.arg('--gigabytes',
           metavar='<gigabytes>',
           type=int, default=None,
           help='New value for the "gigabytes" quota.')
@utils.arg('--volume-type',
           metavar='<volume_type_name>',
           default=None,
           help='Volume type (Optional, Default=None)')
@utils.service_type('volume')
def do_quota_class_update(cs, args):
    """Update the quotas for a quota class."""

    _quota_update(cs.quota_classes, args.class_name, args)


@utils.service_type('volume')
def do_absolute_limits(cs, args):
    """Print a list of absolute limits for a user"""
    limits = cs.limits.get().absolute
    columns = ['Name', 'Value']
    utils.print_list(limits, columns)


@utils.service_type('volume')
def do_rate_limits(cs, args):
    """Print a list of rate limits for a user"""
    limits = cs.limits.get().rate
    columns = ['Verb', 'URI', 'Value', 'Remain', 'Unit', 'Next_Available']
    utils.print_list(limits, columns)


def _print_type_extra_specs(vol_type):
    try:
        return vol_type.get_keys()
    except exceptions.NotFound:
        return "N/A"


def _find_volume_type(cs, vtype):
    """Get a volume type by name or ID."""
    return utils.find_resource(cs.volume_types, vtype)


@utils.arg('volume-id',
           metavar='<volume-id>',
           help='ID of the volume to snapshot')
@utils.arg('--force',
           metavar='<True|False>',
           help='Optional flag to indicate whether '
           'to upload a volume even if it\'s '
           'attached to an instance. (Default=False)',
           default=False)
@utils.arg('--container-format',
           metavar='<container-format>',
           help='Optional type for container format '
           '(Default=bare)',
           default='bare')
@utils.arg('--container_format',
           help=argparse.SUPPRESS)
@utils.arg('--disk-format',
           metavar='<disk-format>',
           help='Optional type for disk format '
           '(Default=raw)',
           default='raw')
@utils.arg('--disk_format',
           help=argparse.SUPPRESS)
@utils.arg('image-name',
           metavar='<image-name>',
           help='Name for created image')
@utils.arg('--image_name',
           help=argparse.SUPPRESS)
@utils.service_type('volume')
def do_upload_to_image(cs, args):
    """Upload volume to image service as image."""
    volume = _find_volume(cs, args.volume_id)
    _print_volume_image(volume.upload_to_image(args.force,
                                               args.image_name,
                                               args.container_format,
                                               args.disk_format))


@utils.arg('volume', metavar='<volume>',
           help='ID of the volume to backup.')
@utils.arg('--container', metavar='<container>',
           help='Optional backup container name. (Default=None)',
           default=None)
@utils.arg('--display-name',
           help=argparse.SUPPRESS)
@utils.arg('--name', metavar='<name>',
           help='Optional backup name. (Default=None)',
           default=None)
@utils.arg('--display-description',
           help=argparse.SUPPRESS)
@utils.arg('--description',
           metavar='<description>',
           default=None,
           help='Options backup description (Default=None)')
@utils.service_type('volume')
def do_backup_create(cs, args):
    """Creates a backup."""
    if args.display_name is not None:
        args.name = args.display_name

    if args.display_description is not None:
        args.description = args.display_description

    cs.backups.create(args.volume,
                      args.container,
                      args.name,
                      args.description)


@utils.arg('backup', metavar='<backup>', help='ID of the backup.')
@utils.service_type('volume')
def do_backup_show(cs, args):
    """Show details about a backup."""
    backup = _find_backup(cs, args.backup)
    info = dict()
    info.update(backup._info)

    info.pop('links', None)
    utils.print_dict(info)


@utils.service_type('volume')
def do_backup_list(cs, args):
    """List all the backups."""
    backups = cs.backups.list()
    columns = ['ID', 'Volume ID', 'Status', 'Name', 'Size', 'Object Count',
               'Container']
    utils.print_list(backups, columns)


@utils.arg('backup', metavar='<backup>',
           help='ID of the backup to delete.')
@utils.service_type('volume')
def do_backup_delete(cs, args):
    """Remove a backup."""
    backup = _find_backup(cs, args.backup)
    backup.delete()


@utils.arg('backup', metavar='<backup>',
           help='ID of the backup to restore.')
@utils.arg('--volume-id', metavar='<volume-id>',
           help='Optional ID of the volume to restore to.',
           default=None)
@utils.service_type('volume')
def do_backup_restore(cs, args):
    """Restore a backup."""
    cs.restores.restore(args.backup,
                        args.volume_id)


@utils.arg('volume', metavar='<volume>',
           help='ID of the volume to transfer.')
@utils.arg('--name',
           metavar='<name>',
           default=None,
           help='Optional transfer name. (Default=None)')
@utils.arg('--display-name',
           help=argparse.SUPPRESS)
@utils.service_type('volume')
def do_transfer_create(cs, args):
    """Creates a volume transfer."""
    if args.display_name is not None:
        args.name = args.display_name

    transfer = cs.transfers.create(args.volume,
                                   args.name)
    info = dict()
    info.update(transfer._info)

    info.pop('links', None)
    utils.print_dict(info)


@utils.arg('transfer', metavar='<transfer>',
           help='ID of the transfer to delete.')
@utils.service_type('volume')
def do_transfer_delete(cs, args):
    """Undo a transfer."""
    transfer = _find_transfer(cs, args.transfer)
    transfer.delete()


@utils.arg('transfer', metavar='<transfer>',
           help='ID of the transfer to accept.')
@utils.arg('auth_key', metavar='<auth_key>',
           help='Auth key of the transfer to accept.')
@utils.service_type('volume')
def do_transfer_accept(cs, args):
    """Accepts a volume transfer."""
    transfer = cs.transfers.accept(args.transfer, args.auth_key)
    info = dict()
    info.update(transfer._info)

    info.pop('links', None)
    utils.print_dict(info)


@utils.service_type('volume')
def do_transfer_list(cs, args):
    """List all the transfers."""
    transfers = cs.transfers.list()
    columns = ['ID', 'Volume ID', 'Name']
    utils.print_list(transfers, columns)


@utils.arg('transfer', metavar='<transfer>',
           help='ID of the transfer to accept.')
@utils.service_type('volume')
def do_transfer_show(cs, args):
    """Show details about a transfer."""
    transfer = _find_transfer(cs, args.transfer)
    info = dict()
    info.update(transfer._info)

    info.pop('links', None)
    utils.print_dict(info)


@utils.arg('volume', metavar='<volume>', help='ID of the volume to extend.')
@utils.arg('new-size',
           metavar='<new_size>',
           type=int,
           help='New size of volume in GB')
@utils.service_type('volume')
def do_extend(cs, args):
    """Attempt to extend the size of an existing volume."""
    volume = _find_volume(cs, args.volume)
    cs.volumes.extend(volume, args.new_size)


@utils.arg('--host', metavar='<hostname>', default=None,
           help='Name of host.')
@utils.arg('--binary', metavar='<binary>', default=None,
           help='Service binary.')
@utils.service_type('volume')
def do_service_list(cs, args):
    """List all the services. Filter by host & service binary."""
    result = cs.services.list(host=args.host, binary=args.binary)
    columns = ["Binary", "Host", "Zone", "Status", "State", "Updated_at"]
    utils.print_list(result, columns)


@utils.arg('host', metavar='<hostname>', help='Name of host.')
@utils.arg('binary', metavar='<binary>', help='Service binary.')
@utils.service_type('volume')
def do_service_enable(cs, args):
    """Enable the service."""
    cs.services.enable(args.host, args.binary)


@utils.arg('host', metavar='<hostname>', help='Name of host.')
@utils.arg('binary', metavar='<binary>', help='Service binary.')
@utils.service_type('volume')
def do_service_disable(cs, args):
    """Disable the service."""
    cs.services.disable(args.host, args.binary)


def _treeizeAvailabilityZone(zone):
    """Build a tree view for availability zones."""
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


@utils.service_type('volume')
def do_availability_zone_list(cs, _args):
    """List all the availability zones."""
    try:
        availability_zones = cs.availability_zones.list()
    except exceptions.Forbidden as e:  # policy doesn't allow probably
        try:
            availability_zones = cs.availability_zones.list(detailed=False)
        except Exception:
            raise e

    result = []
    for zone in availability_zones:
        result += _treeizeAvailabilityZone(zone)
    _translate_availability_zone_keys(result)
    utils.print_list(result, ['Name', 'Status'])
