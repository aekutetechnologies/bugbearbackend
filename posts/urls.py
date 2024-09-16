from django.urls import path
from .views import (
    PostListCreateView,
    PostDetailView,
    CategoryListCreateView,
    LikePostView,
    CommentListView,
    CommentLikeView,
    CommentUpdateView,
)

urlpatterns = [
    path("", PostListCreateView.as_view(), name="post-list-create"),
    path("<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("<int:post_id>/like/", LikePostView.as_view(), name="post-like"),
    path("comments/<int:post_id>/", CommentListView.as_view(), name="comment-list"),
    path(
        "comments/<int:comment_id>/", CommentUpdateView.as_view(), name="comment-update"
    ),
    path("like/<int:comment_id>/", CommentLikeView.as_view(), name="comment-like"),
]
