# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# django_gem_taxonomy
# Copyright (C) 2024-2025 GEM Foundation
#
# django_gem_taxonomy is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django_gem_taxonomy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.views import View
from django.shortcuts import render, redirect
from .models import Version


class TaxGraph(View):
    def get(self, request, vers_id=None):
        template = 'django-gem-taxonomy/taxgraph/taxgraph.html'

        if vers_id is None:
            vers = Version.objects.get(is_default=True)
            return redirect('taxonomy:taxonomy_taxgraph_wver',
                            vers_id=vers.vers)
        else:
            vers = Version.objects.get(vers=vers_id)

        others_objs = Version.objects.all().exclude(vers=vers.vers)
        other_vers = [vers for vers in others_objs]

        return render(request, template, {
            'vers': vers,
            'other_vers': other_vers
        })
