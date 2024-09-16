from django.urls import path
from .views import (
    CourseListCreateView,
    CourseDetailView,
    CourseOrderView,
    CategoryListCreateView,
)

urlpatterns = [
    path("category/", CategoryListCreateView.as_view(), name="course-list-create"),
    path("", CourseListCreateView.as_view(), name="course-create"),
    path("<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path("orders/", CourseOrderView.as_view(), name="course-order-list-create"),
    path("orders/<int:pk>/", CourseOrderView.as_view(), name="course-order-detail"),
]
