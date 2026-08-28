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
from .glossary_views import GlossaryAtom, GlossaryAtomsGroup, GlossaryAttribute

urlpatterns = [
    path('attribute/',
         GlossaryAttribute.as_view(), name='taxonomy_struct_attributes'),
    path('atom/',
         GlossaryAtom.as_view(), name='taxonomy_struct_atoms'),
    path('atom/<str:atom>',
         GlossaryAtom.as_view(), name='taxonomy_struct_atom'),

    path('atoms_group/',
         GlossaryAtomsGroup.as_view(), name='taxonomy_struct_atomsgroups'),
    path('atoms_group/<str:atoms_group>',
         GlossaryAtomsGroup.as_view(), name='taxonomy_struct_atomsgroup'),

    path('attribute/<str:attribute>',
         GlossaryAttribute.as_view(), name='taxonomy_struct_attribute'),

    # structure paths with version
    path('<vers_id>/attribute/',
         GlossaryAttribute.as_view(), name='taxonomy_struct_attributes_wver'),
    path('<vers_id>/atom/',
         GlossaryAtom.as_view(), name='taxonomy_struct_atoms_wver'),
    path('<vers_id>/atom/<str:atom>',
         GlossaryAtom.as_view(), name='taxonomy_struct_atom_wver'),

    path('<vers_id>/atoms_group/',
         GlossaryAtomsGroup.as_view(), name='taxonomy_struct_atomsgroups_wver'),
    path('<vers_id>/atoms_group/<str:atoms_group>',
         GlossaryAtomsGroup.as_view(), name='taxonomy_struct_atomsgroup_wver'),

    path('<vers_id>/attribute/<str:attribute>',
         GlossaryAttribute.as_view(), name='taxonomy_struct_attribute_wver'),
 ]
