from django.core.management import call_command
from django.test import TestCase

class CommandsTestCase(TestCase):
    def test_taxonomy_load_standard(self):
        "Test taxonomy_load_standard command."

        args = ['tests/data/taxonomy3.3_standard.json']
        opts = {}
        call_command('taxonomy_load_standard', *args, **opts)

