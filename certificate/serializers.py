from rest_framework import serializers
from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = [
            "id",
            "title",
            "description",
            "certificate_image",
            "created_at",
            "updated_at",
            "valid_until",
            "likes",
            "total_likes",
        ]

    def get_total_likes(self, obj):
        return obj.likes.count()
