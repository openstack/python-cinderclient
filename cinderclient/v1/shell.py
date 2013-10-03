# Copyright 2010 Jacob Kaplan-Moss

# Copyright (c) 2011 OpenStack Foundation
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

from cinderclient import exceptions
from cinderclient.openstack.common import strutils
from cinderclient import utils
from cinderclient.v1 import availability_zones


def _poll_for_status(poll_fn, obj_id, action, final_ok_states,
                     poll_period=5, show_progress=True):
    """Block while an action is being performed, periodically printing
    progress.
    """
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


def _find_volume_snapshot(cs, snapshot):
    """Get a volume snapshot by name or ID."""
    return utils.find_resource(cs.volume_snapshots, snapshot)


def _find_backup(cs, backup):
    """Get a backup by name or ID."""
    return utils.find_resource(cs.backups, backup)


def _find_transfer(cs, transfer):
    """Get a transfer by name or ID."""
    return utils.find_resource(cs.transfers, transfer)


def _find_qos_specs(cs, qos_specs):
    """Get a qos specs by ID."""
    return utils.find_resource(cs.qos_specs, qos_specs)


def _print_volume(volume):
    utils.print_dict(volume._info)


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
    convert = [('displayName', 'display_name'), ('volumeType', 'volume_type')]
    _translate_keys(collection, convert)


def _translate_volume_snapshot_keys(collection):
    convert = [('displayName', 'display_name'), ('volumeId', 'volume_id')]
    _translate_keys(collection, convert)


def _translate_availability_zone_keys(collection):
    convert = [('zoneName', 'name'), ('zoneState', 'status')]
    _translate_keys(collection, convert)


def _extract_metadata(args):
    metadata = {}
    for metadatum in args.metadata:
        # unset doesn't require a val, so we have the if/else
        if '=' in metadatum:
            (key, value) = metadatum.split('=', 1)
        else:
            key = metadatum
            value = None

        metadata[key] = value
    return metadata


@utils.arg(
    '--all-tenants',
    dest='all_tenants',
    metavar='<0|1>',
    nargs='?',
    type=int,
    const=1,
    default=0,
    help='Display information from all tenants (Admin only).')
@utils.arg(
    '--all_tenants',
    nargs='?',
    type=int,
    const=1,
    help=argparse.SUPPRESS)
@utils.arg(
    '--display-name',
    metavar='<display-name>',
    default=None,
    help='Filter results by display-name')
@utils.arg(
    '--status',
    metavar='<status>',
    default=None,
    help='Filter results by status')
@utils.arg(
    '--metadata',
    type=str,
    nargs='*',
    metavar='<key=value>',
    help='Filter results by metadata',
    default=None)
@utils.service_type('volume')
def do_list(cs, args):
    """List all the volumes."""
    all_tenants = int(os.environ.get("ALL_TENANTS", args.all_tenants))
    search_opts = {
        'all_tenants': all_tenants,
        'display_name': args.display_name,
        'status': args.status,
        'metadata': _extract_metadata(args) if args.metadata else None,
    }
    volumes = cs.volumes.list(search_opts=search_opts)
    _translate_volume_keys(volumes)

    # Create a list of servers to which the volume is attached
    for vol in volumes:
        servers = [s.get('server_id') for s in vol.attachments]
        setattr(vol, 'attached_to', ','.join(map(str, servers)))
    utils.print_list(volumes, ['ID', 'Status', 'Display Name',
                     'Size', 'Volume Type', 'Bootable', 'Attached to'])


@utils.arg('volume', metavar='<volume>', help='Name or ID of the volume.')
@utils.service_type('volume')
def do_show(cs, args):
    """Show details about a volume."""
    volume = utils.find_volume(cs, args.volume)
    _print_volume(volume)


@utils.arg('size',
           metavar='<size>',
           type=int,
           help='Size of volume in GB')
@utils.arg(
    '--snapshot-id',
    metavar='<snapshot-id>',
    default=None,
    help='Create volume from snapshot id (Optional, Default=None)')
@utils.arg(
    '--snapshot_id',
    help=argparse.SUPPRESS)
@utils.arg(
    '--source-volid',
    metavar='<source-volid>',
    default=None,
    help='Create volume from volume id (Optional, Default=None)')
@utils.arg(
    '--source_volid',
    help=argparse.SUPPRESS)
