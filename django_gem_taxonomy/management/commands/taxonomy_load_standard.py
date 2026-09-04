# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2025-2026 GEM Foundation
#
# django-gem-taxonomy is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-gem-taxonomy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# import subprocess
# from django.conf import settings
import os
import sys
import json
from django.core.management.base import BaseCommand

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
            '--is-default', help='to set this dataset as default version',
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
            desc=vers_desc,
            is_default=options['is_default']
        )

        if options['is_default'] is True:
            vers_not_def = Version.objects.all().exclude(vers=vers_id)
            vers_not_def.update(is_default=False)

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

        tax_dump = {
            "version": vers_id,
            "attribute": {},
                # "dates": {
                #           "prog": 300,
                #           "title": "Date of Construction or Retrofit",
                #           "name": "dates",
                #           "atomsgroups": [
                #               "construction_completed_year",
                #               "physical_condition_maintenance"
                #           ]
                #          },

            "atomsgroup": {},
                # "material_type": {
                #     "prog": 0,
                #     "title": "Material type",
                #     "attr": "material",
                #     "mutex": true,
                #     "name": "material_type",
                #     "atoms": [
                #         "MDD", "C", "CU", .... "HYB", "INF", "MATO"
                #     ],
                #     "is_persistent": true
                # },

            "atom": {},
                # "atom": {
                #     "ADO": {
                #         "prog": 0,
                #         "title": "Adobe blocks",
                #         "desc": "",
                #         "group": "masonry_technology",
                #         "attr": "material",
                #         "type": "{\"name\": \"option\"}",
                #         "args": null,
                #         "params": null,
                #         "name": "ADO",
                #         "deps": [
                #             "M",
                #             "MCF",
                #             "MR",
                #             "MUR"
                #         ],
                #         "rev_deps": []
                #         "deny": []
                #         "rev_deny": []
                #     },

            "param": {},
            "atom_type": {},
        }

        for atom in Atom.objects.filter(vers=vers).order_by('name'):
            atom_out = {}
            atom_out['prog'] = atom.prog
            atom_out['title'] = atom.title
            atom_out['desc'] = atom.desc
            if not atom.group:
                atom_out['group'] = atom.group
            else:
                atom_out['group'] = atom.group.name
            if not atom.attr:
                atom_out['attr'] = atom.attr
            else:
                atom_out['attr'] = atom.attr.name
            atom_out['type'] = atom.type
            atom_out['args'] = atom.args
            atom_out['params'] = atom.params
            atom_out['name'] = atom.name

            atom_out['deps'] = []
            # for dep in atom.deps.all().exclude(name="_ARG").order_by('name'):
            for dep in atom.deps.all().order_by('name'):
                atom_out['deps'].append(dep.name)
            atom_out['rev_deps'] = []

            atom_out['deny'] = []
            for den in atom.deny.all().order_by('name'):
                atom_out['deny'].append(den.name)
            atom_out['rev_deny'] = []

            #     atomsgroup_out['atoms'].append(atom.name)
            tax_dump['atom'][atom.name] = atom_out

        for el_key, el_val in tax_dump['atom'].items():
            for el_dep_key, el_dep_val in tax_dump['atom'].items():
                if el_dep_val['name'] == el_val['name']:
                    continue
                if el_val['name'] in el_dep_val['deps']:
                    el_val['rev_deps'].append(el_dep_val['name'])

        for el_key, el_val in tax_dump['atom'].items():
            for el_den_key, el_den_val in tax_dump['atom'].items():
                if el_den_val['name'] == el_val['name']:
                    continue
                if el_val['name'] in el_den_val['deny']:
                    el_val['rev_deny'].append(el_den_val['name'])

        for atomsgroup in AtomsGroup.objects.filter(vers=vers).order_by('name'):
            atomsgroup_out = {}
            atomsgroup_out['prog'] = atomsgroup.prog
            atomsgroup_out['title'] = atomsgroup.title
            atomsgroup_out['attr'] = atomsgroup.attr.name
            atomsgroup_out['mutex'] = atomsgroup.mutex
            atomsgroup_out['name'] = atomsgroup.name
            atomsgroup_out['atoms'] = []
            atoms = Atom.objects.filter(vers=vers, group=atomsgroup).order_by('prog')
            for atom in atoms:
                atomsgroup_out['atoms'].append(atom.name)
            tax_dump['atomsgroup'][atomsgroup.name] = atomsgroup_out

        for attr in Attribute.objects.filter(vers=vers).order_by('name'):
            attr_out = {}
            attr_out['prog'] = attr.prog
            attr_out['title'] = attr.title
            attr_out['name'] = attr.name
            attr_out['atomsgroups'] = []
            atomsgroups = AtomsGroup.objects.filter(vers=vers, attr=attr).order_by('prog')
            for atomsgroup in atomsgroups:
                attr_out['atomsgroups'].append(atomsgroup.name)
            tax_dump['attribute'][attr.name] = attr_out


        for atom in Atom.objects.filter(vers=vers).order_by('prog'):
            if (atom.params and 'type' in atom.params
                and atom.params['type'] == 'options'):
                tax_dump['param'][atom.name] = []
                for param in Param.objects.filter(vers=vers, atom=atom).order_by('prog'):
                    param_out = {}
                    param_out['atom'] = param.atom.name
                    param_out['name'] = param.name
                    param_out['prog'] = param.prog
                    param_out['title'] = param.title
                    param_out['desc'] = param.desc
                    tax_dump['param'][atom.name].append(param_out)

            for atomsgroup_key, atomsgroup_val in tax_dump['atomsgroup'].items():
                atomsgroup_val['is_persistent'] = False

                # FIXME: check 'if 'atoms' in atomsgroup_val' needed
                #        because we start from a atoms partial populated
                #        standard definition
                if 'atoms' in atomsgroup_val:
                    # check to set atomsgroup as persistent
                    atoms_list = atomsgroup_val['atoms']
                    for atom_name in atoms_list:
                        atom = tax_dump['atom'][atom_name]
                        if not atom['deps']:
                            atomsgroup_val['is_persistent'] = True
                            break

                    atomsgroup_val['atoms'] = sorted(
                        atomsgroup_val['atoms'],
                        key=lambda x: tax_dump['atom'][x]['prog'])

        # sort rev_deps by 'group' and 'prog' to generate proper dropdown menu
        for atom_key, atom_val in tax_dump['atom'].items():
            if atom_val['rev_deps']:
                rev_deps_new = sorted(
                    atom_val['rev_deps'],
                    key=lambda x: (
                        tax_dump['atomsgroup'][tax_dump['atom'][x]['group']]['prog'],
                        tax_dump['atom'][x]['prog']))
                atom_val['rev_deps'] = rev_deps_new


        json.dump(tax_dump, sys.stdout, indent=4)

        json_dump_file = os.path.join('django_gem_taxonomy/static/taxonomy/json/',
                                      'taxonomy%s_standard4taxtweb.json.new' % vers_id)
        with open(json_dump_file, 'w', encoding='utf-8') as tf:
            json.dump(tax_dump, tf, indent=4)
