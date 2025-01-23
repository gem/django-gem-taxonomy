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
from .views import TaxtWEB, TaxtGraph, GEMTaxonomyStringValidation
from .views import HelpAtom, HelpAtomsGroup, HelpAttribute

urlpatterns = [
    path('atom/',
         HelpAtom.as_view(), name='taxonomy_helpatoms'),
    path('atom/<str:atom>',
         HelpAtom.as_view(), name='taxonomy_helpatom'),

    path('atoms_group/',
         HelpAtomsGroup.as_view(), name='taxonomy_helpatomsgroups'),
    path('atoms_group/<str:atoms_group>',
         HelpAtomsGroup.as_view(), name='taxonomy_helpatomsgroup'),

    path('attribute/',
         HelpAttribute.as_view(), name='taxonomy_helpattributes'),
    path('attribute/<str:attribute>',
         HelpAttribute.as_view(), name='taxonomy_helpattribute'),

    path('taxtweb/',
         TaxtWEB.as_view(), name='taxonomy_taxtweb'),
    path('graph/',
         TaxtGraph.as_view(), name='taxonomy_taxtgraph'),

    path('api/v1/validation/<str:taxonomy_string>',
         GEMTaxonomyStringValidation.as_view(), name='taxonomy_validation'),
 ]
# [A-Z0-9]+
