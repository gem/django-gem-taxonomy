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

# import subprocess
# from django.conf import settings
import os
from django.core.management import call_command
from openquake import gem_taxonomy_data
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ("Standard command that will be runned by OpenQuake Engine 'install.py'"
            " installer for each django application, if it exists.")

    def handle(self, *args, **options):
        data_path = os.path.join(os.path.dirname(gem_taxonomy_data.__file__), 'data')
        data_file = os.listdir(data_path)[-1]
        print("Data_file: [%s]" % data_file)
        call_command('migrate', 'django_gem_taxonomy', 'zero')
        call_command('migrate', 'django_gem_taxonomy')
        call_command('taxonomy_load_standard', "--no-dump", os.path.join(data_path, data_file))
