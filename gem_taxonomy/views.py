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

#  DEVELOPMENT: to investigate SQL query produded by the ORM
#               use this 2 lines of code from pdb
#
# import sqlparse
# print(sqlparse.format(feahis.query.__str__(), reindent=True, keyword_case='upper'))

# import re
# import csv
# import math
# import datetime
from django.views import View
# from django.http import HttpResponse
# from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render
# from django.core.exceptions import PermissionDenied
# from django.db.models import (Count, F)
# from django.db.models.functions import (
#     Upper, Lower, Cast)
# from django.core.paginator import Paginator
# from subscription.models import Company
# from subscription.models import (APISubscriber, APISubscription,
#                                  APIFeatureHistory)
# from subscription.models import (WEBSubscriber, WEBSubscription,
#                                  WEBFeatureHistory)
# import django_filters
# from django_filters import DateTimeFromToRangeFilter
# from django_filters.widgets import RangeWidget

from django.conf import settings

# from django.db.models import DateField, TimeField
# from oqgeoviewer.filters import DateTimeFromToRangeFilterGEM
from .models import Atom, AtomsGroup, Attribute


class TaxtWEB(View):
    def get(self, request):
        template = 'taxtweb.html'
        return render(request, template, {})


class TaxtGraph(View):
    def get(self, request):
        template = 'taxtgraph.html'
        return render(request, template, {})


class HelpAtom(View):
    def get(self, request, atom=None):
        template = 'help_atom.html'

        if atom is None:
            atoms = Atom.objects.all().order_by('name')
        else:
            atoms = None
            atom = Atom.objects.get(name=atom)

        return render(request, template, {'atoms': atoms,
                                          'atom': atom})


class HelpAtomsGroup(View):
    def get(self, request, atoms_group=None):
        template = 'help_atoms_group.html'

        if atoms_group is None:
            atoms_groups = AtomsGroup.objects.all().order_by('prog')
            atoms_group = None
        else:
            atoms_groups = None
            atoms_group = AtomsGroup.objects.get(name=atoms_group)

        # import pdb ; pdb.set_trace()
        return render(request, template, {'atoms_groups': atoms_groups,
                                          'atoms_group': atoms_group})


class HelpAttribute(View):
    def get(self, request, attribute=None):
        template = 'help_attribute.html'

        if attribute is None:
            attributes = Attribute.objects.all().order_by('name')
            attribute = None
        else:
            attributes = None
            attribute = Attribute.objects.get(name=attribute)

        return render(request, template, {'attributes': attributes,
                                          'attribute': attribute})




# def last_day_of_month(any_day):
#     # The day 28 exists in every month. 4 days later, it's always next month
#     next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
#     # subtracting the number of the current day brings us back one month
#     return next_month - datetime.timedelta(days=next_month.day)


# class NonModelChoiceFilter(django_filters.ChoiceFilter):
#     def filter(self, qs, value):
#         return qs


# def APISubscriptionsReport(request):
#     # DEV: for test purposes use it instead of utcnow:
#     # now = datetime.date(2024, 10, 1)
#     now = datetime.datetime.utcnow()
#     quarter_choices = tuple()
#     csv_quarter_choices = tuple()
#     for x in range(now.month, now.month - 24, -3):
#         quarter = math.ceil((((x - 1) % 12) + 1) / 3.0)
#         year = now.year + math.ceil(x / 12.0) - 1
#         if year < 2023:
#             break

#         quarter_choices += ((
#             "%04d%02d" % (year, quarter), 'Q%d %d' % (quarter, year)),)
#         csv_quarter_choices += ((
#             "%04d%02d" % (year, quarter), 'Q%d %d' % (quarter, year)),)

#     class CompanyFilter(django_filters.FilterSet):
#         name = django_filters.CharFilter(
#             label="Company name contains",
#             field_name='name', lookup_expr='icontains')

#         quarter = NonModelChoiceFilter(
#             label="Period:", empty_label="(not set)",
#             choices=quarter_choices)

#         validity_period = DateTimeFromToRangeFilterGEM(
#             field_name='apisubscription__validity_period',
#             label='Validity period (UTC)',
#             widget=RangeWidget(attrs={'type': 'datetime-local'}),
#             lookup_expr='overlap')

#         class Meta:
#             model = Company
#             fields = ['name', 'quarter', 'validity_period']
#             filter_overrides = {
#                 'filter_class': DateTimeRangeFieldGEM,
#                 'extra': lambda f: {'lookup_expr': 'overlap'}
#             }

