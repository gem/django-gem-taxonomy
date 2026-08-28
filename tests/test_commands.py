import sys
from io import StringIO
from django.core.management import call_command
from django.test import TestCase


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
