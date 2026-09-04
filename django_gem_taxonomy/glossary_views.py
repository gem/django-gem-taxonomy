# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2024-2025 GEM Foundation
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
import os
import re
import time

from django.views import View
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Version, Param, Atom, AtomsGroup, Attribute, Content

from .glossary_forms import ContentFormSet
from django.forms import modelform_factory

from django.http import JsonResponse
from django.db import models

class GlossaryAttribute(View):
    def get(self, request, vers_id=None, name=None):
        template = 'django-gem-taxonomy/glossary/attribute.html'
        attribute_obj = None
        other_vers = None

        if vers_id is None:
            vers = Version.objects.get(is_default=True)

            if name is None:
                return redirect('taxonomy:glossary_attributes_wver',
                                vers_id=vers.vers)
            else:
                return redirect('taxonomy:glossary_attribute_wver',
                                vers_id=vers.vers, name=name)
        else:
            vers = Version.objects.get(vers=vers_id)

        if name is None:
            attributes = Attribute.objects.filter(vers=vers).order_by('name')
            attribute_obj = None
            others_objs = Version.objects.all().exclude(vers=vers_id)
            other_vers = [vers for vers in others_objs]
        else:
            attributes = None
            attribute_obj = Attribute.objects.get(vers=vers, name=name)
            others_objs = Attribute.objects.filter(name=name).exclude(vers=vers)
            other_vers = [atoms_group.vers for atoms_group in others_objs]

        return render(request, template, {'attributes': attributes,
                                          'attribute': attribute_obj,
                                          'vers': vers,
                                          'other_vers': other_vers
                                          })


AttributeForm = modelform_factory(AtomsGroup, fields=('name',))

def manage_attribute_content(request, vers_id, name):
    # If pk is provided, we are in UPDATE mode, otherwise INSERT mode
    obj = get_object_or_404(Attribute, name=name, vers__vers=vers_id)

    if request.method == 'POST':
        form_obj = AttributeForm(request.POST, instance=obj)
        # Pass the article instance into the generic formset
        formset_content = ContentFormSet(request.POST, instance=obj)

        if form_obj.is_valid() and formset_content.is_valid():
            # 1. Save the main article first so it has a valid primary key (ID)
            saved_obj = form_obj.save()

            # 2. Save the formset. Django automatically fills in the
            #    correct content_type and object_id fields on the Note record.
            formset_content.instance = saved_obj
            formset_content.save()

            return redirect('taxonomy:glossary_attribute_wver', vers_id=vers_id, name=name)
    else:
        form_obj = AttributeForm(instance=obj)
        formset_content = ContentFormSet(instance=obj)

    return render(request, 'django-gem-taxonomy/glossary/manage_attribute.html', {
        'form_obj': form_obj,
        'formset_content': formset_content,
        'is_update': name is not None
    })


class GlossaryHome(View):
    def get(self, request):
        template = 'django-gem-taxonomy/glossary/index.html'
        defa_vers = Version.objects.get(is_default=True)

        letter = request.GET.get('letter', '').strip().upper()
        search_query = request.GET.get('q', '').strip()
        selected_versions = request.GET.getlist('version')

        all_versions = Version.objects.all().order_by('vers')

        all_items = []
        els = Content.objects.all()

        for el in els:
            if selected_versions:
                if str(el.content_object.vers.vers) not in selected_versions:
                    continue
            else:
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
            elif isinstance(el.content_object, Attribute):
                item['type'] = 'attribute'
            elif isinstance(el.content_object, AtomsGroup):
                item['type'] = 'atoms_group'

            all_items.append(item)

        if letter and len(letter) == 1:
            filtered_items = []
            for item in all_items:
                if (item['title'] and item['title'][0].upper() == letter) or \
                   (item['name'] and item['name'][0].upper() == letter):
                    filtered_items.append(item)
            all_items = filtered_items

        if search_query:
            search_lower = search_query.lower()
            filtered_items = []
            for item in all_items:
                if (item['title'] and search_lower in item['title'].lower()) or \
                   (item['name'] and search_lower in item['name'].lower()):
                    filtered_items.append(item)
            all_items = filtered_items

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
            'current_letter': letter,
            'search_query': search_query,
            'selected_versions': selected_versions,
            'all_versions': all_versions,
        }

        return render(request, template, context)


