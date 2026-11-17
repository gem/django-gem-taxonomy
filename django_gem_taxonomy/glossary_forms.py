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

from django import forms
from django.forms import modelform_factory
from django.forms.renderers import get_default_renderer
from django.urls import reverse
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from .models import (Attribute, AtomsGroup, Atom, Param, VersRelatedContent,
                     Content)
from django_ckeditor_5.widgets import CKEditor5Widget


class VersionedCKEditor5Widget(CKEditor5Widget):
    """CKEditor5 widget with a per-instance image upload url."""

    def __init__(self, upload_url, **kwargs):
        self.upload_url = upload_url
        super().__init__(**kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        # CKEditor5Widget.render() always sets 'upload_url' to the global
        # upload view (CK_EDITOR_5_UPLOAD_FILE_VIEW_NAME or django_ckeditor_5
        # 'ck_editor_5_upload_file'): override it just before the template
        # is rendered
        if renderer is None:
            renderer = get_default_renderer()
        upload_url = self.upload_url

        class UploadUrlRenderer:
            def render(self, template_name, context, request=None):
                context['upload_url'] = upload_url
                return renderer.render(template_name, context, request=request)

        return super().render(name, value, attrs=attrs,
                              renderer=UploadUrlRenderer())


class VersionedContentForm(forms.ModelForm):
    """Content form where images are uploaded in a per-version folder."""

    class Meta:
        model = Content
        fields = ['content']

    def __init__(self, *args, vers_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget = VersionedCKEditor5Widget(
            upload_url=reverse('taxonomy:glossary_upload_file_wver',
                               kwargs={'vers_id': vers_id}),
            attrs={'class': 'django_ckeditor_5'},
            config_name='extends'
        )

# must be instantiated with form_kwargs={'vers_id': ...}
VersionedContentFormSet = generic_inlineformset_factory(
    Content, form=VersionedContentForm, extra=1, max_num=1, validate_max=True)

class AttributeFormForm(forms.ModelForm):
    name = forms.CharField(disabled=True, required=False)
    title = forms.CharField(disabled=True, required=False)

    class Meta:
        model = Attribute
        fields = ['name', 'title']

AttributeForm = modelform_factory(Attribute, form=AttributeFormForm)


class AtomsGroupFormForm(forms.ModelForm):
    name = forms.CharField(disabled=True, required=False)
    title = forms.CharField(disabled=True, required=False)

    class Meta:
        model = AtomsGroup
        fields = ['name', 'title']

AtomsGroupForm = modelform_factory(AtomsGroup, form=AtomsGroupFormForm)

class AtomFormForm(forms.ModelForm):
    name = forms.CharField(disabled=True, required=False)
    title = forms.CharField(disabled=True, required=False)

    class Meta:
        model = Atom
        fields = ['name', 'title']

AtomForm = modelform_factory(Atom, form=AtomFormForm)

class ParamFormForm(forms.ModelForm):
    param_atom = forms.CharField(label="Parametrized Atom", disabled=True, required=False)
    title = forms.CharField(disabled=True, required=False)

    class Meta:
        model = Param
        fields = ['param_atom', 'title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and getattr(self.instance, 'atom', None):
            self.fields['param_atom'].initial = self.instance.atom.name + ':' + self.instance.name
ParamForm = modelform_factory(Param, form=ParamFormForm)

class VersRelatedContentFormForm(forms.ModelForm):
    title = forms.CharField(disabled=True, required=False)

    class Meta:
        model = VersRelatedContent
        fields = ['title']

VersRelatedContentForm = modelform_factory(VersRelatedContent,
                                           form=VersRelatedContentFormForm)
