# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2026 GEM Foundation
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
import re
import shutil
from collections import Counter
from urllib.parse import urlsplit, unquote, quote

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from django_gem_taxonomy.models import Content
from django_gem_taxonomy.glossary_views import clean_folder_name

IMG_EXTS = ('.gif', '.png', '.jpg')

# <img ... src="..."> (group 1: everything before the value,
# group 2: the quote, group 3: the value)
IMG_SRC_RE = re.compile(r'''(<img\b[^>]*?\bsrc\s*=\s*)(["'])(.*?)\2''',
                        re.IGNORECASE | re.DOTALL)


class Command(BaseCommand):
    help = ("For each Content with images served by the same server of the"
            " page, look for the image (by file name) in IMG_PATH, copy it"
            " under MEDIA_ROOT/uploads/glossary/<vers>/ and update the"
            " image src accordingly.")

    def add_arguments(self, parser):
        parser.add_argument('img_path',
                            help='folder where gif, png and jpg images are stored')

        # Optional arguments
        parser.add_argument(
            '-n', '--dry-run',
            help='show what would be done without copying files or saving contents',
            action='store_true', default=False)

    def handle(self, *args, **options):
        img_path = options['img_path']
        dry_run = options['dry_run']

        if not os.path.isdir(img_path):
            raise CommandError(f'Images folder "{img_path}" not found.')

        copied = set()
        missing = Counter()
        n_contents = 0
        n_imgs = 0

        def local_img(src):
            # return the image file name if src is an image served by the
            # same server of the page and not already in MEDIA_URL
            src_split = urlsplit(src)
            if src_split.scheme or src_split.netloc:
                return None
            if src_split.path.startswith(settings.MEDIA_URL):
                return None
            filename = os.path.basename(unquote(src_split.path))
            if not filename.lower().endswith(IMG_EXTS):
                return None
            return filename

        with transaction.atomic():
            for content in Content.objects.all().order_by('id'):
                if not content.content:
                    continue
                obj = content.content_object
                if obj is None:
                    self.stderr.write(
                        f'Content {content.id}: related object not found, skipped.')
                    continue
                vers_folder = clean_folder_name(obj.vers.vers)
                dest_dir = os.path.join(settings.MEDIA_ROOT, 'uploads',
                                        'glossary', vers_folder)

                def replace_src(match):
                    nonlocal n_imgs
                    src = match.group(3)
                    filename = local_img(src)
                    if filename is None:
                        return match.group(0)

                    src_file = os.path.join(img_path, filename)
                    if not os.path.isfile(src_file):
                        missing[filename] += 1
                        return match.group(0)

                    if (vers_folder, filename) not in copied:
                        if not dry_run:
                            os.makedirs(dest_dir, exist_ok=True)
                            shutil.copyfile(src_file,
                                            os.path.join(dest_dir, filename))
                        copied.add((vers_folder, filename))

                    n_imgs += 1
                    new_src = (f'{settings.MEDIA_URL}uploads/glossary/'
                               f'{vers_folder}/{quote(filename)}')
                    return (match.group(1) + match.group(2) + new_src
                            + match.group(2))

                new_content = IMG_SRC_RE.sub(replace_src, content.content)
                if new_content != content.content:
                    n_contents += 1
                    if not dry_run:
                        content.content = new_content
                        content.save(update_fields=['content'])

            if dry_run:
                transaction.set_rollback(True)

        prefix = '[dry-run] ' if dry_run else ''
        self.stdout.write(f'{prefix}Images updated: {n_imgs}')
        self.stdout.write(f'{prefix}Contents updated: {n_contents}')
        self.stdout.write(f'{prefix}Files copied: {len(copied)}')
        if missing:
            self.stderr.write(
                f'{prefix}Images not found in "{img_path}": {len(missing)}')
            for filename, count in sorted(missing.items()):
                self.stderr.write(f'  {filename} ({count} references)')
