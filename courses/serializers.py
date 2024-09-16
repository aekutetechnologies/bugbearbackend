from rest_framework import serializers
from .models import (
    Course,
    Category,
    CourseModule,
    CourseReview,
    CourseOrder,
    CourseProgress,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["name", "description", "category", "price", "image"]


class CourseSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    likes = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_likes(self, obj):
        return obj.likes.count()

    def get_reviews(self, obj):
        return obj.reviews.count()

    def get_modules(self, obj):
        return CourseModuleSerializer(obj.modules, many=True).data


class CourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = "__all__"


class CourseReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseReview
        fields = "__all__"


class CourseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseOrder
        fields = "__all__"


# Added the CourseProgressSerializer
class CourseProgressSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = CourseProgress
        fields = ["course", "progress"]

    def get_progress(self, obj):
        return obj.calculate_progress()