#     class CSVFilter(django_filters.FilterSet):
#         csv_name = django_filters.CharFilter(
#             label='Company name contains',
#             field_name='subscription__company__name',
#             lookup_expr='icontains')

#         csv_quarter = NonModelChoiceFilter(
#             label="Period:", empty_label="(not set)",
#             choices=csv_quarter_choices)

#         csv_first_accessed_at = DateTimeFromToRangeFilter(
#             field_name='first_accessed_at',
#             label='Request date range (UTC)',
#             widget=RangeWidget(attrs={'type': 'datetime-local'})
#         )

#         class Meta:
#             model = APIFeatureHistory
#             fields = ['csv_name', 'csv_quarter', 'csv_first_accessed_at']

#     if ('quarter' in request.GET and
#         request.GET['quarter'] and
#             len(request.GET['quarter']) == 6 and
#             re.findall(r'^\d{6}$', request.GET['quarter'])):
#         cur_period = request.GET['quarter']
#         cur_quarter_year = int(cur_period[0:4])
#         cur_quarter_numb = int(cur_period[4:6])
#         temp_get = request.GET.copy()
#         # validity_period_min=2023-12-05T15%3A36&validity_period_max=2023-12-05T15%3A36
#         temp_get['validity_period_min'] = (
#             '%04d-%02d-01T00:00' % (cur_quarter_year,
#                                     ((cur_quarter_numb - 1) * 3) + 1))

#         last_day = last_day_of_month(datetime.date(
#             int(cur_quarter_year), cur_quarter_numb * 3, 1))

#         temp_get['validity_period_max'] = (
#             '%04d-%02d-%02dT23:59' % (cur_quarter_year,
#                                       cur_quarter_numb * 3,
#                                       last_day.day))
#         del temp_get['quarter']
#         request.GET = temp_get
#     if not request.user.is_authenticated:
#         return redirect_to_login(request.get_full_path())

#     # TODO extend full_report to a specific administration group
#     full_report = request.user.is_superuser
#     if full_report:
#         get_csv = True
#         companies = Company.objects.all()
#     else:
#         try:
#             APISubscriber.objects.get(
#                 user=request.user)
#         except APISubscriber.DoesNotExist:
#             return HttpResponse('You are not an api subscriber')
#         companies = Company.objects.filter(
#             apisubscription__apisubscriber__user=request.user)
#         get_csv = settings.SUBSCRIPTIONS_CSV_FOR_USERS

#     subscriptions = companies.order_by(
#                 'name',
#                 'apisubscription__validity_period__startswith',
#             ).values(
#                 'name',
#                 'apisubscription__id',
#                 'apisubscription__project__name',
#                 'apisubscription__team',
#                 'apisubscription__project__map__name',
#                 'apisubscription__validity_period',
#                 'apisubscription__features_credit',
#             ).annotate(num_apifeat_hist=Count(
#                 'apisubscription__apifeaturehistory'))

#     com_filter = CompanyFilter(request.GET, subscriptions)
#     csv_filter = CSVFilter(request.GET, subscriptions)

#     template = 'api_subscriptions_report.html'
#     return render(
#         request, template, {
#             'full_report': full_report,
#             'get_csv': get_csv,
#             'com_filter': com_filter,
#             'csv_filter': csv_filter,
#             'subscriptions': com_filter.qs,
#         })




# def APISubscriptionsBilling(request):
#     if not request.user.is_authenticated:
#         return redirect_to_login(request.get_full_path())

#     class CSVFilter(django_filters.FilterSet):
#         csv_name = django_filters.CharFilter(
#             label='Company name contains',
#             field_name='subscription__company__name',
#             lookup_expr='icontains')

#         csv_first_accessed_at = DateTimeFromToRangeFilter(
#             label='Request date range (UTC)',
#             field_name='first_accessed_at',
#             widget=RangeWidget(attrs={'type': 'datetime-local'})
#         )

#         class Meta:
#             model = APIFeatureHistory
#             fields = ['csv_name', 'csv_first_accessed_at']

#     if ('csv_quarter' in request.GET and
#         request.GET['csv_quarter'] and
#             len(request.GET['csv_quarter']) == 6 and
#             re.findall(r'^\d{6}$', request.GET['csv_quarter'])):
#         cur_period = request.GET['csv_quarter']
#         cur_quarter_year = int(cur_period[0:4])
#         cur_quarter_numb = int(cur_period[4:6])
#         temp_get = request.GET.copy()
#         # validity_period_min=2023-12-05T15%3A36&validity_period_max=2023-12-05T15%3A36
#         temp_get['csv_first_accessed_at_min'] = (
#             '%04d-%02d-01T00:00' % (cur_quarter_year,
#                                     ((cur_quarter_numb - 1) * 3) + 1))

