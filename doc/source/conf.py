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

sys.setrecursionlimit(4000)

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#    sys.path.append(os.path.abspath('.'))
sys.path.insert(0, os.path.join(os.path.abspath('..'), 'ext'))

# -- General configuration ----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'openstackdocstheme',
    'reno.sphinxext',
    'cli',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
copyright = 'OpenStack Contributors'

# done by the openstackdocstheme ext
# project = 'python-cinderclient'
# version = version_info.version_string()
# release = version_info.release_string()

# List of directories, relative to source directory, that shouldn't be searched
# for source files.
exclude_trees = []

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'native'

# -- Options for HTML output --------------------------------------------------

# The theme to use for HTML and HTML Help pages.  Major themes that come with
# Sphinx are currently 'default' and 'sphinxdoc'.
#    html_theme = 'nature'
html_theme = 'openstackdocs'

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'
# html_last_updated_fmt = '%Y-%m-%d %H:%M'

# -- Options for manual page output ------------------------------------------

man_pages = [
    ('cli/details', 'cinder', u'Client for OpenStack Block Storage API',
     [u'OpenStack Contributors'], 1),
]

# -- Options for openstackdocstheme -------------------------------------------

openstackdocs_repo_name = 'openstack/python-cinderclient'
openstackdocs_bug_project = 'python-cinderclient'
openstackdocs_bug_tag = 'doc'
openstackdocs_pdf_link = True

# -- Options for LaTeX output -------------------------------------------------

# The paper size ('letter' or 'a4').
# latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
# latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass
# [howto/manual]).
latex_documents = [
    ('index', 'doc-python-cinderclient.tex', u'Cinder Client Documentation',
     u'Cinder Contributors', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# Additional stuff for the LaTeX preamble.
# latex_preamble = ''

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_use_modindex = True

# Disable usage of xindy https://bugzilla.redhat.com/show_bug.cgi?id=1643664
latex_use_xindy = False

latex_domain_indices = False

latex_elements = {
    'makeindex': '',
    'printindex': '',
    'preamble': r'\setcounter{tocdepth}{3}',
}

latex_additional_files = ['cinderclient.sty']
