# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# oq-geoviewer
# Copyright (C) 2018-2019 GEM Foundation
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

from django.urls import path
from .glossary_views import GlossaryAtom, GlossaryAtomsGroup, GlossaryAttribute, GlossaryHome, GlossarySuggestions
from .glossary_views import manage_atom_and_content


urlpatterns = [
    path('', GlossaryHome.as_view(), name='glossary_home'),
    path('suggestions/', GlossarySuggestions.as_view(), name='glossary_suggestions'),

    path('attribute/',
         GlossaryAttribute.as_view(), name='glossary_attributes'),
    path('atom/',
         GlossaryAtom.as_view(), name='glossary_atoms'),
    path('atom/<str:atom>',
         GlossaryAtom.as_view(), name='glossary_atom'),

    path('atoms_group/',
         GlossaryAtomsGroup.as_view(), name='glossary_atomsgroups'),
    path('atoms_group/<str:atoms_group>',
         GlossaryAtomsGroup.as_view(), name='glossary_atomsgroup'),

    path('attribute/<str:attribute>',
         GlossaryAttribute.as_view(), name='glossary_attribute'),

    # glossary paths with version
    path('<vers_id>/attribute/',
         GlossaryAttribute.as_view(), name='glossary_attributes_wver'),
    path('<vers_id>/atom/',
         GlossaryAtom.as_view(), name='glossary_atoms_wver'),
    path('<vers_id>/atom/<str:atom>',
         GlossaryAtom.as_view(), name='glossary_atom_wver'),

    path('<vers_id>/atoms_group/',
         GlossaryAtomsGroup.as_view(), name='glossary_atomsgroups_wver'),
    path('<vers_id>/atoms_group/<str:atoms_group>',
         GlossaryAtomsGroup.as_view(), name='glossary_atomsgroup_wver'),

    path('<vers_id>/attribute/<str:attribute>',
         GlossaryAttribute.as_view(), name='glossary_attribute_wver'),

    path('<vers_id>/atom/new/', manage_atom_and_content, name='create_atom'),
    path('<vers_id>/atom/<str:name>/edit/', manage_atom_and_content, name='update_atom'),
 ]
