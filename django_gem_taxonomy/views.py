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

import os
import json
from django.views import View
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

# from django.conf import settings

from .models import Version, Param, Atom, AtomsGroup, Attribute
from .version import __version__
from openquake.gem_taxonomy import GemTaxonomy
from parsimonious.exceptions import ParseError as ParsimParseError
from parsimonious.exceptions import (IncompleteParseError as
                                     ParsimIncompleteParseError)


class TaxtWEB(View):
    def get(self, request):
        template = 'taxtweb.html'
        return render(request, template, {})


class TaxGraph(View):
    def get(self, request):
        template = 'django-gem-taxonomy/taxgraph/taxgraph.html'
        return render(request, template, {})


class StructureAtom(View):
    def get(self, request, vers_id=None, atom=None):
        atom_obj = None
        param_obj = None
        other_vers = None
        template = 'django-gem-taxonomy/structure/atom.html'

        if vers_id is None:
            vers = Version.objects.get(is_default=True)
        else:
            vers = Version.objects.get(vers=vers_id)

        if atom is None:
            atoms = Atom.objects.filter(vers=vers).order_by('name')
            others_objs = Version.objects.all().exclude(vers=vers_id)
            other_vers = [vers for vers in others_objs]
        else:
            atoms = None
            if ':' in atom:
                parts = atom.split(':')
                atom_part = parts[0]
                param_part = parts[1]

                param_obj = Param.objects.get(vers=vers, name=param_part,
                                              atom__name=atom_part)
                atom_obj = param_obj.atom

                others_objs = Param.objects.filter(
                    name=param_part, atom__name=atom_part).exclude(vers=vers)
                other_vers = [param.vers for param in others_objs]
                template = 'django-gem-taxonomy/structure/param.html'
            else:
                atom_obj = Atom.objects.get(vers=vers, name=atom)
                others_objs = Atom.objects.filter(name=atom).exclude(vers=vers)
                other_vers = [atom.vers for atom in others_objs]

        return render(request, template, {'atoms': atoms,
                                          'atom': atom_obj,
                                          'param': param_obj,
                                          'vers': vers.vers,
                                          'other_vers': other_vers
                                          })


class StructureAtomsGroup(View):
    def get(self, request, vers_id=None, atoms_group=None):
        template = 'django-gem-taxonomy/structure/atoms_group.html'
        atoms_group_obj = None
        other_vers = None

        if vers_id is None:
            vers = Version.objects.get(is_default=True)
        else:
            vers = Version.objects.get(vers=vers_id)
        
        if atoms_group is None:
            atoms_groups = AtomsGroup.objects.filter(vers=vers).order_by('name')
            atoms_group = None
            others_objs = Version.objects.all().exclude(vers=vers_id)
            other_vers = [vers for vers in others_objs]
        else:
            atoms_groups = None
            atoms_group_obj = AtomsGroup.objects.get(vers=vers, name=atoms_group)
            others_objs = AtomsGroup.objects.filter(name=atoms_group).exclude(vers=vers)
            other_vers = [atoms_group.vers for atoms_group in others_objs]

        return render(request, template, {'atoms_groups': atoms_groups,
                                          'atoms_group': atoms_group_obj,
                                          'vers': vers.vers,
                                          'other_vers': other_vers
                                          })


class StructureAttribute(View):
    def get(self, request, vers_id=None, attribute=None):
        template = 'django-gem-taxonomy/structure/attribute.html'
        attribute_obj = None
        other_vers = None

        if vers_id is None:
            vers = Version.objects.get(is_default=True)
        else:
            vers = Version.objects.get(vers=vers_id)
        
        if attribute is None:
            attributes = Attribute.objects.filter(vers=vers).order_by('name')
            attribute_obj = None
            others_objs = Version.objects.all().exclude(vers=vers_id)
            other_vers = [vers for vers in others_objs]
        else:
            attributes = None
            attribute_obj = Attribute.objects.get(vers=vers, name=attribute)
            others_objs = Attribute.objects.filter(name=attribute).exclude(vers=vers)
            other_vers = [atoms_group.vers for atoms_group in others_objs]

        return render(request, template, {'attributes': attributes,
                                          'attribute': attribute_obj,
                                          'vers': vers.vers,
                                          'other_vers': other_vers
                                          })


class GEMTaxonomyInfo(APIView):
    def get(self, request):
        if request.method != 'GET':
            return Response({'message': 'Not implemented'}, status=405)

        info = GemTaxonomy.info(fmt='dict')
        return Response({**{'django_gem_taxonomy_version': __version__},
                         **info}, status=200)


class GEMTaxonomyStringValidation(APIView):
    # authentication_classes = [SessionAuthentication]

    def get(self, request, taxonomy_string):
        """
        Retrieve information about submitted taxonomy string
        """
        if request.method != 'GET':
            return Response({'message': 'Not implemented'}, status=405)

        fmt = request.query_params.get('fmt', 'json')
        gt = GemTaxonomy()

        try:
            _, _, report = gt.validate(taxonomy_string)
        except (ValueError, ParsimParseError,
                ParsimIncompleteParseError) as exc:
            return Response({'success': False, 'message': str(exc)},
                            status=400)
        return Response({**{'success': True}, **report}, status=200)


class GEMTaxonomyStringExplanation(APIView):
    # authentication_classes = [SessionAuthentication]

    def get(self, request, taxonomy_string):
        """
        Retrieve information about submitted taxonomy string
        """
        if request.method != 'GET':
            return Response({'message': 'Not implemented'}, status=405)

        fmt = request.query_params.get('fmt', 'json')
        version = request.query_params.get('version', None)

        if version:
            gt = GemTaxonomy(version)
        else:
            gt = GemTaxonomy()

        try:
            fmt, expl, val_reply = gt.explain(taxonomy_string, fmt=fmt)
        except (ValueError, ParsimParseError,
                ParsimIncompleteParseError) as exc:
            return Response({'success': False, 'message': str(exc)},
                            status=400)

        if fmt in [GemTaxonomy.EXPL_OUT_TYPE.SINGLELINE,
                   GemTaxonomy.EXPL_OUT_TYPE.MULTILINE]:
            return Response({**{'success': True},
                             **{'explanation': expl},
                             **val_reply},
                            status=200)
        elif fmt in [GemTaxonomy.EXPL_OUT_TYPE.JSON]:
            return Response({**{'success': True},
                             **{'explanation': json.dumps(expl)},
                             **val_reply},
                            status=200)
        else:
            return Response({
                'success': False,
                'message': 'Unknown explain format %d' % fmt},
                            status=400)
