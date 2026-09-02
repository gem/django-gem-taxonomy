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
from django.shortcuts import render, redirect, get_object_or_404
from .models import Version, Param, Atom, AtomsGroup, Attribute, Content

from .glossary_forms import ContentFormSet
from django.forms import modelform_factory


AtomForm = modelform_factory(Atom, fields=('name',))

def manage_atom_and_content(request, vers_id, name=None):
    # If pk is provided, we are in UPDATE mode, otherwise INSERT mode
    if name:
        atom = get_object_or_404(Atom, name=name, vers__vers=vers_id)
    else:
        atom = Atom()

    if request.method == 'POST':
        form_atom = AtomForm(request.POST, instance=atom)
        # Pass the article instance into the generic formset
        formset_content = ContentFormSet(request.POST, instance=atom)

        if form_atom.is_valid() and formset_content.is_valid():
            # 1. Save the main article first so it has a valid primary key (ID)
            saved_atom = form_atom.save()

            # 2. Save the formset. Django automatically fills in the
            #    correct content_type and object_id fields on the Note record.
            formset_content.instance = saved_atom
            formset_content.save()

            return redirect('taxonomy:glossary_atom_wver', vers_id=vers_id, atom=name) # Replace with your actual redirect URL route
    else:
        form_atom = AtomForm(instance=atom)
        formset_content = ContentFormSet(instance=atom)

    return render(request, 'django-gem-taxonomy/glossary/manage_atom.html', {
        'form_atom': form_atom,
        'formset_content': formset_content,
        'is_update': name is not None
    })


class GlossaryHome(View):
    def get(self, request):
        template = 'django-gem-taxonomy/glossary/index.html'
        defa_vers = Version.objects.get(is_default=True)

        letter = request.GET.get('letter', '').strip().upper()

        all_items = []

        els = Content.objects.all()
        for el in els:
            if el.content_object.vers != defa_vers:
                continue

            item = {
                'title': el.content_object.title,
                'name': el.content_object.name,
                'vers': el.content_object.vers.vers,
                'type': None,
                'attribute': None
            }

            if isinstance(el.content_object, Atom):
                item['type'] = 'atom'
                item['attribute'] = getattr(el.content_object, 'attribute', None)
                all_items.append(item)
                print(item)
                print(type(el.content_object))
            elif isinstance(el.content_object, Attribute):
                item['type'] = 'attribute'
                all_items.append(item)
                print(item)
                print(type(el.content_object))
            elif isinstance(el.content_object, AtomsGroup):
                item['type'] = 'atoms_group'
                all_items.append(item)
                print(item)
                print(type(el.content_object))

        if letter and len(letter) == 1:
            filtered_items = []
            for item in all_items:
                # Controlla se title o name inizia con la lettera
                if (item['title'] and item['title'][0].upper() == letter) or \
                   (item['name'] and item['name'][0].upper() == letter):
                    filtered_items.append(item)
            all_items = filtered_items

        # All items sort
        all_items.sort(key=lambda x: x['title'].lower())

        all_letters = set()
        for item in all_items:
            if item['title']:
                first_char = item['title'][0].upper()
                if first_char.isalpha():
                    all_letters.add(first_char)
            if item['name']:
                first_char = item['name'][0].upper()
                if first_char.isalpha():
                    all_letters.add(first_char)

        sorted_letters = sorted(list(all_letters))

        context = {
            'all_items': all_items,
            'default_version': defa_vers,
            'total_items': len(all_items),
            'letters': sorted_letters,
            'current_letter': letter
        }

        return render(request, template, context)


class GlossaryAtom(View):
    def get_queryset(self):
        # Prefetches the generic 'note' relation efficiently using 'prefetch_related'
        return super().get_queryset().prefetch_related('content')

    def get(self, request, vers_id=None, atom=None):
        atom_obj = None
        param_obj = None
        other_vers = None
        template = 'django-gem-taxonomy/glossary/atom.html'

        if vers_id is None:
            vers = Version.objects.get(is_default=True)
            if atom is None:
                return redirect('taxonomy:glossary_atoms_wver',
                                vers_id=vers.vers)
            else:
                return redirect('taxonomy:glossary_atoms_wver',
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
                return redirect('taxonomy:glossary_atomsgroups_wver',
                                vers_id=vers.vers)
            else:
                return redirect('taxonomy:glossary_atomsgroup_wver',
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
                return redirect('taxonomy:glossary_attributes_wver',
                                vers_id=vers.vers)
            else:
                return redirect('taxonomy:glossary_attribute_wver',
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
