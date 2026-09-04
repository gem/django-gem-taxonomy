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

from django.test import TestCase, Client


class ServiceTestCase(TestCase):
    def test_validation(self):
        'Test taxonomy validation service.'

        c = Client()
        response = c.get('/taxonomy/api/v1/validation/S')
        self.assertEqual(response.status_code, 200)

        c = Client()
        response = c.get('/taxonomy/api/v1/validation/S+SL')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['is_canonical'], True)

        response = c.get('/taxonomy/api/v1/validation/SL+S')
        self.assertEqual(response.data['is_canonical'], False)
        self.assertEqual(response.data['canonical'], 'S+SL')
        self.assertEqual(response.status_code, 200)

        response = c.get('/taxonomy/api/v1/validation/S+SL+S')
        self.assertEqual(response.status_code, 400)

        response = c.get('/taxonomy/api/v1/validation/SSSS')
        self.assertEqual(response.data['message'],
                         'Attribute [SSSS]: unknown atom [SSSS].')
        self.assertEqual(response.status_code, 400)

        response = c.get('/taxonomy/api/v1/info')
        self.assertEqual(response.status_code, 200)
