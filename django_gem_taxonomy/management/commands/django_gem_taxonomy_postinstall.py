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

import os
from django.core.management import call_command
from openquake import gem_taxonomy_data
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ("Standard command that will be runned by OpenQuake Engine 'install.py'"
            " installer for each django application, if it exists.")

    def handle(self, *args, **options):
        data_path = os.path.join(os.path.dirname(gem_taxonomy_data.__file__), 'data')
        # OLD VERSION, NOW WE MUST FORCE THE 4.0 UNTIL WE WILL LOAD BOTH'
        # data_file = os.listdir(data_path)[-1]
        call_command('migrate', 'django_gem_taxonomy', 'zero', interactive=False)
        call_command('migrate', 'django_gem_taxonomy', interactive=False)

        # first iteration set the taxonomy_standard default
        for data in [
                    {'vers_id': '4.0',
                     'vers_desc': 'Version 4.0 year 2025',
                     'is_default': True,
                     'fname': 'taxonomy4.0_standard.json'},
                    {'vers_id': '3.3',
                     'vers_desc': 'Version 3.3 year 2024',
                     'is_default': False,
                     'fname': 'taxonomy3.3_standard.json'}
                ]:
            print("Data_file: [%s]" % data['fname'])
            call_args = ['taxonomy_load_standard', data['vers_id'], data['vers_desc'], '--no-dump']
            if data['is_default']:
                call_args.append('--is-default')
            call_args.append(os.path.join(data_path, data['fname']))

            call_command(*call_args)
