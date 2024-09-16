from django.urls import path
from .views import JobCreateView, JobDetailView, JobSearchView, JobAppliedCreateView, JobSavedCreateView, JobCategoryView, GetJobStats, ChangeJobStatus, JobListView, JobUnSaveCreateView, ApplicantsListView, JobsAppliedView, JobsSavedView, JobCategoryCountView

urlpatterns = [
    path("", JobCreateView.as_view(), name="create-job"),
    path("list/<str:slug>/", JobListView.as_view(), name="job-list"),
    path("search/", JobSearchView.as_view(), name="search-job"),
    path("<int:pk>/", JobDetailView.as_view(), name="job-detail"),
    path("apply/", JobAppliedCreateView.as_view(), name="apply-job"),
    path("save/", JobSavedCreateView.as_view(), name="save-job"),
    path("unsave/", JobUnSaveCreateView.as_view(), name="unsave-job"),
    path("category/", JobCategoryView.as_view(), name="job-category"),
    path("stats/", GetJobStats.as_view(), name="job-stats"),
    path("status/", ChangeJobStatus.as_view(), name="change-job-status"),
    path("applicants/<int:pk>/", ApplicantsListView.as_view(), name="job-applicants"),
    path("applied/", JobsAppliedView.as_view(), name="jobs-applied"),
    path("saved/", JobsSavedView.as_view(), name="jobs-saved"),
    path("categories/", JobCategoryCountView.as_view(), name="job-category-count"),

]