#         last_day = last_day_of_month(datetime.date(
#             int(cur_quarter_year), cur_quarter_numb * 3, 1))

#         temp_get['csv_first_accessed_at_max'] = (
#             '%04d-%02d-%02dT23:59' % (cur_quarter_year,
#                                       cur_quarter_numb * 3,
#                                       last_day.day))
#         del temp_get['csv_quarter']
#         request.GET = temp_get

#     feahis = APIFeatureHistory.objects.all()
#     feahis = feahis.select_related(
#         'subscription')
#     feahis = feahis.select_related(
#         'subscription__company')
#     full_report = request.user.is_superuser

#     if full_report is False:
#         if not settings.SUBSCRIPTIONS_CSV_FOR_USERS:
#             raise PermissionDenied

#         try:
#             APISubscriber.objects.get(
#                 user=request.user)
#         except APISubscriber.DoesNotExist:
#             return HttpResponse('You are not an api subscriber')
#         feahis = feahis.filter(subscription__user=request.user)

#     if not feahis:
#         raise APISubscriber.DoesNotExist(
#                 'Not available subscriptions for this user')

#     csvFilter = CSVFilter(request.GET, feahis)
#     feahis = csvFilter.qs

#     field_names = (
#         'subscription__company__name',
#         'subscription__id',
#         'job_id',
#         'subscription__team',
#         'subscription__project__map__name',
#         'subscription__features_credit',
#         'subscription__validity_period',
#         )

#     feahis = feahis.order_by(
#         'subscription__company__name', 'job_id').values(
#             *field_names
#         ).annotate(
#             feature_requests=Count('subscription_id'),
#             subscription__validity_period__lower__date=Cast(
#                 Lower('subscription__validity_period'),
#                 output_field=DateField()),
#             subscription__validity_period__lower__time=Cast(
#                 Lower('subscription__validity_period'),
#                 output_field=TimeField()),
#             subscription__validity_period__upper__date=Cast(
#                 Upper('subscription__validity_period'),
#                 output_field=DateField()),
#             subscription__validity_period__upper__time=Cast(
#                 Upper('subscription__validity_period'),
#                 output_field=TimeField())
#         )
#     response = HttpResponse(
#         content_type="text/csv",
#         headers={
#             "Content-Disposition":
#             'attachment; filename="api_subscription_full_report.csv"'},
#         )
#     writer = csv.writer(response)
#     writer.writerow(field_names + (
#         'feature_requests',
#         'subscription__validity_period__lower__date',
#         'subscription__validity_period__lower__time',
#         'subscription__validity_period__upper__date',
#         'subscription__validity_period__upper__time',
#         ))

#     for fh in feahis:
#         feat_hist = [fh[x] for x in field_names + (
#             'feature_requests',
#             'subscription__validity_period__lower__date',
#             'subscription__validity_period__lower__time',
#             'subscription__validity_period__upper__date',
#             'subscription__validity_period__upper__time',
#             ) if x in fh]

#         writer.writerow(feat_hist)

#     return response


# def WEBSubscriptionsReport(request):
#     # DEV: for test purposes use it instead of utcnow:
#     # now = datetime.date(2024, 10, 1)
#     now = datetime.datetime.utcnow()
#     quarter_choices = tuple()
#     csv_quarter_choices = tuple()
#     for x in range(now.month, now.month - 24, -3):
#         quarter = math.ceil((((x - 1) % 12) + 1) / 3.0)
#         year = now.year + math.ceil(x / 12.0) - 1
#         if year < 2023:
#             break

#         quarter_choices += ((
#             "%04d%02d" % (year, quarter), 'Q%d %d' % (quarter, year)),)
#         csv_quarter_choices += ((
#             "%04d%02d" % (year, quarter), 'Q%d %d' % (quarter, year)),)

#     class CompanyFilter(django_filters.FilterSet):
#         name = django_filters.CharFilter(
#             label="Company name contains",
#             field_name='name', lookup_expr='icontains')

#         quarter = NonModelChoiceFilter(
#             label="Period:", empty_label="(not set)",
#             choices=quarter_choices)

#         validity_period = DateTimeFromToRangeFilterGEM(
#             field_name='websubscription__validity_period',
#             label='Validity period (UTC)',
#             widget=RangeWidget(attrs={'type': 'datetime-local'}),
#             lookup_expr='overlap')

