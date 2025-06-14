from django.contrib import admin
from .models import Bundle, Benchmark, Reference, Script, GroupedTag, GroupedTaggedItem
from pathlib import Path
from django import forms
from taggit.admin import TagAdmin


BASE_BUNDLE_DIR = Path("./benchmarks")

class DirectoryChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        choices = [
            (str(p), p.relative_to(BASE_BUNDLE_DIR))
            for p in BASE_BUNDLE_DIR.iterdir()
            if p.is_dir()
        ]
        super().__init__(choices=choices, *args, **kwargs)

class BundleAdminForm(forms.ModelForm):
    directory = DirectoryChoiceField(label="Directory")

    class Meta:
        model = Bundle
        fields = '__all__'



@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    search_fields = ['title', 'authors', 'doi']
    list_display = ['title', 'authors', 'year']

@admin.register(Benchmark)
class BenchmarkAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name']
    filter_horizontal = ['references']

class ScriptInline(admin.TabularInline):
    model = Script
    extra = 1

@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    form = BundleAdminForm
    search_fields = ['key']
    list_display = ['key', 'title', 'directory']
    inlines = [ScriptInline]
    filter_horizontal = ['benchmarks']


@admin.register(GroupedTag)
class GroupedTagAdmin(admin.ModelAdmin):
    list_display  = ("name", "category")
    list_filter   = ("category",)
    search_fields = ("name",)
