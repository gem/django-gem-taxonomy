# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# django-gem-taxonomy
# Copyright (C) 2026 GEM Foundation
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

from django import template
from django.urls import resolve, reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def other_vers(context, **kwargs):
    """
    Rigenera l'URL della view corrente modificando solo i parametri del path specificati.
    """
    request = context['request']
    
    # 1. Recupera il nome della view corrente e i suoi parametri attuali
    match = resolve(request.path_info)
    view_name = match.view_name
    current_kwargs = match.kwargs.copy()

    current_kwargs.update(kwargs)
    
    # 2. Sovrascrive i parametri con i nuovi valori passati dal template
    current_kwargs.update(kwargs)
    
    # 3. Ricostruisce l'URL strutturale
    try:
        return reverse(view_name, kwargs=current_kwargs)
    except Exception:
        return "#" # Ritorna un link vuoto in caso di errore nei parametri