@utils.arg(
    '--image-id',
    metavar='<image-id>',
    default=None,
    help='Create volume from image id (Optional, Default=None)')
@utils.arg(
    '--image_id',
    help=argparse.SUPPRESS)
@utils.arg(
    '--display-name',
    metavar='<display-name>',
    default=None,
    help='Volume name (Optional, Default=None)')
@utils.arg(
    '--display_name',
    help=argparse.SUPPRESS)
@utils.arg(
    '--display-description',
    metavar='<display-description>',
    default=None,
    help='Volume description (Optional, Default=None)')
@utils.arg(
    '--display_description',
    help=argparse.SUPPRESS)
@utils.arg(
    '--volume-type',
    metavar='<volume-type>',
    default=None,
    help='Volume type (Optional, Default=None)')
@utils.arg(
    '--volume_type',
    help=argparse.SUPPRESS)
@utils.arg(
    '--availability-zone',
    metavar='<availability-zone>',
    default=None,
    help='Availability zone for volume (Optional, Default=None)')
@utils.arg(
    '--availability_zone',
    help=argparse.SUPPRESS)
@utils.arg('--metadata',
           type=str,
           nargs='*',
           metavar='<key=value>',
           help='Metadata key=value pairs (Optional, Default=None)',
           default=None)
@utils.service_type('volume')
def do_create(cs, args):
    """Add a new volume."""

    volume_metadata = None
    if args.metadata is not None:
        volume_metadata = _extract_metadata(args)

    volume = cs.volumes.create(args.size,
                               args.snapshot_id,
                               args.source_volid,
                               args.display_name,
                               args.display_description,
                               args.volume_type,
                               availability_zone=args.availability_zone,
                               imageRef=args.image_id,
                               metadata=volume_metadata)
    _print_volume(volume)


@utils.arg('volume', metavar='<volume>',
           help='Name or ID of the volume to delete.')
@utils.service_type('volume')
def do_delete(cs, args):
    """Remove a volume."""
    volume = utils.find_volume(cs, args.volume)
    volume.delete()


@utils.arg('volume', metavar='<volume>',
           help='Name or ID of the volume to delete.')
@utils.service_type('volume')
def do_force_delete(cs, args):
    """Attempt forced removal of a volume, regardless of its state."""
    volume = utils.find_volume(cs, args.volume)
    volume.force_delete()


@utils.arg('volume', metavar='<volume>',
           help='Name or ID of the volume to modify.')
@utils.arg('--state', metavar='<state>', default='available',
           help=('Indicate which state to assign the volume. Options include '
                 'available, error, creating, deleting, error_deleting. If no '
                 'state is provided, available will be used.'))
@utils.service_type('volume')
def do_reset_state(cs, args):
    """Explicitly update the state of a volume."""
    volume = utils.find_volume(cs, args.volume)
    volume.reset_state(args.state)


@utils.arg('volume', metavar='<volume>',
           help='Name or ID of the volume to rename.')
@utils.arg('display_name', nargs='?', metavar='<display-name>',
           help='New display-name for the volume.')
@utils.arg('--display-description', metavar='<display-description>',
           help='Optional volume description. (Default=None)',
           default=None)
@utils.service_type('volume')
def do_rename(cs, args):
    """Rename a volume."""
    kwargs = {}
    if args.display_name is not None:
        kwargs['display_name'] = args.display_name
    if args.display_description is not None:
        kwargs['display_description'] = args.display_description

    if not any(kwargs):
        msg = 'Must supply either display-name or display-description.'
        raise exceptions.ClientException(code=1, message=msg)

    utils.find_volume(cs, args.volume).update(**kwargs)


@utils.arg('volume',
           metavar='<volume>',
           help='Name or ID of the volume to update metadata on.')
@utils.arg('action',
           metavar='<action>',
           choices=['set', 'unset'],
           help="Actions: 'set' or 'unset'")
@utils.arg('metadata',
           metavar='<key=value>',
           nargs='+',
           default=[],
           help='Metadata to set/unset (only key is necessary on unset)')
@utils.service_type('volume')
def do_metadata(cs, args):
    """Set or Delete metadata on a volume."""
    volume = utils.find_volume(cs, args.volume)
    metadata = _extract_metadata(args)

    if args.action == 'set':
        cs.volumes.set_metadata(volume, metadata)
    elif args.action == 'unset':
        cs.volumes.delete_metadata(volume, list(metadata.keys()))


