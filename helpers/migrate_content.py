#!/usr/bin/env python3
import os
import re
import ast
import json
import django
from difflib import SequenceMatcher
# from django.conf import settings

# to dump:
#   ./server/run.sh dumpdata --indent 4 --natural-foreign --natural-primary --format json_gfk django_gem_taxonomy.content django_gem_taxonomy.versrelatedcontent > dump.json_gfk
#
# to restore:
#  ./server/run.sh loaddata dump.json_gfk

CACHE_FILE = '.migrate_content.cache.json'

# Reset code
RESET         = "\033[0m"  # Resets all colors and styles back to terminal default

# Standard colors (darker shades)
RED           = "\033[31m"  # Standard Red
GREEN         = "\033[32m"  # Standard Green
ORANGE        = "\033[33m"  # Standard Yellow/Brown (renders as Orange on some terminals)

# High-intensity colors (brighter shades)
BRIGHT_RED    = "\033[91m"  # Bright Red
BRIGHT_GREEN  = "\033[92m"  # Bright Green
BRIGHT_ORANGE = "\033[93m"  # Bright Yellow (often works well as a bright light Orange)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

django.setup()

from django_gem_taxonomy.models import (Version,
                                        Attribute, AtomsGroup, Atom, Param,
                                        VersRelatedContent, Content)

def delete_content(obj):
    if obj.content.all():
        for content in obj.content.all():
            content.delete()
    

def copy_content(obj_from, obj_to):
    delete_content(obj_to)

    if obj_from.content.all():
        Content.objects.create(content=obj_from.content.all()[0].content,
                               content_object=obj_to, is_draft=True)

def save_cache(cache):
    json_cache = {str(k): v for k, v in cache.items()}
        
    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(json_cache, file, indent=4, ensure_ascii=False)


def load_cache():
    if os.path.exists(CACHE_FILE):
        json2cache = json.load(open(CACHE_FILE))
        cache = {ast.literal_eval(k): v for k,v in json2cache.items()}
    else:
        cache = {}

    return cache
    
        
