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

from django import template
from django.urls import resolve, reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def other_vers(context, **kwargs):
    """
    Regenerate the current view's URL by modifying only the specified path parameters.
    """
    request = context['request']
    
    # 1. Retrieves the current view name and its current parameters.
    match = resolve(request.path_info)
    view_name = match.view_name
    current_kwargs = match.kwargs.copy()

    current_kwargs.update(kwargs)
    
    # 2. Overrides parameters with the new values passed from the template.
    current_kwargs.update(kwargs)
    
    # 3. Reconstructs the structural URL.
    try:
        return reverse(view_name, kwargs=current_kwargs)
    except Exception:
        return "#" # Returns an empty link in case of a parameter error.