@utils.arg(
    '--all-tenants',
    dest='all_tenants',
    metavar='<0|1>',
    nargs='?',
    type=int,
    const=1,
    default=0,
    help='Display information from all tenants (Admin only).')
@utils.arg(
    '--all_tenants',
    nargs='?',
    type=int,
    const=1,
    help=argparse.SUPPRESS)
@utils.arg(
    '--display-name',
    metavar='<display-name>',
    default=None,
    help='Filter results by display-name')
@utils.arg(
    '--status',
    metavar='<status>',
    default=None,
    help='Filter results by status')
@utils.arg(
    '--volume-id',
    metavar='<volume-id>',
    default=None,
    help='Filter results by volume-id')
@utils.service_type('volume')
def do_snapshot_list(cs, args):
    """List all the snapshots."""
    all_tenants = int(os.environ.get("ALL_TENANTS", args.all_tenants))
    search_opts = {
        'all_tenants': all_tenants,
        'display_name': args.display_name,
        'status': args.status,
        'volume_id': args.volume_id,
    }

    snapshots = cs.volume_snapshots.list(search_opts=search_opts)
    _translate_volume_snapshot_keys(snapshots)
    utils.print_list(snapshots,
                     ['ID', 'Volume ID', 'Status', 'Display Name', 'Size'])


@utils.arg('snapshot', metavar='<snapshot>',
           help='Name or ID of the snapshot.')
@utils.service_type('volume')
def do_snapshot_show(cs, args):
    """Show details about a snapshot."""
    snapshot = _find_volume_snapshot(cs, args.snapshot)
    _print_volume_snapshot(snapshot)


@utils.arg('volume',
           metavar='<volume>',
           help='Name or ID of the volume to snapshot')
@utils.arg('--force',
           metavar='<True|False>',
           help='Optional flag to indicate whether '
           'to snapshot a volume even if it\'s '
           'attached to an instance. (Default=False)',
           default=False)
@utils.arg(
    '--display-name',
    metavar='<display-name>',
    default=None,
    help='Optional snapshot name. (Default=None)')
@utils.arg(
    '--display_name',
    help=argparse.SUPPRESS)
@utils.arg(
    '--display-description',
    metavar='<display-description>',
    default=None,
    help='Optional snapshot description. (Default=None)')
@utils.arg(
    '--display_description',
    help=argparse.SUPPRESS)
@utils.service_type('volume')
def do_snapshot_create(cs, args):
    """Add a new snapshot."""
    volume = utils.find_volume(cs, args.volume)
    snapshot = cs.volume_snapshots.create(volume.id,
                                          args.force,
                                          args.display_name,
                                          args.display_description)
    _print_volume_snapshot(snapshot)


@utils.arg('snapshot',
           metavar='<snapshot>',
           help='Name or ID of the snapshot to delete.')
@utils.service_type('volume')
def do_snapshot_delete(cs, args):
    """Remove a snapshot."""
    snapshot = _find_volume_snapshot(cs, args.snapshot)
    snapshot.delete()


@utils.arg('snapshot', metavar='<snapshot>',
           help='Name or ID of the snapshot.')
@utils.arg('display_name', nargs='?', metavar='<display-name>',
           help='New display-name for the snapshot.')
@utils.arg('--display-description', metavar='<display-description>',
           help='Optional snapshot description. (Default=None)',
           default=None)
@utils.service_type('volume')
def do_snapshot_rename(cs, args):
    """Rename a snapshot."""
    kwargs = {}
    if args.display_name is not None:
        kwargs['display_name'] = args.display_name
    if args.display_description is not None:
        kwargs['display_description'] = args.display_description

    if not any(kwargs):
        msg = 'Must supply either display-name or display-description.'
        raise exceptions.ClientException(code=1, message=msg)

    _find_volume_snapshot(cs, args.snapshot).update(**kwargs)


@utils.arg('snapshot', metavar='<snapshot>',
           help='Name or ID of the snapshot to modify.')
@utils.arg('--state', metavar='<state>',
           default='available',
           help=('Indicate which state to assign the snapshot. '
                 'Options include available, error, creating, deleting, '
                 'error_deleting. If no state is provided, '
                 'available will be used.'))
@utils.service_type('volume')
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
           nargs='*',
           default=None,
           help='Extra_specs to set/unset (only key is necessary on unset)')
@utils.service_type('volume')
def do_type_key(cs, args):
    """Set or unset extra_spec for a volume type."""
    vtype = _find_volume_type(cs, args.vtype)

    if args.metadata is not None:
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


