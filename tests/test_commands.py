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

import sys
from io import StringIO
from django.core.management import call_command
from django.test import TestCase, TransactionTestCase


class CommandsTestCase(TestCase):
    def test_taxonomy_load_standard(self):
        "Test taxonomy_load_standard command."
        
        data = {'vers_id': '3.3',
                'vers_desc': 'Version 3.3 year 2024',
                'is_default': True,
                'fname': 'tests/data/taxonomy3.3_standard.json'}

        call_args = ['taxonomy_load_standard', data['vers_id'], data['vers_desc'], '--no-dump']
        if data['is_default']:
            call_args.append('--is-default')
        call_args.append(data['fname'])
        call_opts = {}
        v_file = StringIO()
        stdout_backup, sys.stdout = sys.stdout, v_file
        call_command(*call_args, **call_opts)
        sys.stdout = stdout_backup

class PostInstallTestCase(TransactionTestCase):
    def test_django_gem_taxonomy_postinstall(self):
        "Test django_gem_taxonomy_postinstall command."

        call_args = ['django_gem_taxonomy_postinstall']
        call_opts = {}
        v_file = StringIO()
        stdout_backup, sys.stdout = sys.stdout, v_file
        call_command(*call_args, **call_opts)
        sys.stdout = stdout_backup
