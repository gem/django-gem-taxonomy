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

from django.contrib.contenttypes.forms import generic_inlineformset_factory
from .models import Content
from django_ckeditor_5.widgets import CKEditor5Widget

def assign_ckeditor(db_field, **kwargs):
    if db_field.name == 'content':
        kwargs['widget'] = CKEditor5Widget(
            attrs={'class': 'django_ckeditor_5'},
            config_name='extends'
        )
    return db_field.formfield(**kwargs)

# Create a generic inline formset for the Note model.
# - extra=1: Displays one empty field to add a new note.
# - max_num=1: (Optional) Set this if you want to limit it to exactly one note per object.
ContentFormSet = generic_inlineformset_factory(Content, fields=('content',),
                                               formfield_callback=assign_ckeditor,
                                               extra=1, max_num=1, validate_max=True)
