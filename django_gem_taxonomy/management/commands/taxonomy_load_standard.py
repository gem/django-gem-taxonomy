# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4 expandtab
#
# oq-geoviewer
# Copyright (C) 2018-2019 GEM Foundation
#
# oq-geoviewer is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# oq-geoviewer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# import subprocess
# from django.conf import settings
import os
import copy
import json
from django.core.management import call_command
from django.core.management.base import BaseCommand
from pathlib import Path
import tempfile

from django_gem_taxonomy.models import (Version,
                                        Attribute, AtomsGroup, Atom, Param)


class Command(BaseCommand):
    help = ("Based on taxonomy vers 3 constraint typologies"
            " build attributes/atoms relationships db.")

    def add_arguments(self, parser):
        parser.add_argument('vers_id')
        parser.add_argument('vers_desc')
        parser.add_argument('json_filename')

        # Optional arguments
        parser.add_argument(
            '-n', '--no-dump', help='avoid create json files from DB',
            action='store_true', default=False)
        parser.add_argument(
            '-d', '--development',
            help='enable pdb on exceptions and increase verbosity',
            action='store_true', default=False)
        parser.add_argument(
            '-D', '--delete-only',
            help=('stop command just after version deletion if it exists'
                  ' instead of repopulate it from DB'),
            action='store_true', default=False)

    def handle(self, *args, **options):
        if options['development']:
            from pprint import pprint

        vers_id = options['vers_id']
        vers_desc = options['vers_desc']
        try:
            vers = Version.objects.get(vers=vers_id)
            vers.delete()
            print(f'Version {vers_id} deleted.')
        except Exception:
            print(f'Version {vers_id} not found.')

        if options['delete_only']:
            print('Delete only enabled, exit now.')
            return

        tax_json_in = None
        with open(options['json_filename'], 'r') as f:
            tax_json_in = json.load(f)

        vers = Version.objects.create(
            vers=vers_id,
            desc=vers_desc)

        for attr_in in tax_json_in['Attribute']:
            attr = Attribute.objects.create(
                vers=vers,
                name=attr_in['name'],
                prog=attr_in['prog'],
                title=attr_in['title'],
            )
            if options['development']:
                pprint(attr)

        for atg_in in tax_json_in['AtomsGroup']:
            atoms_group = AtomsGroup.objects.create(
                vers=vers,
                name=atg_in['name'],
                prog=atg_in['prog'],
                title=atg_in['title'],
                attr=Attribute.objects.get(vers=vers, name=atg_in['group'])
            )
            if options['development']:
                pprint(atoms_group)

        atom = Atom.objects.create(
            vers=vers,
            name='_ARG',
            prog=0,
            desc=('Virtual atom dependency to prevent arguments-only atoms'
                  ' to be visualized as unconstrained atoms'),
            args=None,
            params=None,
            type=json.dumps({"name": "virtual"}),
            group=None,
            attr=None,
        )
        for at_in in tax_json_in['Atom']:
            atom_name = at_in['name']
            atom_type = (tax_json_in['AtomType'][atom_name]
                         if atom_name in tax_json_in['AtomType']
                         else json.dumps({}))

            atom_args = (json.loads(at_in['args'])
                         if at_in['args'] else None)
            try:
                atom_params = (json.loads(at_in['params'])
                               if at_in['params'] else None)
            except Exception:
                if options['development']:
                    import pdb; pdb.set_trace()
                raise

            if options['development']:
                print(atom_name)
            atom = Atom.objects.create(
                vers=vers,
                name=at_in['name'],
                prog=at_in['prog'],
                title=at_in['title'],
                desc=at_in['desc'],
                args=atom_args,
                params=atom_params,
                type=atom_type,
                group=AtomsGroup.objects.get(vers=vers, name=at_in['group']),
                attr=Attribute.objects.get(vers=vers, name=at_in['attr']),
            )
            try:
                if atom.name in tax_json_in['AtomsDeps']:
                    for dep in tax_json_in['AtomsDeps'][atom.name]:
                        atom.deps.add(Atom.objects.get(vers=vers, name=dep))
            except Exception:
                if options['development']:
                    import pdb; pdb.set_trace()
                raise

            try:
                if atom.name in tax_json_in['AtomsDeny']:
                    for den in tax_json_in['AtomsDeny'][atom.name]:
                        atom.deny.add(Atom.objects.get(vers=vers, name=den))
            except Exception:
                if options['development']:
                    import pdb; pdb.set_trace()
                raise

        for param_atom, pa_ins in tax_json_in['Param'].items():
            for pa_in in pa_ins:
                param_name = pa_in['name']
                param_prog = pa_in['prog']
                param_title = pa_in['title']
                param_desc = pa_in['desc']

                Param.objects.create(
                    vers=vers,
                    atom=Atom.objects.get(vers=vers, name=param_atom),
                    name=param_name,
                    prog=param_prog,
                    title=param_title,
                    desc=param_desc,
                )
        if options['no_dump']:
            return

        tax_dump_in = None
        # tempfile.TemporaryDirectory() creates a completely unique,
        # isolated directory every time

        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = os.path.join(Path(temp_dir),
                                     "taxonomy_standard_dump.json")
            try:
                call_command('dumpdata', 'django_gem_taxonomy', indent=4,
                             output=json_file)
                tax_dump_in = json.load(open(json_file, 'r'))
            finally:
                # REMOVE json_file
                # TODO tollerate failure to remove
                os.unlink(json_file)

        tax = {}
        for el in tax_dump_in:
            model = el['model'].replace('django_gem_taxonomy.', '')
            if model not in tax:
                tax[model] = {}
            tax[model][el['pk']] = el['fields']

            # NOTE: code to investigate wrong name set
            # if 'name' not in tax[model][el['pk']]:
            #     print('WARNING name missing in: %s' % tax[model][el['pk']])
            # elif tax[model][el['pk']]['name'] != el['pk']:
            #     print('WARNING different name in: %s (%s)' % (
            #         tax[model][el['pk']], el['pk']))

            if 'name' not in tax[model][el['pk']]:
                tax[model][el['pk']]['name'] = el['pk']

        for el_key, el_val in tax['atom'].items():
            if 'rev_deps' not in el_val:
                el_val['rev_deps'] = []
            for el_dep_key, el_dep_val in tax['atom'].items():
                if el_dep_val['name'] == el_val['name']:
                    continue
                if el_val['name'] in el_dep_val['deps']:
                    el_val['rev_deps'].append(el_dep_val['name'])

        # sort rev_deps by 'group' and 'prog' to generate proper dropdown menu
        for atom_key, atom_val in tax['atom'].items():
            if atom_val['rev_deps']:
                rev_deps_new = sorted(
                    atom_val['rev_deps'],
                    key=lambda x: (
                        tax['atomsgroup'][tax['atom'][x]['group']]['prog'],
                        tax['atom'][x]['prog']))
                atom_val['rev_deps'] = rev_deps_new

        # ordered atomgroups into attributes
        for atomsgroup_key, atomsgroup_val in tax['atomsgroup'].items():
            attr = tax['attribute'][atomsgroup_val['attr']]
            if 'atomsgroups' not in attr:
                attr['atomsgroups'] = []
            attr['atomsgroups'].append(atomsgroup_key)

        # sort atomsgroups by ['atomsgroup'][x]['prog']
        for attr_key, attr_val in tax['attribute'].items():
            attr_val['atomsgroups'] = sorted(
                attr_val['atomsgroups'],
                key=lambda x: tax['atomsgroup'][x]['prog'])

        for atom_key, atom_val in tax['atom'].items():
            if atom_val['group']:
                group = tax['atomsgroup'][atom_val['group']]
                if 'atoms' not in group:
                    group['atoms'] = []
                group['atoms'].append(atom_key)

        # sort atoms by ['atom'][x]['prog']
        for atomsgroup_key, atomsgroup_val in tax['atomsgroup'].items():
            atomsgroup_val['is_persistent'] = False

            # FIXME: check 'if 'atoms' in atomsgroup_val' needed
            #        because we start from a atoms partial populated
            #        standard definition
            if 'atoms' in atomsgroup_val:
                # check to set atomsgroup as persistent
                atoms_list = atomsgroup_val['atoms']
                for atom_name in atoms_list:
                    atom = tax['atom'][atom_name]
                    if not atom['deps']:
                        atomsgroup_val['is_persistent'] = True
                        break

                atomsgroup_val['atoms'] = sorted(
                    atomsgroup_val['atoms'],
                    key=lambda x: tax['atom'][x]['prog'])

        tax['atom_type'] = tax_json_in['AtomType']

        tax['param'] = copy.deepcopy(tax_json_in['Param'])

        dump_json = os.path.join(Path(tempfile.gettempdir()),
                                 'taxonomy_standard4taxtweb.json')
        with open(dump_json, 'w', encoding='utf-8') as tf:
            json.dump(tax, tf, indent=4)
