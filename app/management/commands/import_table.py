import csv
import glob
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from app.models import Bundle, GroupedTag, Script


class Command(BaseCommand):
    help = "Import Bundles from a CSV file with columns: key, title, type_tag"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to CSV file")

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            self.stderr.write(f"File not found: {csv_path}")
            return

        with csv_path.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row["key"].strip()
                title = row["title"].strip()
                type_tag_name = row["type_tag"].strip().lower()

                number = key[5:]

                key = f"vsapa-{number}"

                bundle, created = Bundle.objects.get_or_create(
                    key=key,
                    defaults={
                        "title": title,
                        "directory": f"./benchmarks/sap/{number}",
                    }
                )

                if created:
                    self.stdout.write(f"Created bundle: {key}")
                else:
                    self.stdout.write(f"Bundle exists: {key}")

                #
                tag, _ = GroupedTag.objects.get_or_create(
                    name=type_tag_name,
                    defaults={"category": GroupedTag.TagCategory.TYPE}
                )

                bundle.tags.add(tag)

                for path in glob.glob(os.path.join(bundle.directory, "*.s2k")):
                    script, created = Script.objects.get_or_create(bundle=bundle, path=path)
                    print(f"    {script.path} {'created' if created else 'exists'}")
                bundle.save()
