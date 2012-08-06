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


def _print_volume(cs, volume):
    utils.print_dict(volume._info)


def _print_volume_snapshot(cs, snapshot):
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


@utils.arg('--all_tenants',
           dest='all_tenants',
           metavar='<0|1>',
           nargs='?',
           type=int,
           const=1,
           default=0,
           help='Display information from all tenants (Admin only).')
@utils.service_type('volume')
def do_list(cs, args):
    """List all the volumes."""
    all_tenants = int(os.environ.get("ALL_TENANTS", args.all_tenants))
    search_opts = {'all_tenants': all_tenants}
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
    _print_volume(cs, volume)


@utils.arg('size',
           metavar='<size>',
           type=int,
           help='Size of volume in GB')
@utils.arg(
    '--snapshot_id',
    metavar='<snapshot_id>',
    help='Optional snapshot id to create the volume from. (Default=None)',
    default=None)
@utils.arg('--display_name', metavar='<display_name>',
           help='Optional volume name. (Default=None)',
           default=None)
@utils.arg('--display_description', metavar='<display_description>',
           help='Optional volume description. (Default=None)',
           default=None)
@utils.arg('--volume_type',
           metavar='<volume_type>',
           help='Optional volume type. (Default=None)',
           default=None)
@utils.service_type('volume')
def do_create(cs, args):
    """Add a new volume."""
    cs.volumes.create(args.size,
                      args.snapshot_id,
                      args.display_name,
                      args.display_description,
                      args.volume_type)


@utils.arg('volume', metavar='<volume>', help='ID of the volume to delete.')
@utils.service_type('volume')
def do_delete(cs, args):
    """Remove a volume."""
    volume = _find_volume(cs, args.volume)
    volume.delete()


@utils.arg('--all_tenants',
           dest='all_tenants',
           metavar='<0|1>',
           nargs='?',
           type=int,
           const=1,
           default=0,
           help='Display information from all tenants (Admin only).')
@utils.service_type('volume')
def do_snapshot_list(cs, args):
    """List all the snapshots."""
    all_tenants = int(os.environ.get("ALL_TENANTS", args.all_tenants))
    search_opts = {'all_tenants': all_tenants}

    snapshots = cs.volume_snapshots.list(search_opts=search_opts)
    _translate_volume_snapshot_keys(snapshots)
    utils.print_list(snapshots,
                     ['ID', 'Volume ID', 'Status', 'Display Name', 'Size'])


@utils.arg('snapshot', metavar='<snapshot>', help='ID of the snapshot.')
@utils.service_type('volume')
def do_snapshot_show(cs, args):
    """Show details about a snapshot."""
    snapshot = _find_volume_snapshot(cs, args.snapshot)
    _print_volume_snapshot(cs, snapshot)


@utils.arg('volume_id',
           metavar='<volume_id>',
           help='ID of the volume to snapshot')
@utils.arg('--force',
           metavar='<True|False>',
           help='Optional flag to indicate whether '
           'to snapshot a volume even if its '
           'attached to an instance. (Default=False)',
           default=False)
@utils.arg('--display_name', metavar='<display_name>',
           help='Optional snapshot name. (Default=None)',
           default=None)
@utils.arg('--display_description', metavar='<display_description>',
           help='Optional snapshot description. (Default=None)',
           default=None)
@utils.service_type('volume')
def do_snapshot_create(cs, args):
    """Add a new snapshot."""
    cs.volume_snapshots.create(args.volume_id,
                               args.force,
                               args.display_name,
                               args.display_description)


@utils.arg('snapshot_id',
           metavar='<snapshot_id>',
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
