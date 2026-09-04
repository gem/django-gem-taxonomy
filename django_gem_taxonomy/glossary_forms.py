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
from .models import Atom, Content

# Create a generic inline formset for the Note model.
# - extra=1: Displays one empty field to add a new note.
# - max_num=1: (Optional) Set this if you want to limit it to exactly one note per object.
ContentFormSet = generic_inlineformset_factory(Content, fields=('content',), extra=1, max_num=1, validate_max=True)
