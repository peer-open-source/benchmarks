import os
from uuid import uuid4
import time

from django.shortcuts import get_object_or_404, render
from django_tables2 import RequestConfig
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from app.models import Bundle
from django.views.generic import ListView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from app.models import Bundle
from app.filters import BundleFilter
from app.tables import BundleTable
from app.models import Bundle, GroupedTag
from app.models import Bundle, AnalysisJob, GroupedTag
from app.filters import BundleFilter
from app.tables import BundleTable
from django.http import Http404
from django.views import View

# @require_POST
# @csrf_exempt
# def analyze_bundles(request):
#     if request.method == "POST":
#         bundle_ids = request.POST.getlist("bundle_ids")
#         results = []

#         for bundle in Bundle.objects.filter(id__in=bundle_ids).prefetch_related("scripts"):
#             for script in bundle.scripts.all():
#                 try:
#                     test = TestCase(script.path)
#                     output = test.run()
#                     results.append({
#                         "bundle": bundle.key,
#                         "script": os.path.basename(script.path),
#                         "result": output.get("status", "ok")  # or however xara structures it
#                     })
#                 except Exception as e:
#                     results.append({
#                         "bundle": bundle.key,
#                         "script": os.path.basename(script.path),
#                         "result": f"Error: {str(e)}"
#                     })

#         return render(request, "app/analyze_results.html", {"results": results})


# def bundle_analysis_result(request, job_id):
#     job = PENDING_ANALYSIS.get(job_id)
#     if not job or "results" not in job:
#         raise Http404("No such result")
#     return render(request, "app/analyze_results.html", {"results": job["results"]})


# class BundleAnalysisStatusView(View):
#     template_name = "app/analysis_status.html"

#     def get(self, request, job_id):
#         # from xara.runtime import evaluate
#         from xara.test import TestCase
#         job = PENDING_ANALYSIS.get(job_id)
#         if not job:
#             raise Http404("No such analysis")

#         if job["status"] == "pending":
#             job["results"] = []
#             bundles = Bundle.objects.filter(id__in=job["bundle_ids"]).prefetch_related("scripts")

#             for bundle in bundles:
#                 for script in bundle.scripts.all():
#                     try:

#                         result = TestCase(script.path).run()
#                         status = result.get("status", "ok") if isinstance(result, dict) else str(result)
#                     except Exception as e:
#                         status = f"Error: {str(e)}"

#                     job["results"].append({
#                         "bundle": bundle.key,
#                         "script": os.path.basename(script.path),
#                         "result": status,
#                     })

#             job["status"] = "done"
#             return redirect(reverse("bundle_analysis_result", args=[job_id]))

#         elif job["status"] == "done":
#             return redirect(reverse("bundle_analysis_result", args=[job_id]))

#         return render(request, self.template_name, {"job_id": job_id})

def bundle_list(request):
    qs = Bundle.objects.prefetch_related('benchmarks__references').all()
    f = BundleFilter(request.GET, queryset=qs)
    table = BundleTable(f.qs)
    RequestConfig(request, paginate={'per_page': 12}).configure(table)
    return render(request, 'app/bundle_list.html', {'filter': f, 'table': table})


def bundle_detail(request, key):
    bundle = get_object_or_404(Bundle, key=key)
    return render(request, 'app/bundle_detail.html', {
        'bundle': bundle,
        'index_html': bundle.get_index_html(),
    })



class BundleListView(FilterView, ListView):
    model = Bundle
    template_name = "app/bundle_list.html"
    context_object_name = "bundles"
    paginate_by = 9
    filterset_class = BundleFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_obj"] = context.get("page_obj") or context.get("paginator").page(context.get("page").number)
        
        # Organize all tags by category
        from collections import defaultdict
        all_tags = defaultdict(list)
        for tag in GroupedTag.objects.all():
            all_tags[tag.category].append(tag)
        context["all_tags"] = dict(all_tags)
        return context

# class BundleListView(SingleTableMixin, FilterView):
#     model = Bundle
#     table_class = BundleTable
#     template_name = "app/bundle_list.html"
#     filterset_class = BundleFilter
#     paginate_by = 8
