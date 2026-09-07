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
import csv
import json
from django.utils.text import slugify
from django.core.management.base import BaseCommand

from django_gem_taxonomy.models import (Version,
                                        Attribute, AtomsGroup, Atom, Param)


attr_name_map = {
    'direction': 'direction',
    'material-of-lateral-load-resisting-system': 'material',
    'lateral-load-resisting-system': 'llrs',
    'height': 'height',
    'date': 'dates',
    'occupancy': 'occupancy',
    'building-position-within-a-block': 'position',
    'shape-of-the-building-plan': 'shape',
    'structural-irregularity': 'irregularity',
    'exterior-walls': 'ext_walls',
    'roof': 'roof',
    'floor': 'floor',
    'foundation': 'foundation',
    }

atomsgroup_name_map = {
    'Type lateral load-resisting system': 'type_lateral_load',
    'Building occupancy type - general': 'building_occupancy_class',
    'Building position within a block': 'building_position_within',
    }

class Command(BaseCommand):
    help = ("Based on taxonomy vers 2 constraint typologies"
            " build attributes/atoms relationships db."
            "FIXME: all constraints, deny, params descr are missing")

    def add_arguments(self, parser):
        parser.add_argument('vers_id')
        parser.add_argument('vers_desc')
        parser.add_argument('psv_filename')

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

        tax_psv_in = None
        f = open(options['psv_filename'], 'r')
        tax_psv_in = csv.DictReader(f, delimiter='|')

        vers = Version.objects.create(
            vers=vers_id,
            desc=vers_desc,
            is_default=options['is_default']
        )

        if options['is_default'] is True:
            vers_not_def = Version.objects.all().exclude(vers=vers_id)
            vers_not_def.update(is_default=False)

        # atomsgroup_count|attribute_title|atomsgroup_title|atomsgroup_name|atomsgroup_prog|atom_name|atom_title
        attr = None
        attr_name = 'invalid'
        attr_title = 'invalid'
        attr_prog = -100
        attr_name = 'invalid'

        atomsgroup = None
        atomsgroup_title = 'invalid'
        atomsgroup_name = 'invalid'
        atomsgroup_prog = -100

        atom = None
        atom_name = 'invalid'
        atom_prog = -100

        for row in tax_psv_in:
            if attr_title != row['attr_title']:
                attr_title = row['attr_title']
                attr_name = attr_name_map[slugify(attr_title)]
                attr_prog += 100
                attr = Attribute.objects.create(
                    vers=vers,
                    name=attr_name,
                    prog=attr_prog,
                    title=attr_title,
                )

            if atomsgroup_title != row['atomsgroup_title']:
                atom_prog = -100
                atomsgroup_title = row['atomsgroup_title']

                if atomsgroup_title in atomsgroup_name_map:
                    atomsgroup_name = atomsgroup_name_map[atomsgroup_title]
                else:
                    atomsgroup_name = slugify(row['atomsgroup_title']).replace('-', '_')
                atomsgroup_prog = int(row['atomsgroup_prog']) * 100

                try:
                    atoms_group = AtomsGroup.objects.create(
                        vers=vers,
                        name=atomsgroup_name,
                        prog=atomsgroup_prog,
                        title=atomsgroup_title,
                        attr=attr
                    )
                except Exception:
                    import pdb ; pdb.set_trace()
            atom_name = row['atom_name']
            atom_title = row['atom_title']
            atom_prog += 100

            if ':' in atom_name:
                parts = atom_name.split(':')
                atom_part = parts[0]
                param_part = parts[1]
                try:
                    atom = Atom.objects.get(vers=vers,
                                            name=atom_part)
                except Exception:
                    print('WARNING: parametrized atom [%s] does not exists' % atom_name)
                    atom = Atom.objects.create(
                        vers=vers,
                        name=atom_part,
                        prog=atom_prog,
                        title='from: ' + atom_title,
                        desc='',
                        args='',
                        params={"type": "options",
                                "params_min": 1,
                                "params_max": 1},
                        type='{}',
                        group=atoms_group,
                        attr=attr
                    )
                param = Param.objects.create(
                    vers=vers,
                    atom=atom,
                    name=param_part,
                    prog=atom_prog,
                    title=atom_title,
                    desc='',
                )
            else:

                if atom_name in ['IRPP', 'IRPS', 'IRVP', 'IRVS']:
                    params={"type": "options",
                            "params_min": 1,
                            "params_max": 1}
                else:
                    params=''
                
                atom = Atom.objects.create(
                    vers=vers,
                    name=atom_name,
                    prog=atom_prog,
                    title=atom_title,
                    desc='',
                    args='',
                    params=params,
                    type='{}',
                    group=atoms_group,
                    attr=attr
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