def main():
    print('Check attributes')
    attrs_from = Attribute.objects.filter(vers__vers='2.0')
    atomsgrps_from = AtomsGroup.objects.filter(vers__vers='2.0')
    atoms_from = Atom.objects.filter(vers__vers='2.0')
    vrconts_from = VersRelatedContent.objects.filter(vers__vers='2.0')

    cache = load_cache()
    
    for vers_id in ['3.3', '4.0']:
        vers = Version.objects.get(vers=vers_id)
        print(f'---=== {vers} ===---')
        print()
        print('------ ATTRIBUTES ===---')
        attrs_to = Attribute.objects.filter(vers=vers)
        for attr_to in attrs_to:
            delete_content(attr_to)
            if (vers.vers, 'attr', attr_to.title) in cache:
                cached_item = cache[(vers.vers, 'attr', attr_to.title)]
                if cached_item[2]:
                    print(f'{ORANGE}SIMILAR (cached){RESET} ratio: {cached_item[1]}')
                    print(f'  [2.0] {cached_item[0]}\n  [{vers.vers}] {attr_to.title}')
                    attr_from = Attribute.objects.get(vers__vers='2.0', title=cached_item[0])
                    copy_content(attr_from, attr_to)
                else:
                    print(f'{RED}SIMILAR NOT ENOUGH (cached){RESET} ratio: {cached_item[1]}')
                    print(f'  [2.0] {cached_item[0]}\n  [{vers.vers}] {attr_to.title}')
                continue
            similar = []
            for attr_from in attrs_from:
                simi_ratio = SequenceMatcher(None, attr_from.title, attr_to.title).ratio()

                if attr_from.title == attr_to.title:
                    print(f'{attr_from.title}: {BRIGHT_GREEN}PERFECT{RESET} match [2.0 -> {vers.vers}]')
                    copy_content(attr_from, attr_to)
                    break
                elif simi_ratio > 0.7:
                    similar.append([attr_from, simi_ratio])
            else:
                if similar:
                    attr_from_pair = sorted(similar, key=lambda x: x[1])[-1]
                    attr_from = attr_from_pair[0]
                    simi_ratio = attr_from_pair[1]
                    print(f'{ORANGE}SIMILAR{RESET} ratio: {simi_ratio}')
                    print(f'  [2.0] {attr_from.title}\n  [{vers.vers}] {attr_to.title}')
                    rep = input('Accept [Y/N]? ')
                    if rep.lower() in ['y', 'yes']:
                        accepted = True
                        copy_content(attr_from, attr_to)
                    else:
                        accepted = False
                        print(f'{attr_to.title}: {RED}NO MATCH{RESET}')
                    pro_cache = {(vers.vers, 'attr', attr_to.title): (attr_from.title, simi_ratio, accepted)}
                    cache.update(pro_cache)
                    save_cache(cache)
                else:
                    print(f'{attr_to.title}: {RED}NO MATCH{RESET}')

        print()
        print('------ ATOMS GROUPS ------')
        atomsgrps_to = AtomsGroup.objects.filter(vers=vers)
        for atomsgrp_to in atomsgrps_to:
            delete_content(atomsgrp_to)
            if (vers.vers, 'atomsgroup', atomsgrp_to.title) in cache:
                cached_item = cache[(vers.vers, 'atomsgroup', atomsgrp_to.title)]
                if cached_item[2]:
                    print(f'{ORANGE}SIMILAR (cached){RESET} ratio: {cached_item[1]}')
                    print(f'  [2.0] {cached_item[0]}\n  [{vers.vers}] {atomsgrp_to.title}')
                    atomsgrp_from = AtomsGroup.objects.get(vers__vers='2.0', title=cached_item[0])
                    copy_content(atomsgrp_from, atomsgrp_to)
                else:
                    print(f'{RED}SIMILAR NOT ENOUGH (cached){RESET} ratio: {cached_item[1]}')
                    print(f'  [2.0] {cached_item[0]}\n  [{vers.vers}] {atomsgrp_to.title}')
                continue

            similar = []
            for atomsgrp_from in atomsgrps_from:
                simi_ratio = SequenceMatcher(None, atomsgrp_from.title, atomsgrp_to.title).ratio()

                if atomsgrp_from.title == atomsgrp_to.title:
                    print(f'{atomsgrp_from.title}: {BRIGHT_GREEN}PERFECT{RESET} match [2.0 -> {vers.vers}]')
                    copy_content(atomsgrp_from, atomsgrp_to)
                    break
                elif simi_ratio > 0.7:
                    similar.append([atomsgrp_from, simi_ratio])
            else:
                if similar:
                    atomsgrp_from_pair = sorted(similar, key=lambda x: x[1])[-1]
                    atomsgrp_from = atomsgrp_from_pair[0]
                    simi_ratio = atomsgrp_from_pair[1]
                    print(f'{ORANGE}SIMILAR{RESET} ratio: {simi_ratio}')
                    print(f'  [2.0] {atomsgrp_from.title}\n  [{vers.vers}] {atomsgrp_to.title}')
                    rep = input('Accept [Y/N]? ')
                    if rep.lower() in ['y', 'yes']:
                        pro_cache = {(vers.vers, 'atomsgroup', atomsgrp_to.title): (atomsgrp_from.title, simi_ratio, True)}
                        cache.update(pro_cache)
                        save_cache(cache)
                        copy_content(atomsgrp_from, atomsgrp_to)
                    else:
                        pro_cache = {(vers.vers, 'atomsgroup', atomsgrp_to.title): (atomsgrp_from.title, simi_ratio, False)}
                        cache.update(pro_cache)
                        save_cache(cache)
                        print(f'{atomsgrp_to.title}: {RED}NO MATCH{RESET}')
                else:
                    print(f'{atomsgrp_to.title}: {RED}NO MATCH{RESET}')

                
        print()
        print('------ ATOMS ------')
        atoms_to = Atom.objects.filter(vers=vers)
        for atom_to in atoms_to:
            delete_content(atom_to)
            if (vers.vers, 'atom', atom_to.name) in cache:
                cached_item = cache[(vers.vers, 'atom', atom_to.name)]
                if cached_item[2]:
                    print(f'{ORANGE}SIMILAR (cached){RESET} ratio: {cached_item[1]}')
                    print(f'  [2.0] {cached_item[0]}\n  [{vers.vers}] {atom_to.name}')
                    atom_from = Atom.objects.get(vers__vers='2.0', name=cached_item[0])
                    copy_content(atom_from, atom_to)
                else:
                    print(f'{RED}SIMILAR NOT ENOUGH (cached){RESET} ratio: {cached_item[1]}')
                    print(f'  [2.0] {cached_item[0]}\n  [{vers.vers}] {atom_to.name}')
                continue

            similar = []
            for atom_from in atoms_from:
                simi_ratio = SequenceMatcher(None, atom_from.title, atom_to.title).ratio()

                if atom_from.name == atom_to.name:
                    print(f'{atom_from.name}, {atom_from.title} {BRIGHT_GREEN}PERFECT{RESET} match [2.0 -> {vers.vers}]')
                    copy_content(atom_from, atom_to)
                    break
                elif simi_ratio > 0.7:
                    similar.append([atom_from, simi_ratio])
            else:
                if similar:
                    atom_from_pair = sorted(similar, key=lambda x: x[1])[-1]
                    atom_from = atom_from_pair[0]
                    simi_ratio = atom_from_pair[1]
                    print(f'{ORANGE}SIMILAR{RESET} ratio: {simi_ratio}')
                    print(f'  [2.0] {atom_from.name}:{atom_from.title}\n  [{vers.vers}] {atom_to.name}:{atom_to.title}')
                    rep = input('Accept [Y/N]? ')
                    if rep.lower() in ['y', 'yes']:
                        pro_cache = {(vers.vers, 'atom', atom_to.name): (atom_from.name, simi_ratio, True)}
                        cache.update(pro_cache)
                        save_cache(cache)
                        copy_content(atom_from, atom_to)
                    else:
                        pro_cache = {(vers.vers, 'atom', atom_to.name): (atom_from.name, simi_ratio, False)}
                        cache.update(pro_cache)
                        save_cache(cache)
                        print(f'{atom_to.name}: {RED}NO MATCH{RESET}')
                else:
                    print(f'{atom_to.name}: {RED}NO MATCH{RESET}')

        print()

        VersRelatedContent.objects.filter(vers=vers).delete()
        for vrcont_from in vrconts_from:
            vrcont_to = VersRelatedContent.objects.create(
                vers=vers, name=vrcont_from.name,
                title=vrcont_from.title,
                slug_title=vrcont_from.slug_title,
            )
            copy_content(vrcont_from, vrcont_to)

    for cont in Content.objects.all():
        no_title = re.sub(r'^<h2>.*?</h2>\n?', '', cont.content, flags=re.DOTALL)
        cont.content = no_title
        cont.save()

if __name__ == '__main__':
    main()
