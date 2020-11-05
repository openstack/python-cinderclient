# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2010 OpenStack Foundation
# Copyright 2013 IBM Corp.
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import sys

from six.moves import configparser

import install_venv_common as install_venv


def print_help(project, venv, root):
    """
    Print the help of a project.

    Args:
        project: (todo): write your description
        venv: (todo): write your description
        root: (todo): write your description
    """
    help = """
    %(project)s development environment setup is complete.

    %(project)s development uses virtualenv to track and manage Python
    dependencies while in development and testing.

    To activate the %(project)s virtualenv for the extent of your current
    shell session you can run:

    $ . %(venv)s/bin/activate

    Or, if you prefer, you can run commands in the virtualenv on a case by
    case basis by running:

    $ %(root)s/tools/with_venv.sh <your command>
    """
    print(help % dict(project=project, venv=venv, root=root))


def main(argv):
    """
    Main entry point.

    Args:
        argv: (str): write your description
    """
    root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    if os.environ.get('tools_path'):
        root = os.environ['tools_path']
    venv = os.path.join(root, '.venv')
    if os.environ.get('venv'):
        venv = os.environ['venv']

    pip_requires = os.path.join(root, 'requirements.txt')
    test_requires = os.path.join(root, 'test-requirements.txt')
    py_version = "python%s.%s" % (sys.version_info[0], sys.version_info[1])
    setup_cfg = configparser.ConfigParser()
    setup_cfg.read('setup.cfg')
    project = setup_cfg.get('metadata', 'name')

    install = install_venv.InstallVenv(
        root, venv, pip_requires, test_requires, py_version, project)
    options = install.parse_args(argv)
    install.check_python_version()
    install.check_dependencies()
    install.create_virtualenv(no_site_packages=options.no_site_packages)
    install.install_dependencies()
    print_help(project, venv, root)


if __name__ == '__main__':
    main(sys.argv)
