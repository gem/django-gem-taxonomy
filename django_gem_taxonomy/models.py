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

import json
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

class Version(models.Model):
    vers = models.CharField(max_length=16, primary_key=True)
    desc = models.TextField()
    is_default = models.BooleanField(default=False)


class VersRelatedContentManager(models.Manager):
    def get_by_natural_key(self, vers, name):
        return self.get(vers__vers=vers, name=name)


class VersRelatedContent(models.Model):
    vers = models.ForeignKey(Version, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    title = models.TextField()
    content = GenericRelation('Content')

    class Meta:
        unique_together = [['vers', 'name']]

    objects = VersRelatedContentManager()

    def natural_key(self):
        return (self.vers.vers, self.name)


class AttributeManager(models.Manager):
    def get_by_natural_key(self, vers, name):
        return self.get(vers__vers=vers, name=name)

class Attribute(models.Model):
    vers = models.ForeignKey(Version, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    prog = models.IntegerField()
    title = models.TextField()
    content = GenericRelation('Content')

    class Meta:
        unique_together = [['vers', 'name'],
                           ['vers', 'prog']]

    objects = AttributeManager()

    def natural_key(self):
        return (self.vers.vers, self.name)


class AtomsGroupManager(models.Manager):
    def get_by_natural_key(self, vers, attr, name):
        return self.get(vers__vers=vers, attr__name=attr, name=name)


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


    objects = AtomsGroupManager()

    def natural_key(self):
        return (self.vers.vers, self.attr.name, self.name)


# TODO: parameters description atom(param1[,param2[...,paramN]])
# class AtomParam(models.Model):
#     atom = models.ForeignKey(Atom)

# TODO: arguments description atom[:arg1[:arg2[...:argN]]]
# class AtomArg(models.Model):
#     atom = models.ForeignKey(Atom)


class AtomManager(models.Manager):
    def get_by_natural_key(self, vers, name):
        return self.get(vers__vers=vers, name=name)

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

    objects = AtomManager()

    def entry_type(self):
        return json.loads(self.type)

    def natural_key(self):
        return (self.vers.vers, self.name)


class ParamManager(models.Manager):
    def get_by_natural_key(self, vers, atom, name):
        return self.get(vers__vers=vers, atom__name=atom, name=name)


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

    objects = ParamManager()

    def natural_key(self):
        return (self.vers.vers, self.atom.name, self.name)


class Content(models.Model):
    content = CKEditor5Field('Content')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # - object_id: memorize the primary key (ID) of linked object
    object_id = models.PositiveIntegerField()
    # - content_object: virtual field that join 2 previous fields
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['content_type', 'object_id'],
                name='unique_generic_relation'
                )
        ]


    def natural_key(self):
        pass

    # 3. Inform Django that this model MUST be serialized AFTER the target models.
    # If you know the specific apps, you explicitly add them here.
    # Django will read this list and reorder the dump output accordingly.
    natural_key.dependencies = [
        'django_gem_taxonomy.VersRelatedContent',
        'django_gem_taxonomy.Attribute', 'django_gem_taxonomy.AtomsGroup',
        'django_gem_taxonomy.Atom', 'django_gem_taxonomy.Param', ]

