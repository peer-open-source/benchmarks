from django.db import models
from pathlib import Path
import yaml
import uuid 

from taggit.managers import TaggableManager

from taggit.models import TagBase, GenericTaggedItemBase
from taggit.managers import TaggableManager


class Reference(models.Model):
    title = models.CharField(max_length=512)
    authors = models.TextField()
    year = models.PositiveIntegerField(null=True, blank=True)
    doi = models.CharField(max_length=128, blank=True, null=True, unique=True)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.authors} ({self.year}): {self.title}"


class Benchmark(models.Model):
    name  = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    references = models.ManyToManyField(Reference, blank=True)

    def __str__(self):
        return self.title



class GroupedTag(TagBase):
    
    class TagCategory(models.TextChoices):
        COLLECTION = 'collection', ('Collection')
        MATERIAL = 'material', ('Material')
        GENERAL = 'general', ('General')
        REGION = 'region', ('Region')
        TYPE = 'type', ('Type')

    category = models.CharField(max_length=20, choices=TagCategory.choices, default=TagCategory.GENERAL)

class GroupedTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(GroupedTag, related_name="tagged_items", on_delete=models.CASCADE)



class Bundle(models.Model):
    key = models.CharField(max_length=128, unique=True)
    title = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    benchmarks = models.ManyToManyField(Benchmark, blank=True)
    directory = models.FilePathField(path="/benchmarks", match=".*", recursive=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    # tags = TaggableManager(blank=True)
    tags = TaggableManager(through=GroupedTaggedItem, blank=True)

    def __str__(self):
        return self.key


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.write_yaml()

    def write_yaml(self):
        path = Path(self.directory) / "bundle.yaml"
        data = {
            "key": self.key,
            "title": self.title,
            "description": self.description,
            "thumbnail_url": self.thumbnail_url,
            "benchmarks": [b.name for b in self.benchmarks.all()],
            "scripts": [
                {"path": s.path, "description": s.description}
                for s in self.scripts.all()
            ],
            "references": [
                r.doi or r.title for b in self.benchmarks.all()
                for r in b.references.all()
            ]
        }
        path.write_text(yaml.dump(data, sort_keys=False))


    def grouped_tags(self):
        from collections import defaultdict
        out = defaultdict(list)
        for tag in self.tags.all():
            out[tag.category].append(tag)
        return dict(out)

    def get_index_html(self):
        import markdown
        index_md = Path(self.directory) / "index.md"
        if not index_md.exists():
            return "<p><em>index.md not found.</em></p>"

        text = index_md.read_text(encoding="utf-8")

        # Strip YAML front matter
        if text.startswith('---'):
            parts = text.split('---', 2)
            if len(parts) == 3:
                text = parts[2]

        return markdown.markdown(text)


class Script(models.Model):
    bundle = models.ForeignKey(Bundle, related_name='scripts', on_delete=models.CASCADE)
    path = models.FilePathField(path="benchmarks/", recursive=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.path


class Evaluation(models.Model):
    bundle = models.ForeignKey(Bundle, related_name='evaluations', on_delete=models.CASCADE)
    script = models.ForeignKey(Script, related_name='evaluations', on_delete=models.CASCADE)
    result = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluation of {self.bundle.key} using {self.script.path} at {self.timestamp}"


from concurrent.futures import ThreadPoolExecutor, as_completed
from xara.test import TestCase
import os

class AnalysisJob(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("done", "Done"),
        ("failed", "Failed"),
    ]

    job_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    bundles = models.ManyToManyField("Bundle")
    results = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Analysis {self.job_id} ({self.status})"


    # def run_analysis(self):
    #     self.status = "running"
    #     self.save()

    #     collected = []

    #     def analyze_script(bundle_key, script_path):
    #         try:
    #             result = TestCase(script_path).run()
    #             status = result.get("status", "ok") if isinstance(result, dict) else str(result)
    #         except Exception as e:
    #             status = f"Error: {str(e)}"
    #         return {
    #             "bundle": bundle_key,
    #             "script": os.path.basename(script_path),
    #             "result": status,
    #         }

    #     try:
    #         tasks = []
    #         with ThreadPoolExecutor(max_workers=4) as executor:
    #             for bundle in self.bundles.prefetch_related("scripts"):
    #                 for script in bundle.scripts.all():
    #                     tasks.append(executor.submit(analyze_script, bundle.key, script.path))

    #             for future in as_completed(tasks):
    #                 collected.append(future.result())
    #                 self.results = collected
    #                 self.save()

    #         self.status = "done"
    #         self.results = collected

    #     except Exception as e:
    #         self.status = "failed"
    #         self.results = [{"error": str(e)}]

    #     self.save()

    def run_analysis(self):
        from xara.test import TestCase
        import os

        self.status = "running"
        self.save()

        collected = []
        try:
            for bundle in self.bundles.prefetch_related("scripts"):
                for script in bundle.scripts.all():
                    if not script.path.endswith(".tcl"):
                        continue
                    try:
                        result = TestCase(script.path).run()
                        status = result.get("status", "ok") if isinstance(result, dict) else str(result)
                    except Exception as e:
                        status = f"Error: {str(e)}"
                    
                    collected.append({
                        "bundle": bundle.key,
                        "script": os.path.basename(script.path),
                        "result": status
                    })
                    self.results = collected
                    self.save()
            self.status = "done"
            self.results = collected
        except Exception as e:
            self.status = "failed"
            self.results = [{"error": str(e)}]

        self.save()