#         class Meta:
#             model = Company
#             fields = ['name', 'quarter', 'validity_period']
#             filter_overrides = {
#                 'filter_class': DateTimeRangeFieldGEM,
#                 'extra': lambda f: {'lookup_expr': 'overlap'}
#             }

#     class CSVFilter(django_filters.FilterSet):
#         csv_name = django_filters.CharFilter(
#             label='Company name contains',
#             field_name='subscription__company__name',
#             lookup_expr='icontains')

#         csv_quarter = NonModelChoiceFilter(
#             label="Period:", empty_label="(not set)",
#             choices=csv_quarter_choices)

#         csv_first_accessed_at = DateTimeFromToRangeFilter(
#             field_name='first_accessed_at',
#             label='Request date range (UTC)',
#             widget=RangeWidget(attrs={'type': 'datetime-local'})
#         )

#         class Meta:
#             model = WEBFeatureHistory
#             fields = ['csv_name', 'csv_quarter', 'csv_first_accessed_at']

#     if ('quarter' in request.GET and
#         request.GET['quarter'] and
#             len(request.GET['quarter']) == 6 and
#             re.findall(r'^\d{6}$', request.GET['quarter'])):
#         cur_period = request.GET['quarter']
#         cur_quarter_year = int(cur_period[0:4])
#         cur_quarter_numb = int(cur_period[4:6])
#         temp_get = request.GET.copy()
#         # validity_period_min=2023-12-05T15%3A36&validity_period_max=2023-12-05T15%3A36
#         temp_get['validity_period_min'] = (
#             '%04d-%02d-01T00:00' % (cur_quarter_year,
#                                     ((cur_quarter_numb - 1) * 3) + 1))

#         last_day = last_day_of_month(datetime.date(
#             int(cur_quarter_year), cur_quarter_numb * 3, 1))

#         temp_get['validity_period_max'] = (
#             '%04d-%02d-%02dT23:59' % (cur_quarter_year,
#                                       cur_quarter_numb * 3,
#                                       last_day.day))
#         del temp_get['quarter']
#         request.GET = temp_get
#     if not request.user.is_authenticated:
#         return redirect_to_login(request.get_full_path())

#     # TODO extend full_report to a specific administration group
#     full_report = request.user.is_superuser
#     if full_report:
#         get_csv = True
#         companies = Company.objects.all()
#     else:
#         try:
#             WEBSubscriber.objects.get(
#                 user=request.user)
#         except WEBSubscriber.DoesNotExist:
#             return HttpResponse('You are not an web subscriber')
#         companies = Company.objects.filter(
#             websubscription__websubscriber__user=request.user)
#         get_csv = settings.SUBSCRIPTIONS_CSV_FOR_USERS

#     subscriptions = companies.order_by(
#                 'name',
#                 'websubscription__validity_period__startswith',
#             ).values(
#                 'name',
#                 'websubscription__id',
#                 'websubscription__project__name',
#                 'websubscription__team',
#                 'websubscription__project__map__name',
#                 'websubscription__validity_period',
#                 'websubscription__features_credit',
#             ).annotate(num_webfeat_hist=Count(
#                 'websubscription__webfeaturehistory'))

#     com_filter = CompanyFilter(request.GET, subscriptions)
#     csv_filter = CSVFilter(request.GET, subscriptions)

#     template = 'web_subscriptions_report.html'
#     return render(
#         request, template, {
#             'full_report': full_report,
#             'get_csv': get_csv,
#             'com_filter': com_filter,
#             'csv_filter': csv_filter,
#             'subscriptions': com_filter.qs,
#         })

# class WEBSubscriptionsReportDetail(View):
#     def get(self, request, subscr_id):
#         if not request.user.is_authenticated:
#             return redirect_to_login(request.get_full_path())
#         full_report = request.user.is_superuser

#         now = datetime.datetime.utcnow()
#         quarter_choices = tuple()
#         for x in range(now.month, now.month - 24, -3):
#             quarter = math.ceil((((x - 1) % 12) + 1) / 3.0)
#             year = now.year + math.ceil(x / 12.0) - 1
#             if year < 2023:
#                 break

#             quarter_choices += ((
#                 "%04d%02d" % (year, quarter), 'Q%d %d' % (quarter, year)),)

#         class DetailFilter(django_filters.FilterSet):
#             quarter = NonModelChoiceFilter(
#                 label="Period:", empty_label="(not set)",
#                 choices=quarter_choices)

