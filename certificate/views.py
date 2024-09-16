from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import CertificateSerializer
from .models import Certificate
from buguser.renderers import UserRenderer
from rest_framework.permissions import IsAuthenticated


class CertificateListCreateView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        certificates = Certificate.objects.filter(user=user)
        serializer = CertificateSerializer(certificates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        user = request.user
        request.data["user"] = user.id
        serializer = CertificateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
