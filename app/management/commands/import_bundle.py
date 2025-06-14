import os
import yaml
import glob
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from app.models import Bundle, Script, GroupedTag


class Command(BaseCommand):
    help = 'Import bundle metadata from index.md in a bundle directory'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Path to the bundle directory')

    def handle(self, *args, **options):
        bundle_path = Path(options['path']).resolve()
        index_md = bundle_path / 'index.md'

        if not index_md.exists():
            raise CommandError(f"index.md not found in {bundle_path}")

        key = bundle_path.name

        with open(index_md, 'r') as f:
            lines = f.readlines()

        # Parse YAML front matter
        if not lines[0].strip() == '---':
            raise CommandError("Missing starting YAML front matter block in index.md")

        try:
            end_idx = lines[1:].index('---\n') + 1
        except ValueError:
            raise CommandError("Missing closing YAML front matter block in index.md")

        yaml_block = ''.join(lines[1:end_idx])
        metadata = yaml.safe_load(yaml_block)

        title = metadata.get('title', '')
        description = metadata.get('description', '')
        thumbnail = metadata.get('thumbnail')

        thumbnail_url = ''
        if thumbnail:
            # Move thumbnail to bundle-local img directory
            original_thumb = Path(".")/Path(thumbnail.strip())
            if not original_thumb.is_absolute():
                original_thumb = (original_thumb).resolve()

            dest_dir = bundle_path / 'img'
            dest_path = dest_dir / original_thumb.name

            if not original_thumb.exists() and not dest_path.exists():
                raise CommandError(f"Thumbnail file not found: {original_thumb}")

            if not dest_path.exists():
                dest_dir.mkdir(parents=True, exist_ok=True)

                shutil.copyfile(original_thumb, dest_path)
            thumbnail_url = str(dest_path.relative_to(bundle_path.parent))

        bundle, created = Bundle.objects.get_or_create(
            key=key,
            defaults={
                'title': title,
                'description': description,
                'directory': str(bundle_path),
                'thumbnail_url': thumbnail_url,
            }
        )

        if not created:
            self.stdout.write(self.style.WARNING(f"Bundle '{key}' already exists."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Imported bundle: {bundle.key}"))

        tag_name = bundle.key[:5]
        tag, created = GroupedTag.objects.get_or_create(
            name=tag_name,
            defaults={"category": GroupedTag.TagCategory.TYPE},
        )
        bundle.tags.add(tag)


        #
        #
        #
        for path in glob.glob(os.path.join(bundle.directory, "test*.tcl")):
            script, created = Script.objects.get_or_create(bundle=bundle, path=path)
            print(f"    {script.path} {'created' if created else 'exists'}")