@utils.arg('tenant', metavar='<tenant_id>',
           help='UUID of tenant to list the quotas for.')
@utils.service_type('volume')
def do_quota_show(cs, args):
    """List the quotas for a tenant."""

    _quota_show(cs.quotas.get(args.tenant))


@utils.arg('tenant', metavar='<tenant_id>',
           help='UUID of tenant to list the default quotas for.')
@utils.service_type('volume')
def do_quota_defaults(cs, args):
    """List the default quotas for a tenant."""

    _quota_show(cs.quotas.defaults(args.tenant))


@utils.arg('tenant', metavar='<tenant_id>',
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


@utils.arg('class_name', metavar='<class>',
           help='Name of quota class to list the quotas for.')
@utils.service_type('volume')
def do_quota_class_show(cs, args):
    """List the quotas for a quota class."""

    _quota_show(cs.quota_classes.get(args.class_name))


@utils.arg('class_name', metavar='<class>',
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


@utils.arg('volume',
           metavar='<volume>',
           help='Name or ID of the volume to upload to an image')
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
@utils.arg('--disk-format',
           metavar='<disk-format>',
           help='Optional type for disk format '
           '(Default=raw)',
           default='raw')
@utils.arg('image_name',
           metavar='<image-name>',
           help='Name for created image')
@utils.service_type('volume')
def do_upload_to_image(cs, args):
    """Upload volume to image service as image."""
    volume = utils.find_volume(cs, args.volume)
    _print_volume_image(volume.upload_to_image(args.force,
                                               args.image_name,
                                               args.container_format,
                                               args.disk_format))


@utils.arg('volume', metavar='<volume>',
           help='Name or ID of the volume to backup.')
@utils.arg('--container', metavar='<container>',
           help='Optional Backup container name. (Default=None)',
           default=None)
@utils.arg('--display-name', metavar='<display-name>',
           help='Optional backup name. (Default=None)',
           default=None)
@utils.arg('--display-description', metavar='<display-description>',
           help='Optional backup description. (Default=None)',
           default=None)
@utils.service_type('volume')
def do_backup_create(cs, args):
    """Creates a backup."""
    volume = utils.find_volume(cs, args.volume)
    backup = cs.backups.create(volume.id,
                               args.container,
                               args.display_name,
                               args.display_description)

    info = {"volume_id": volume.id}
    info.update(backup._info)

    if 'links' in info:
        info.pop('links')

    utils.print_dict(info)


@utils.arg('backup', metavar='<backup>', help='Name or ID of the backup.')
@utils.service_type('volume')
def do_backup_show(cs, args):
    """Show details about a backup."""
    backup = _find_backup(cs, args.backup)
    info = dict()
    info.update(backup._info)

    if 'links' in info:
        info.pop('links')

    utils.print_dict(info)


@utils.service_type('volume')
def do_backup_list(cs, args):
    """List all the backups."""
    backups = cs.backups.list()
    columns = ['ID', 'Volume ID', 'Status', 'Name', 'Size', 'Object Count',
               'Container']
    utils.print_list(backups, columns)


@utils.arg('backup', metavar='<backup>',
           help='Name or ID of the backup to delete.')
@utils.service_type('volume')
def do_backup_delete(cs, args):
    """Remove a backup."""
    backup = _find_backup(cs, args.backup)
    backup.delete()


@utils.arg('backup', metavar='<backup>',
           help='ID of the backup to restore.')
@utils.arg('--volume-id', metavar='<volume>',
           help='Optional ID(or name) of the volume to restore to.',
           default=None)
@utils.service_type('volume')
def do_backup_restore(cs, args):
    """Restore a backup."""
    if args.volume:
        volume_id = utils.find_volume(cs, args.volume).id
    else:
        volume_id = None
    cs.restores.restore(args.backup, volume_id)


@utils.arg('volume', metavar='<volume>',
           help='Name or ID of the volume to transfer.')
@utils.arg('--display-name', metavar='<display-name>',
           help='Optional transfer name. (Default=None)',
           default=None)
@utils.service_type('volume')
def do_transfer_create(cs, args):
    """Creates a volume transfer."""
    volume = utils.find_volume(cs, args.volume)
    transfer = cs.transfers.create(volume.id,
                                   args.display_name)
    info = dict()
    info.update(transfer._info)

    if 'links' in info:
        info.pop('links')

    utils.print_dict(info)


@utils.arg('transfer', metavar='<transfer>',
           help='Name or ID of the transfer to delete.')
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

    if 'links' in info:
        info.pop('links')

    utils.print_dict(info)


@utils.service_type('volume')
def do_transfer_list(cs, args):
    """List all the transfers."""
    transfers = cs.transfers.list()
    columns = ['ID', 'Volume ID', 'Name']
    utils.print_list(transfers, columns)


@utils.arg('transfer', metavar='<transfer>',
           help='Name or ID of the transfer to accept.')
@utils.service_type('volume')
def do_transfer_show(cs, args):
    """Show details about a transfer."""
    transfer = _find_transfer(cs, args.transfer)
    info = dict()
    info.update(transfer._info)

    if 'links' in info:
        info.pop('links')

    utils.print_dict(info)


@utils.arg('volume', metavar='<volume>',
           help='Name or ID of the volume to extend.')
@utils.arg('new_size',
           metavar='<new-size>',
           type=int,
           help='New size of volume in GB')
@utils.service_type('volume')
def do_extend(cs, args):
    """Attempt to extend the size of an existing volume."""
    volume = utils.find_volume(cs, args.volume)
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


def _print_volume_encryption_type_list(encryption_types):
    """
    Display a tabularized list of volume encryption types.

    :param encryption_types: a list of :class: VolumeEncryptionType instances
    """
    utils.print_list(encryption_types, ['Volume Type ID', 'Provider',
                                        'Cipher', 'Key Size',
                                        'Control Location'])


@utils.service_type('volume')
def do_encryption_type_list(cs, args):
    """List encryption type information for all volume types (Admin Only)."""
    result = cs.volume_encryption_types.list()
    utils.print_list(result, ['Volume Type ID', 'Provider', 'Cipher',
                              'Key Size', 'Control Location'])


@utils.arg('volume_type',
           metavar='<volume_type>',
           type=str,
           help="Name or ID of the volume type")
@utils.service_type('volume')
def do_encryption_type_show(cs, args):
    """Show the encryption type information for a volume type (Admin Only)."""
    volume_type = _find_volume_type(cs, args.volume_type)

    result = cs.volume_encryption_types.get(volume_type)

    # Display result or an empty table if no result
    if hasattr(result, 'volume_type_id'):
        _print_volume_encryption_type_list([result])
    else:
        _print_volume_encryption_type_list([])


@utils.arg('volume_type',
           metavar='<volume_type>',
           type=str,
           help="Name or ID of the volume type")
@utils.arg('provider',
           metavar='<provider>',
           type=str,
           help="Class providing encryption support (e.g. LuksEncryptor)")
@utils.arg('--cipher',
           metavar='<cipher>',
           type=str,
           required=False,
           default=None,
           help="Encryption algorithm/mode to use (e.g., aes-xts-plain64) "
           "(Optional, Default=None)")
@utils.arg('--key_size',
           metavar='<key_size>',
           type=int,
           required=False,
           default=None,
           help="Size of the encryption key, in bits (e.g., 128, 256) "
           "(Optional, Default=None)")
@utils.arg('--control_location',
           metavar='<control_location>',
           choices=['front-end', 'back-end'],
           type=str,
           required=False,
           default=None,
           help="Notional service where encryption is performed (e.g., "
           "front-end=Nova). Values: 'front-end', 'back-end' "
           "(Optional, Default=None)")
@utils.service_type('volume')
def do_encryption_type_create(cs, args):
    """Create a new encryption type for a volume type (Admin Only)."""
    volume_type = _find_volume_type(cs, args.volume_type)

    body = {}
    body['provider'] = args.provider
    body['cipher'] = args.cipher
    body['key_size'] = args.key_size
    body['control_location'] = args.control_location

    result = cs.volume_encryption_types.create(volume_type, body)
    _print_volume_encryption_type_list([result])


@utils.arg('volume', metavar='<volume>', help='ID of the volume to migrate')
@utils.arg('host', metavar='<host>', help='Destination host')
@utils.arg('--force-host-copy', metavar='<True|False>',
           choices=['True', 'False'], required=False,
           help='Optional flag to force the use of the generic '
           'host-based migration mechanism, bypassing driver '
           'optimizations (Default=False).',
           default=False)
@utils.service_type('volume')
def do_migrate(cs, args):
    """Migrate the volume to the new host."""
    volume = utils.find_volume(cs, args.volume)

    volume.migrate_volume(args.host, args.force_host_copy)


def _print_qos_specs(qos_specs):
    utils.print_dict(qos_specs._info)


def _print_qos_specs_list(q_specs):
    utils.print_list(q_specs, ['ID', 'Name', 'Consumer', 'specs'])


def _print_qos_specs_and_associations_list(q_specs):
    utils.print_list(q_specs, ['ID', 'Name', 'Consumer', 'specs'])


def _print_associations_list(associations):
    utils.print_list(associations, ['Association_Type', 'Name', 'ID'])


@utils.arg('name',
           metavar='<name>',
           help="Name of the new QoS specs")
@utils.arg('metadata',
           metavar='<key=value>',
           nargs='+',
           default=[],
           help='Specifications for QoS')
@utils.service_type('volume')
def do_qos_create(cs, args):
    """Create a new qos specs."""
    keypair = None
    if args.metadata is not None:
        keypair = _extract_metadata(args)
    qos_specs = cs.qos_specs.create(args.name, keypair)
    _print_qos_specs(qos_specs)


@utils.service_type('volume')
def do_qos_list(cs, args):
    """Get full list of qos specs."""
    qos_specs = cs.qos_specs.list()
    _print_qos_specs_list(qos_specs)


@utils.arg('qos_specs', metavar='<qos_specs>',
           help='ID of the qos_specs to show.')
@utils.service_type('volume')
def do_qos_show(cs, args):
    """Get a specific qos specs."""
    qos_specs = _find_qos_specs(cs, args.qos_specs)
    _print_qos_specs(qos_specs)


@utils.arg('qos_specs', metavar='<qos_specs>',
           help='ID of the qos_specs to delete.')
@utils.arg('--force',
           metavar='<True|False>',
           default=False,
           help='Optional flag that indicates whether to delete '
                'specified qos specs even if it is in-use.')
@utils.service_type('volume')
def do_qos_delete(cs, args):
    """Delete a specific qos specs."""
    force = strutils.bool_from_string(args.force)
    qos_specs = _find_qos_specs(cs, args.qos_specs)
    cs.qos_specs.delete(qos_specs, force)


@utils.arg('qos_specs', metavar='<qos_specs>',
           help='ID of qos_specs.')
@utils.arg('vol_type_id', metavar='<volume_type_id>',
           help='ID of volume type to be associated with.')
@utils.service_type('volume')
def do_qos_associate(cs, args):
    """Associate qos specs with specific volume type."""
    cs.qos_specs.associate(args.qos_specs, args.vol_type_id)


@utils.arg('qos_specs', metavar='<qos_specs>',
           help='ID of qos_specs.')
@utils.arg('vol_type_id', metavar='<volume_type_id>',
           help='ID of volume type to be associated with.')
@utils.service_type('volume')
def do_qos_disassociate(cs, args):
    """Disassociate qos specs from specific volume type."""
    cs.qos_specs.disassociate(args.qos_specs, args.vol_type_id)


@utils.arg('qos_specs', metavar='<qos_specs>',
           help='ID of qos_specs to be operate on.')
@utils.service_type('volume')
def do_qos_disassociate_all(cs, args):
    """Disassociate qos specs from all of its associations."""
    cs.qos_specs.disassociate_all(args.qos_specs)


@utils.arg('qos_specs', metavar='<qos_specs>',
           help='ID of qos specs')
@utils.arg('action',
           metavar='<action>',
           choices=['set', 'unset'],
           help="Actions: 'set' or 'unset'")
@utils.arg('metadata', metavar='key=value',
           nargs='+',
           default=[],
           help='QoS specs to set/unset (only key is necessary on unset)')
def do_qos_key(cs, args):
    """Set or unset specifications for a qos spec."""
    keypair = _extract_metadata(args)

    if args.action == 'set':
        cs.qos_specs.set_keys(args.qos_specs, keypair)
    elif args.action == 'unset':
        cs.qos_specs.unset_keys(args.qos_specs, list(keypair.keys()))


@utils.arg('qos_specs', metavar='<qos_specs>',
           help='ID of the qos_specs.')
@utils.service_type('volume')
def do_qos_get_association(cs, args):
    """Get all associations of specific qos specs."""
    associations = cs.qos_specs.get_associations(args.qos_specs)
    _print_associations_list(associations)
