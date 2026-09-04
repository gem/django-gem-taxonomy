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
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
import json

class Version(models.Model):
    vers = models.CharField(max_length=16, primary_key=True)
    desc = models.TextField()
    is_default = models.BooleanField(default=False)

class VersRelatedContent(models.Model):
    vers = models.ForeignKey(Version, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    title = models.TextField()
    content = GenericRelation('Content')


class Attribute(models.Model):
    vers = models.ForeignKey(Version, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    prog = models.IntegerField()
    title = models.TextField()
    content = GenericRelation('Content')

    class Meta:
        unique_together = [['vers', 'name'],
                           ['vers', 'prog']]

class AtomsGroup(models.Model):
    vers = models.ForeignKey(Version, on_delete=models.CASCADE)
    attr = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    prog = models.IntegerField()
    title = models.TextField()
    # mutex identify if it is possible or not dropdown multi-selection
    mutex = models.BooleanField(default=True)
    content = GenericRelation('Content')

    class Meta:
        unique_together = [['vers', 'attr', 'name'],
                           ['vers', 'attr', 'prog']]


# TODO: parameters description atom(param1[,param2[...,paramN]])
# class AtomParam(models.Model):
#     atom = models.ForeignKey(Atom)

# TODO: arguments description atom[:arg1[:arg2[...:argN]]]
# class AtomArg(models.Model):
#     atom = models.ForeignKey(Atom)


class Atom(models.Model):
    vers = models.ForeignKey(Version, on_delete=models.CASCADE)
    attr = models.ForeignKey(Attribute, on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(AtomsGroup, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=32)
    prog = models.IntegerField()
    title = models.TextField()
    desc = models.TextField()
    type = models.TextField()
    args = models.JSONField(blank=True, null=True)
    params = models.JSONField(blank=True, null=True)
    deps = models.ManyToManyField('self', symmetrical=False,
                                  related_name='revdeps')
    deny = models.ManyToManyField('self', symmetrical=False,
                                  related_name='revdeny')
    content = GenericRelation('Content')
    # is_pseudoid = models.BooleanField()

    class Meta:
        unique_together = [['vers', 'name'],
                           ['vers', 'attr', 'group', 'prog']]

    def entry_type(self):
        return json.loads(self.type)


class Param(models.Model):
    vers = models.ForeignKey(Version, on_delete=models.CASCADE)
    atom = models.ForeignKey(Atom, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=32)
    prog = models.IntegerField()
    title = models.TextField()
    desc = models.TextField()
    content = GenericRelation('Content')

    class Meta:
        unique_together = [['vers', 'atom', 'name'],
                           ['vers', 'atom', 'prog']]


class Content(models.Model):
    content = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # - object_id: memorize the primary key (ID) of linked object
    object_id = models.PositiveIntegerField()
    # - content_object: virtual field that join 2 previous fields
    content_object = GenericForeignKey('content_type', 'object_id')
