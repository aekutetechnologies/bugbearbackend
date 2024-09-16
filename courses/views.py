from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import (
    CourseSerializer,
    CourseOrderSerializer,
    CategorySerializer,
    CourseCreateSerializer,
)
from .models import Course, Category, CourseOrder
from buguser.renderers import UserRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


class CourseListCreateView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = CourseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CourseDetailView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        course = get_object_or_404(Course, pk=pk)
        if course.user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this course.")
        return course

    def get(self, request, pk, format=None):
        course = Course.objects.get(id=pk)
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        course = self.get_object(pk)
        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseOrderView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        orders = CourseOrder.objects.filter(user=request.user)
        serializer = CourseOrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        user = request.user
        request.data["user"] = user.id
        serializer = CourseOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk, format=None):
        try:
            request.data["user"] = request.user.id
            order = CourseOrder.objects.get(id=pk, user=request.user)
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CourseOrder.DoesNotExist:
            return Response(
                {"message": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, pk, format=None):
        order = CourseOrder.objects.get(id=pk)
        serializer = CourseOrderSerializer(order, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryListCreateView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCourseListView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        courses = Course.objects.filter(courseorder__user=user)
        serializer = CourseSerializer(courses, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        user = request.user
        request.data["user"] = user.id
        serializer = CourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        course = Course.objects.get(id=pk)
        serializer = CourseSerializer(course, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
