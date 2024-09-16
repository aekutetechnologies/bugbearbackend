from rest_framework import serializers
from .models import Post, PostCategory, Comment
from buguser.serializers import PostUserSerializer


class PostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCategory
        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):
    # post_likes = PostUserSerializer(many=True)
    post_image_url = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "image",
            "likes",
            "created_at",
            "updated_at",
            "post_image_url",
            "total_comments",
            "comments",
            # "post_likes",
        ]
        read_only_fields = [
            "id",
            "user",
            "likes",
            "created_at",
            "updated_at",
            "post_image_url",
            "total_comments",
            "comments",
            # "post_likes",
        ]

    def create(self, validated_data):
        post = Post.objects.create(user=self.context["request"].user, **validated_data)
        return post

    def get_post_image_url(self, obj):
        if obj.image:
            return "http://127.0.0.1:8000" + str(obj.image.url)
        return None

    def get_total_comments(self, obj):
        return obj.comments.count()

    def get_comments(self, obj):
        comments = obj.comments.all()
        return CommentSerializer(comments, many=True).data


class PostUpdateSerializer(serializers.ModelSerializer):
    """
    Verify the user and save the post.
    """

    class Meta:
        model = Post
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    comment_user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "user",
            "body",
            "date_added",
            "likes",
            "reply",
            "comment_user",
        ]
        read_only_fields = ["id", "date_added", "likes", "comment_user"]

    def get_comment_user(self, obj):
        # Assuming Comment model has a ForeignKey relationship with User
        user = obj.user
        return PostUserSerializer(user).data

    def create(self, validated_data):
        comment = Comment.objects.create(**validated_data)
        return comment


class LikePostSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()

    def validate_post_id(self, value):
        try:
            Post.objects.get(id=value)
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post does not exist.")
        return value
