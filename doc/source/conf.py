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

# python-cinderclient documentation build configuration file

import os
import sys
import pbr.version

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#    sys.path.append(os.path.abspath('.'))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
sys.path.insert(0, ROOT)

# -- General configuration ----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'openstackdocstheme',
    'reno.sphinxext',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'python-cinderclient'
copyright = 'OpenStack Contributors'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
version_info = pbr.version.VersionInfo('python-cinderclient')
# The short X.Y version.
version = version_info.version_string()
# The full version, including alpha/beta/rc tags.
release = version_info.release_string()

# List of directories, relative to source directory, that shouldn't be searched
# for source files.
exclude_trees = []

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output --------------------------------------------------

# The theme to use for HTML and HTML Help pages.  Major themes that come with
# Sphinx are currently 'default' and 'sphinxdoc'.
#    html_theme = 'nature'
html_theme = 'openstackdocs'

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'
html_last_updated_fmt = '%Y-%m-%d %H:%M'

# -- Options for manual page output ------------------------------------------

man_pages = [
    ('cli/details', 'cinder', u'Client for OpenStack Block Storage API',
     [u'OpenStack Contributors'], 1),
]

# -- Options for openstackdocstheme -------------------------------------------

repository_name = 'openstack/python-cinderclient'
bug_project = 'cinderclient'
bug_tag = ''