class GlossarySuggestions(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()

        if not query:
            return JsonResponse({'suggestions': []})

        suggestions = []

        # Title and name search
        if len(query) >= 3:
            # Atom search
            atom_results = Atom.objects.filter(
                models.Q(title__icontains=query) |
                models.Q(name__icontains=query)
            )[:5]

            for obj in atom_results:
                suggestions.append({
                    'type': 'title',
                    'text': obj.title or obj.name,
                    'label': f'📄 {obj.title or obj.name}'
                })

            # Attributes search
            attr_results = Attribute.objects.filter(
                models.Q(title__icontains=query) |
                models.Q(name__icontains=query)
            )[:5]

            for obj in attr_results:
                suggestions.append({
                    'type': 'title',
                    'text': obj.title or obj.name,
                    'label': f'📄 {obj.title or obj.name}'
                })

            # AtomsGroup search
            group_results = AtomsGroup.objects.filter(
                models.Q(title__icontains=query) |
                models.Q(name__icontains=query)
            )[:5]

            for obj in group_results:
                suggestions.append({
                    'type': 'title',
                    'text': obj.title or obj.name,
                    'label': f'📄 {obj.title or obj.name}'
                })

        # Content search
        if len(query) >= 3:
            content_results = Content.objects.filter(
                models.Q(content__icontains=query)
            )[:10]

            for content in content_results:
                obj = content.content_object
                if obj:
                    title = getattr(obj, 'title', None) or getattr(obj, 'name', None)
                    if title:
                        content_text = content.content or ''
                        if content_text:
                            pos = content_text.lower().find(query.lower())
                            if pos != -1:
                                start = max(0, pos - 30)
                                end = min(len(content_text), pos + 60)
                                preview = '...' + content_text[start:end] + '...' if start > 0 else content_text[:end] + '...'
                            else:
                                preview = content_text[:100] + '...'
                        else:
                            preview = ''

                        suggestions.append({
                            'type': 'content',
                            'text': title,
                            'label': f'📝 {title}',
                            'preview': preview
                        })

        # ATOM
        if len(query) >= 1:
            atom_results = Atom.objects.filter(
                models.Q(name__icontains=query)
            )[:10]

            for atom in atom_results:
                suggestions.append({
                    'type': 'atom',
                    'text': atom.name,
                    'label': f'⚛️ {atom.name}'
                })

        # Suggestion number limit
        suggestions = suggestions[:20]

        return JsonResponse({'suggestions': suggestions})


class GlossaryAtomsGroup(View):
    def get(self, request, vers_id=None, name=None):
        template = 'django-gem-taxonomy/glossary/atoms_group.html'
        atoms_group_obj = None
        other_vers = None

        if vers_id is None:
            vers = Version.objects.get(is_default=True)
            if name is None:
                return redirect('taxonomy:glossary_atomsgroups_wver',
                                vers_id=vers.vers)
            else:
                return redirect('taxonomy:glossary_atomsgroup_wver',
                                vers_id=vers.vers, name=name)
        else:
            vers = Version.objects.get(vers=vers_id)

        if name is None:
            atoms_groups = AtomsGroup.objects.filter(vers=vers).order_by('name')
            atoms_group_obj = None
            others_objs = Version.objects.all().exclude(vers=vers_id)
            other_vers = [vers for vers in others_objs]
        else:
            atoms_groups = None
            atoms_group_obj = AtomsGroup.objects.get(vers=vers, name=name)
            others_objs = AtomsGroup.objects.filter(name=name).exclude(vers=vers)
            other_vers = [atoms_group.vers for atoms_group in others_objs]

        return render(request, template, {'atoms_groups': atoms_groups,
                                          'atoms_group': atoms_group_obj,
                                          'vers': vers,
                                          'other_vers': other_vers
                                          })


AtomsGroupForm = modelform_factory(AtomsGroup, fields=('name',))

def manage_atomsgroup_content(request, vers_id, name):
    # If pk is provided, we are in UPDATE mode, otherwise INSERT mode
    obj = get_object_or_404(AtomsGroup, name=name, vers__vers=vers_id)

    if request.method == 'POST':
        form_obj = AtomsGroupForm(request.POST, instance=obj)
        # Pass the article instance into the generic formset
        formset_content = ContentFormSet(request.POST, instance=obj)

        if form_obj.is_valid() and formset_content.is_valid():
            # 1. Save the main article first so it has a valid primary key (ID)
            saved_obj = form_obj.save()

            # 2. Save the formset. Django automatically fills in the
            #    correct content_type and object_id fields on the Note record.
            formset_content.instance = saved_obj
            formset_content.save()

            return redirect('taxonomy:glossary_atomsgroup_wver', vers_id=vers_id, name=name)
    else:
        form_obj = AtomsGroupForm(instance=obj)
        formset_content = ContentFormSet(instance=obj)

    return render(request, 'django-gem-taxonomy/glossary/manage_atomsgroup.html', {
        'form_obj': form_obj,
        'formset_content': formset_content,
        'is_update': name is not None
    })


class GlossaryAtom(View):
    def get_queryset(self):
        # Prefetches the generic 'note' relation efficiently using 'prefetch_related'
        return super().get_queryset().prefetch_related('content')

    def get(self, request, vers_id=None, name=None):
        atom_obj = None
        param_obj = None
        other_vers = None
        template = 'django-gem-taxonomy/glossary/atom.html'

        if vers_id is None:
            vers = Version.objects.get(is_default=True)
            if name is None:
                return redirect('taxonomy:glossary_atoms_wver',
                                vers_id=vers.vers)
            else:
                return redirect('taxonomy:glossary_atoms_wver',
                                vers_id=vers.vers, name=name)
        else:
            vers = Version.objects.get(vers=vers_id)

        if name is None:
            atoms = Atom.objects.filter(vers=vers).order_by('name')
            others_objs = Version.objects.all().exclude(vers=vers_id)
            other_vers = [vers for vers in others_objs]
        else:
            atoms = None
            if ':' in name:
                parts = name.split(':')
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
                atom_obj = Atom.objects.get(vers=vers, name=name)
                others_objs = Atom.objects.filter(name=name).exclude(vers=vers)
                other_vers = [atom.vers for atom in others_objs]

        return render(request, template, {'atoms': atoms,
                                          'atom': atom_obj,
                                          'param': param_obj,
                                          'vers': vers,
                                          'other_vers': other_vers
                                          })

AtomForm = modelform_factory(Atom, fields=('name',))

def manage_atom_content(request, vers_id, name=None):
    # If pk is provided, we are in UPDATE mode, otherwise INSERT mode
    if name:
        obj = get_object_or_404(Atom, name=name, vers__vers=vers_id)
    else:
        obj = Atom()

    if request.method == 'POST':
        form_obj = AtomForm(request.POST, instance=obj)
        # Pass the article instance into the generic formset
        formset_content = ContentFormSet(request.POST, instance=obj)

        if form_obj.is_valid() and formset_content.is_valid():
            # 1. Save the main article first so it has a valid primary key (ID)
            saved_obj = form_obj.save()

            # 2. Save the formset. Django automatically fills in the
            #    correct content_type and object_id fields on the Note record.
            formset_content.instance = saved_obj
            formset_content.save()

            return redirect('taxonomy:glossary_atom_wver', vers_id=vers_id, name=name) # Replace with your actual redirect URL route
    else:
        form_obj = AtomForm(instance=obj)
        formset_content = ContentFormSet(instance=obj)

    return render(request, 'django-gem-taxonomy/glossary/manage_atom.html', {
        'form_obj': form_obj,
        'formset_content': formset_content,
        'is_update': name is not None
    })


def clean_folder_name(name):
    cleaned = re.sub(r'[^a-zA-Z0-9.\-]', '', name)
    cleaned = cleaned.strip('.-')
    if not cleaned:
        cleaned = 'default'
    return cleaned


@csrf_exempt
@require_POST
def custom_upload_file(request):
    """
    Custom view for handling image uploads from CKEditor 5.
    """
    print("=" * 50)
    print("📤 CUSTOM UPLOAD VIEW")
    print(f"POST data: {request.POST}")
    print(f"GET data: {request.GET}")
    print(f"FILES: {request.FILES}")
    print("=" * 50)

    if request.FILES.get("upload"):
        uploaded_file = request.FILES["upload"]

        content_type = uploaded_file.content_type
        if not content_type.startswith('image/'):
            return JsonResponse({"error": {"message": "The file must be an image."}}, status=400)

        version_name = request.POST.get('category', '').strip()
        print(f"📂 Category from POST: '{version_name}'")

        if not version_name:
            version_name = request.GET.get('category', '').strip()
            print(f"📂 Category from GET: '{version_name}'")

        if not version_name:
            version_name = 'default'
            print("⚠️ No category found, using 'default'")
        else:
            print(f"✅ Using category: '{version_name}'")

        version_folder = clean_folder_name(version_name)
        print(f"📁 Category folder: '{version_folder}'")

        name, ext = os.path.splitext(uploaded_file.name)
        safe_name = f"{name}_{int(time.time())}{ext}"

        upload_path = os.path.join("uploads", "version", version_folder, safe_name)
        print(f"📁 Full path: '{upload_path}'")

        file_path = default_storage.save(upload_path, uploaded_file)
        file_url = default_storage.url(file_path)

        print(f"✅ File saved at: {file_url}")
        print("=" * 50)

        return JsonResponse({
            "url": file_url,
            "uploaded": True,
            "fileName": safe_name,
            "category": version_name
        })

    return JsonResponse({"error": {"message": "No file uploaded."}}, status=400)
