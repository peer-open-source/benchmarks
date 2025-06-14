from django.urls import path
import app.views as views

from app.views.analysis import (
    analyze_bundles,
    BundleAnalysisStatusView,
    BundleAnalysisPollView,
    bundle_analysis_result,
)

urlpatterns = [
    # path('', views.bundle_list, name='bundle_list'),
    path('', views.BundleListView.as_view(), name='bundle_list'),

    path('bundle/<str:key>/', views.bundle_detail, name='bundle_detail'),

    path("analyze/", analyze_bundles, name="bundle_analyze"),
    path("analyze/status/<uuid:job_id>/", BundleAnalysisStatusView.as_view(), name="bundle_analysis_status"),
    path("analyze/poll/<uuid:job_id>/", BundleAnalysisPollView.as_view(), name="bundle_analysis_poll"),
    path("analyze/result/<uuid:job_id>/", bundle_analysis_result, name="bundle_analysis_result"),
]
