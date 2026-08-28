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

from django.urls import path, include
from django.views.generic import TemplateView

app_name = 'taxonomy'

urlpatterns = [
    path('', TemplateView.as_view(template_name='django-gem-taxonomy/homepage/homepage.html'),
         name='home'),

    path('api/v1/', include('django_gem_taxonomy.api_v1_urls')),
    path('graph/', include('django_gem_taxonomy.graph_urls')),
    path('structure/', include('django_gem_taxonomy.structure_urls')),
    path('glossary/', include('django_gem_taxonomy.glossary_urls')),

 ]
