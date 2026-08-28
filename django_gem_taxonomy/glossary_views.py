# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# django_gem_taxonomy
# Copyright (C) 2024-2025 GEM Foundation
#
# django_gem_taxonomy is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django_gem_taxonomy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from django.views import View
from django.shortcuts import render, redirect
from .models import Version, Param, Atom, AtomsGroup, Attribute


class GlossaryAtom(View):
    def get(self, request, vers_id=None, atom=None):
        atom_obj = None
        param_obj = None
        other_vers = None
        template = 'django-gem-taxonomy/glossary/atom.html'

        if vers_id is None:
            vers = Version.objects.get(is_default=True)
            if atom is None:
                return redirect('taxonomy:taxonomy_struct_atoms_wver',
                                vers_id=vers.vers)
            else:
                return redirect('taxonomy:taxonomy_struct_atoms_wver',
                                vers_id=vers.vers, atom=atom)
        else:
            vers = Version.objects.get(vers=vers_id)

        if atom is None:
            atoms = Atom.objects.filter(vers=vers).order_by('name')
            others_objs = Version.objects.all().exclude(vers=vers_id)
            other_vers = [vers for vers in others_objs]
        else:
            atoms = None
            if ':' in atom:
                parts = atom.split(':')
                atom_part = parts[0]
                param_part = parts[1]

                param_obj = Param.objects.get(vers=vers, name=param_part,
                                              atom__name=atom_part)
                atom_obj = param_obj.atom

                others_objs = Param.objects.filter(
                    name=param_part, atom__name=atom_part).exclude(vers=vers)
                other_vers = [param.vers for param in others_objs]
                template = 'django-gem-taxonomy/glossary/param.html'
            else:
                atom_obj = Atom.objects.get(vers=vers, name=atom)
                others_objs = Atom.objects.filter(name=atom).exclude(vers=vers)
                other_vers = [atom.vers for atom in others_objs]

        return render(request, template, {'atoms': atoms,
                                          'atom': atom_obj,
                                          'param': param_obj,
                                          'vers': vers,
                                          'other_vers': other_vers
                                          })


class GlossaryAtomsGroup(View):
    def get(self, request, vers_id=None, atoms_group=None):
        template = 'django-gem-taxonomy/glossary/atoms_group.html'
        atoms_group_obj = None
        other_vers = None

        if vers_id is None:
            vers = Version.objects.get(is_default=True)
            if atoms_group is None:
                return redirect('taxonomy:taxonomy_struct_atomsgroups_wver',
                                vers_id=vers.vers)
            else:
                return redirect('taxonomy:taxonomy_struct_atomsgroup_wver',
                                vers_id=vers.vers, atoms_group=atoms_group)
        else:
            vers = Version.objects.get(vers=vers_id)

        if atoms_group is None:
            atoms_groups = AtomsGroup.objects.filter(vers=vers).order_by('name')
            atoms_group = None
            others_objs = Version.objects.all().exclude(vers=vers_id)
            other_vers = [vers for vers in others_objs]
        else:
            atoms_groups = None
            atoms_group_obj = AtomsGroup.objects.get(vers=vers, name=atoms_group)
            others_objs = AtomsGroup.objects.filter(name=atoms_group).exclude(vers=vers)
            other_vers = [atoms_group.vers for atoms_group in others_objs]

        return render(request, template, {'atoms_groups': atoms_groups,
                                          'atoms_group': atoms_group_obj,
                                          'vers': vers,
                                          'other_vers': other_vers
                                          })


class GlossaryAttribute(View):
    def get(self, request, vers_id=None, attribute=None):
        template = 'django-gem-taxonomy/glossary/attribute.html'
        attribute_obj = None
        other_vers = None

        if vers_id is None:
            vers = Version.objects.get(is_default=True)

            if attribute is None:
                return redirect('taxonomy:taxonomy_struct_attributes_wver',
                                vers_id=vers.vers)
            else:
                return redirect('taxonomy:taxonomy_struct_attribute_wver',
                                vers_id=vers.vers, attribute=attribute)
        else:
            vers = Version.objects.get(vers=vers_id)

        if attribute is None:
            attributes = Attribute.objects.filter(vers=vers).order_by('name')
            attribute_obj = None
            others_objs = Version.objects.all().exclude(vers=vers_id)
            other_vers = [vers for vers in others_objs]
        else:
            attributes = None
            attribute_obj = Attribute.objects.get(vers=vers, name=attribute)
            others_objs = Attribute.objects.filter(name=attribute).exclude(vers=vers)
            other_vers = [atoms_group.vers for atoms_group in others_objs]

        return render(request, template, {'attributes': attributes,
                                          'attribute': attribute_obj,
                                          'vers': vers,
                                          'other_vers': other_vers
                                          })
