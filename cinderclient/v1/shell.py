# Copyright 2010 Jacob Kaplan-Moss

# Copyright 2011 OpenStack LLC.
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

import argparse
import os
import sys
import time

from cinderclient import utils


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

    print
    while True:
        obj = poll_fn(obj_id)
        status = obj.status.lower()
        progress = getattr(obj, 'progress', None) or 0
        if status in final_ok_states:
            print_progress(100)
            print "\nFinished"
            break
        elif status == "error":
            print "\nError %(action)s instance" % locals()
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


def _print_volume(volume):
    utils.print_dict(volume._info)


def _print_volume_snapshot(snapshot):
    utils.print_dict(snapshot._info)


def _translate_volume_keys(collection):
    convert = [('displayName', 'display_name'), ('volumeType', 'volume_type')]
    for item in collection:
        keys = item.__dict__.keys()
        for from_key, to_key in convert:
            if from_key in keys and to_key not in keys:
                setattr(item, to_key, item._info[from_key])


def _translate_volume_snapshot_keys(collection):
    convert = [('displayName', 'display_name'), ('volumeId', 'volume_id')]
    for item in collection:
        keys = item.__dict__.keys()
        for from_key, to_key in convert:
            if from_key in keys and to_key not in keys:
                setattr(item, to_key, item._info[from_key])


def _extract_metadata(arg_list):
    metadata = {}
    for metadatum in arg_list:
        assert(metadatum.find('=') > -1), "Improperly formatted metadata "\
                                          "input (%s)" % metadatum
        (key, value) = metadatum.split('=', 1)
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
@utils.service_type('volume')
def do_list(cs, args):
    """List all the volumes."""
    all_tenants = int(os.environ.get("ALL_TENANTS", args.all_tenants))
    search_opts = {
        'all_tenants': all_tenants,
        'display_name': args.display_name,
        'status': args.status,
    }
    volumes = cs.volumes.list(search_opts=search_opts)
    _translate_volume_keys(volumes)

    # Create a list of servers to which the volume is attached
    for vol in volumes:
        servers = [s.get('server_id') for s in vol.attachments]
        setattr(vol, 'attached_to', ','.join(map(str, servers)))
    utils.print_list(volumes, ['ID', 'Status', 'Display Name',
                     'Size', 'Volume Type', 'Attached to'])


@utils.arg('volume', metavar='<volume>', help='ID of the volume.')
@utils.service_type('volume')
def do_show(cs, args):
    """Show details about a volume."""
    volume = _find_volume(cs, args.volume)
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
        volume_metadata = _extract_metadata(args.metadata)

    volume = cs.volumes.create(args.size,
                               args.snapshot_id,
                               args.display_name,
                               args.display_description,
                               args.volume_type,
                               availability_zone=args.availability_zone,
                               imageRef=args.image_id,
                               metadata=volume_metadata)
    _print_volume(volume)


@utils.arg('volume', metavar='<volume>', help='ID of the volume to delete.')
@utils.service_type('volume')
def do_delete(cs, args):
    """Remove a volume."""
    volume = _find_volume(cs, args.volume)
    volume.delete()


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


@utils.arg('snapshot', metavar='<snapshot>', help='ID of the snapshot.')
@utils.service_type('volume')
def do_snapshot_show(cs, args):
    """Show details about a snapshot."""
    snapshot = _find_volume_snapshot(cs, args.snapshot)
    _print_volume_snapshot(snapshot)


@utils.arg('volume_id',
           metavar='<volume-id>',
           help='ID of the volume to snapshot')
@utils.arg('--force',
           metavar='<True|False>',
           help='Optional flag to indicate whether '
           'to snapshot a volume even if its '
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
    snapshot = cs.volume_snapshots.create(args.volume_id,
                                          args.force,
                                          args.display_name,
                                          args.display_description)
    _print_volume_snapshot(snapshot)


@utils.arg('snapshot_id',
           metavar='<snapshot-id>',
           help='ID of the snapshot to delete.')
@utils.service_type('volume')
def do_snapshot_delete(cs, args):
    """Remove a snapshot."""
    snapshot = _find_volume_snapshot(cs, args.snapshot_id)
    snapshot.delete()


def _print_volume_type_list(vtypes):
    utils.print_list(vtypes, ['ID', 'Name'])


@utils.service_type('volume')
def do_type_list(cs, args):
    """Print a list of available 'volume types'."""
    vtypes = cs.volume_types.list()
    _print_volume_type_list(vtypes)


@utils.arg('name',
           metavar='<name>',
           help="Name of the new flavor")
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
    """Delete a specific flavor"""
    cs.volume_types.delete(args.id)


def do_endpoints(cs, args):
    """Discover endpoints that get returned from the authenticate services"""
    catalog = cs.client.service_catalog.catalog
    for e in catalog['access']['serviceCatalog']:
        utils.print_dict(e['endpoints'][0], e['name'])


def do_credentials(cs, args):
    """Show user credentials returned from auth"""
    catalog = cs.client.service_catalog.catalog
    utils.print_dict(catalog['access']['user'], "User Credentials")
    utils.print_dict(catalog['access']['token'], "Token")

_quota_resources = ['volumes', 'gigabytes']


def _quota_show(quotas):
    quota_dict = {}
    for resource in _quota_resources:
        quota_dict[resource] = getattr(quotas, resource, None)
    utils.print_dict(quota_dict)


def _quota_update(manager, identifier, args):
    updates = {}
    for resource in _quota_resources:
        val = getattr(args, resource, None)
        if val is not None:
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
@utils.arg('--gigabytes',
           metavar='<gigabytes>',
           type=int, default=None,
           help='New value for the "gigabytes" quota.')
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
@utils.arg('--gigabytes',
           metavar='<gigabytes>',
           type=int, default=None,
           help='New value for the "gigabytes" quota.')
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