#             first_accessed_at = DateTimeFromToRangeFilter(
#                 label='Request date range (UTC)',
#                 widget=RangeWidget(attrs={'type': 'datetime-local'})
#             )

#             username = django_filters.CharFilter(
#                 label="Username",
#                 field_name='first_accessed_by__user__username')

#             class Meta:
#                 model = WEBFeatureHistory
#                 fields = ['quarter', 'first_accessed_at', 'username']

#         subscription = WEBSubscription.objects.filter(id=subscr_id)
#         if full_report is False:
#             if not subscription.filter(websubscriber__user=request.user):
#                 raise PermissionDenied('You are not an web subscriber')

#         feahis = WEBFeatureHistory.objects.filter(subscription=subscr_id)
#         detail_filter = DetailFilter(request.GET, feahis)

#         subscription = subscription.annotate(
#             company_name=F('company__name'),
#             project_name=F('project__name'),
#             project_map_name=F('project__map__name'),
#         ).values(
#             'company_name',
#             'id',
#             'project_name',
#             'team',
#             'project_map_name',
#             'validity_period',
#             'features_credit'
#         )

#         feahises_num = len(feahis)
#         feahis = detail_filter.qs.annotate(
#             first_accessed_by_user_first_name=F(
#                 'first_accessed_by__user__first_name'),
#             first_accessed_by_user_last_name=F(
#                 'first_accessed_by__user__last_name'),
#             first_accessed_by_user_username=F(
#                 'first_accessed_by__user__username')
#         ).values(
#                 'gem_id',
#                 'lon',
#                 'lat',
#                 'first_accessed_at',
#                 'first_accessed_by_user_first_name',
#                 'first_accessed_by_user_last_name',
#                 'first_accessed_by_user_username',
#                 'downloads'
#         ).order_by(
#             'first_accessed_at',
#         )
#         feahises_vis = len(detail_filter.qs)
#         feahis_paginator = Paginator(feahis, 100)
#         page_number = request.GET.get("page")
#         feahises_page = feahis_paginator.get_page(page_number)

#         url_params = detail_filter.data.copy()
#         if 'page' in url_params:
#             url_params.pop('page')
#         if url_params:
#             page_params = url_params.urlencode()
#         else:
#             page_params = ''

#         template = 'web_subscriptions_report_detail.html'
#         return render(
#             request, template, {
#                 'detail_filter': detail_filter,
#                 'page_params': page_params,
#                 'full_report': False,
#                 'subscription': subscription[0],
#                 'feahises': feahises_page,
#                 'page_obj': feahises_page,
#                 'feahises_num': feahises_num,
#                 'feahises_vis': feahises_vis,
#             })


# class WEBSubscriptionsBilling(View):
#     def get(self, request):
#         if not request.user.is_authenticated:
#             return redirect_to_login(request.get_full_path())

#         # TODO extend full_report to a specific administration group
#         full_report = request.user.is_superuser
#         if full_report:
#             feature_histories = WEBFeatureHistory.objects.all().order_by(
#                 'subscription__company__name', 'subscription__project__name'
#                 )
#         else:
#             if settings.SUBSCRIPTIONS_CSV_FOR_USERS:
#                 # CSV enabled for customers
#                 try:
#                     subscriber = WEBSubscriber.objects.get(user=request.user)
#                 except WEBSubscriber.DoesNotExist:
#                     return HttpResponse('You are not a web subscriber')
#                 feature_histories = WEBFeatureHistory.objects.filter(
#                     subscription__company=subscriber.company).order_by(
#                     'subscription__company__name',
#                     'subscription__project__name'
#                     )
#             else:
#                 # CSV disabled for customers
#                 raise PermissionDenied

#         response = HttpResponse(
#             content_type="text/csv",
#             headers={
#                 "Content-Disposition":
#                 'attachment; filename="web_subscription_full_report.csv"'},
#             )
#         writer = csv.writer(response)
#         writer.writerow(('company name', 'team', 'project name',
#                          'validity (from)', 'validity (to)', 'job id',
#                          'lon', 'lat', 'gem id', 'first accessed at',
#                          'first accessed by'))
#         for fh in feature_histories:
#             feat_hist = (fh.subscription.company.name, fh.subscription.team,
#                          fh.subscription.project.name,
#                          str(fh.subscription.validity_period.lower),
#                          str(fh.subscription.validity_period.upper),
#                          fh.job_id, fh.lon, fh.lat, fh.gem_id,
#                          str(fh.first_accessed_at),
#                          fh.first_accessed_by.user.username)
#             writer.writerow(feat_hist)

#         return response
