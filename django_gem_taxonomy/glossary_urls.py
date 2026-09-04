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
from .glossary_views import (manage_atom_content, manage_atomsgroup_content,
                             manage_attribute_content, custom_upload_file)


urlpatterns = [
    path('attribute/',
         GlossaryAttribute.as_view(), name='glossary_attributes'),
    path('attribute/<str:name>',
         GlossaryAttribute.as_view(), name='glossary_attribute'),

    path('atoms_group/',
         GlossaryAtomsGroup.as_view(), name='glossary_atomsgroups'),
    path('atoms_group/<str:name>',
         GlossaryAtomsGroup.as_view(), name='glossary_atomsgroup'),

    path('atom/',
         GlossaryAtom.as_view(), name='glossary_atoms'),
    path('atom/<str:name>',
         GlossaryAtom.as_view(), name='glossary_atom'),

    # glossary paths with version
    path('<vers_id>/attribute/',
         GlossaryAttribute.as_view(), name='glossary_attributes_wver'),
    path('<vers_id>/attribute/<str:name>',
         GlossaryAttribute.as_view(), name='glossary_attribute_wver'),
    path('<vers_id>/attribute/<str:name>/edit/', manage_attribute_content,
         name='update_attribute_content'),

    path('<vers_id>/atoms_group/',
         GlossaryAtomsGroup.as_view(), name='glossary_atomsgroups_wver'),
    path('<vers_id>/atoms_group/<str:name>',
         GlossaryAtomsGroup.as_view(), name='glossary_atomsgroup_wver'),
    path('<vers_id>/atoms_group/<str:name>/edit/', manage_atomsgroup_content,
         name='update_atomsgroup_content'),

    path('<vers_id>/atom/',
         GlossaryAtom.as_view(), name='glossary_atoms_wver'),
    path('<vers_id>/atom/<str:name>',
         GlossaryAtom.as_view(), name='glossary_atom_wver'),
    path('<vers_id>/atom/<str:name>/edit/', manage_atom_content,
         name='update_atom_content'),

    path('ckeditor5/image_upload/', custom_upload_file, name='custom_upload_file'),
 ]
