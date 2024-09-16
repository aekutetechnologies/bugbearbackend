from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import GigSerializer, CategorySerializer
from .models import Gig, Category
from buguser.renderers import UserRenderer
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class GigListCreateView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        gigs = Gig.objects.filter(user=request.user)
        serializer = GigSerializer(gigs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GigDetailView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        gig = Gig.objects.get(id=pk)
        serializer = GigSerializer(gig)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        user = request.user
        request.data["user"] = user.id
        serializer = GigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        gig = Gig.objects.get(id=pk)
        serializer = GigSerializer(gig, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        gig = Gig.objects.get(id=pk)
        gig.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryListCreateView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
