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

"""Sphinx extension to generate CLI documentation."""

from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst import directives
from docutils import statemachine as sm
from sphinx.util import logging
from sphinx.util import nested_parse_with_titles

from cinderclient import api_versions
from cinderclient import shell

LOG = logging.getLogger(__name__)


class CLIDocsDirective(rst.Directive):
    """Directive to generate CLI details into docs output."""

    def _get_usage_lines(self, usage, append_value=None):
        """Breaks usage output into separate lines."""
        results = []
        lines = usage.split('\n')

        indent = 0
        if '[' in lines[0]:
            indent = lines[0].index('[')

        for line in lines:
            if line.strip():
                results.append(line)

        if append_value:
            results.append('  {}{}'.format(' ' * indent, append_value))

        return results

    def _format_description_lines(self, description):
        """Formats option description into formatted lines."""
        desc = description.split('\n')
        return [line.strip() for line in desc if line.strip() != '']

    def run(self):
        """Load and document the current config options."""

        cindershell = shell.OpenStackCinderShell()
        parser = cindershell.get_base_parser()

        api_version = api_versions.APIVersion(api_versions.MAX_VERSION)
        LOG.info('Generating CLI docs %s', api_version)

        cindershell.get_subcommand_parser(api_version, False, [])

        result = sm.ViewList()
        source = '<{}>'.format(__name__)

        result.append('.. _cinder_command_usage:', source)
        result.append('', source)
        result.append('cinder usage', source)
        result.append('------------', source)
        result.append('', source)
        result.append('.. code-block:: console', source)
        result.append('', source)
        result.append('', source)
        usage = self._get_usage_lines(
            parser.format_usage(), '<subcommand> ...')
        for line in usage:
            result.append('  {}'.format(line), source)
        result.append('', source)

        result.append('.. _cinder_command_options:', source)
        result.append('', source)
        result.append('Optional Arguments', source)
        result.append('~~~~~~~~~~~~~~~~~~', source)
        result.append('', source)

        # This accesses a private variable from argparse. That's a little
        # risky, but since this is just for the docs and not "production" code,
        # and since this variable hasn't changed in years, it's a calculated
        # risk to make this documentation generation easier. But if something
        # suddenly breaks, check here first.
        actions = sorted(parser._actions, key=lambda x: x.option_strings[0])
        for action in actions:
            if action.help == '==SUPPRESS==':
                continue
            opts = ', '.join(action.option_strings)
            result.append('``{}``'.format(opts), source)
            result.append('  {}'.format(action.help), source)
            result.append('', source)

        result.append('', source)
        result.append('.. _cinder_commands:', source)
        result.append('', source)
        result.append('Commands', source)
        result.append('~~~~~~~~', source)
        result.append('', source)

        for cmd in cindershell.subcommands:
            if 'completion' in cmd:
                continue
            result.append('``{}``'.format(cmd), source)
            subcmd = cindershell.subcommands[cmd]
            description = self._format_description_lines(subcmd.description)
            result.append('  {}'.format(description[0]), source)
            result.append('', source)

        result.append('', source)
        result.append('.. _cinder_command_details:', source)
        result.append('', source)
        result.append('Command Details', source)
        result.append('---------------', source)
        result.append('', source)

        for cmd in cindershell.subcommands:
            if 'completion' in cmd:
                continue
            subcmd = cindershell.subcommands[cmd]
            result.append('.. _cinder{}:'.format(cmd), source)
            result.append('', source)
            result.append(subcmd.prog, source)
            result.append('~' * len(subcmd.prog), source)
            result.append('', source)
            result.append('.. code-block:: console', source)
            result.append('', source)
            usage = self._get_usage_lines(subcmd.format_usage())
            for line in usage:
                result.append('  {}'.format(line), source)
            result.append('', source)
            description = self._format_description_lines(subcmd.description)
            result.append(description[0], source)
            result.append('', source)

            if len(subcmd._actions) == 0:
                continue

            positional = []
            optional = []
            for action in subcmd._actions:
                if len(action.option_strings):
                    if (action.option_strings[0] != '-h' and
                            action.help != '==SUPPRESS=='):
                        optional.append(action)
                else:
                    positional.append(action)

            if positional:
                result.append('**Positional arguments:**', source)
                result.append('', source)
                for action in positional:
                    result.append('``{}``'.format(action.metavar), source)
                    result.append('  {}'.format(action.help), source)
                    result.append('', source)

            if optional:
                result.append('**Optional arguments:**', source)
                result.append('', source)
                for action in optional:
                    result.append('``{} {}``'.format(
                            ', '.join(action.option_strings), action.metavar),
                        source)
                    result.append('  {}'.format(action.help), source)
                    result.append('', source)

        node = nodes.section()
        node.document = self.state.document
        nested_parse_with_titles(self.state, result, node)
        return node.children


def setup(app):
    app.add_directive('cli-docs', CLIDocsDirective)
    return {
        'version': '1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
