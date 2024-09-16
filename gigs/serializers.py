from rest_framework import serializers
from .models import Gig, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class GigSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)

    class Meta:
        model = Gig
        fields = "__all__"
