import django_tables2 as tables
from .models import Bundle

class BundleTable(tables.Table):
    key = tables.Column(linkify=True)
    benchmarks = tables.Column(empty_values=())

    class Meta:
        model = Bundle
        fields = ('key',)

    def render_benchmarks(self, value, record):
        return ", ".join(b.name for b in record.benchmarks.all())
