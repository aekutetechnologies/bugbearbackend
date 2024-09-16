from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import (
    PostSerializer,
    PostCategorySerializer,
    CommentSerializer,
)
from .models import Post, PostCategory, Comment
from buguser.renderers import UserRenderer
from django.core.paginator import Paginator
from rest_framework.exceptions import PermissionDenied, NotFound

# Create your views here.


class PostListCreateView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve all posts of the logged-in user",
        responses={200: PostSerializer(many=True)},
    )
    def get(self, request, format=None):
        posts = Post.objects.filter(user=request.user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a new post",
        request_body=PostSerializer,
        responses={201: PostSerializer},
    )
    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this post.")
        return post

    @swagger_auto_schema(
        operation_summary="Retrieve a specific post by ID",
        responses={200: PostSerializer, 404: "Not Found"},
    )
    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Update a specific post",
        request_body=PostSerializer,
        responses={200: PostSerializer, 400: "Bad Request", 403: "Permission Denied"},
    )
    def put(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete a specific post by ID",
        responses={204: "No Content", 404: "Not Found"},
    )
    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryListCreateView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve all post categories",
        responses={200: PostCategorySerializer(many=True)},
    )
    def get(self, request, format=None):
        categories = PostCategory.objects.all()
        serializer = PostCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a new post category",
        request_body=PostCategorySerializer,
        responses={201: PostCategorySerializer, 400: "Bad Request"},
    )
    def post(self, request, format=None):
        serializer = PostCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfilePostView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve posts for the logged-in user profile",
        responses={200: PostSerializer(many=True)},
    )
    def get(self, request, format=None):
        posts = Post.objects.filter(user=request.user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a post for the logged-in user",
        request_body=PostSerializer,
        responses={201: PostSerializer, 400: "Bad Request"},
    )
    def post(self, request, format=None):
        user = request.user
        request.data["user"] = user.id
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikePostView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Like or unlike a post",
        responses={200: "Post liked/unliked", 404: "Not Found"},
    )
    def post(self, request, post_id, format=None):
        try:
            post = get_object_or_404(Post, id=post_id)
            user = request.user
            if user in post.likes.all():
                post.likes.remove(user)
                message = "Post unliked."
            else:
                post.likes.add(user)
                message = "Post liked."

            post.save()
            return Response(
                {"message": message, "total_likes": post.get_total_likes()},
                status=status.HTTP_200_OK,
            )
        except NotFound:
            return Response(
                {"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )


class CommentListView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve comments for a specific post",
        responses={200: CommentSerializer(many=True), 404: "Not Found"},
    )
    def get(self, request, post_id, format=None):
        comments = Comment.objects.filter(post=post_id).order_by("-date_added")
        paginator = Paginator(comments, 5)  # Show 5 comments per page

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        serializer = CommentSerializer(page_obj, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a comment for a specific post",
        request_body=CommentSerializer,
        responses={201: CommentSerializer, 400: "Bad Request", 404: "Not Found"},
    )
    def post(self, request, post_id, format=None):
        try:
            post = get_object_or_404(Post, id=post_id)
            request.data["post"] = post_id
            request.data["user"] = request.user.id
            serializer = CommentSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except NotFound:
            return Response(
                {"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )


class CommentUpdateView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update a specific comment",
        request_body=CommentSerializer,
        responses={200: CommentSerializer, 404: "Not Found"},
    )
    def put(self, request, comment_id, format=None):
        comment = get_object_or_404(Comment, id=comment_id)
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentLikeView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Like or unlike a comment",
        responses={200: "Comment liked/unliked", 404: "Not Found"},
    )
    def post(self, request, comment_id, format=None):
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user

        if user in comment.likes.all():
            comment.likes.remove(user)
            message = "Comment unliked."
        else:
            comment.likes.add(user)
            message = "Comment liked."

        comment.save()
        return Response({"message": message}, status=status.HTTP_200_OK)
