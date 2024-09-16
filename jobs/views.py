from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache
from django.utils import timezone
from .models import BugJob, JobsApplied, JobSaved, BugJobCategory
from .serializers import JobSerializer, JobAppliedSerializer, JobSavedSerializer, JobCategorySerializer
import json
from datetime import datetime, date
from django.utils import timezone
from buguser.models import BugUserDetail
from django.conf import settings
from django.db.models import Q
from django.forms.models import model_to_dict


from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.pagination import PageNumberPagination



from datetime import datetime
from django.utils import timezone
from django.core.cache import cache  # Import the Django cache framework

class JobCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=JobSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                "BugJob Created Successfully", JobSerializer
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                "Invalid input",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def post(self, request, format=None):
        try:
            user = request.user
            serializer = JobSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Create the job instance, passing the user as the company
            job = serializer.save(company=user)

            company_name = job.company.organization.current_company_name
            company_logo = settings.WEB_URL + str(job.company.organization.company_logo.url)

            # Prepare the job data
            job_data = {
                "id": job.id,
                "title": job.title.lower(),
                "job_created": job.job_posted.isoformat(),
                "job_expiry": job.job_expiry.isoformat(),
                "salary_min": str(job.salary_min),
                "salary_max": str(job.salary_max),
                "job_type": job.job_type,
                "featured": job.featured,
                "company_name": company_name,
                "company_logo": company_logo,
                "description": job.responsibilities.lower()
            }

            # Convert job.job_expiry to datetime and make it timezone aware
            job_expiry_datetime = datetime.combine(job.job_expiry, datetime.min.time())
            job_expiry_aware = timezone.make_aware(job_expiry_datetime, timezone.get_current_timezone())

            # Calculate the expiry time in seconds
            current_time = timezone.now()
            expiry_seconds = int((job_expiry_aware - current_time).total_seconds())

            if expiry_seconds > 0:
                redis_client = cache.client.get_client()

                # Store job in Redis (Django's cache framework) with an expiry time
                job_key = f"job:{job.id}"
                redis_client.set(job_key, json.dumps(job_data), ex=expiry_seconds)

                # Add the job title to a Redis set for quick searching
                redis_client.sadd("job_titles", job.title.lower())

            return Response(
                {"msg": "BugJob Created Successfully", "job": job_data},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            print(e)
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    


class JobPagination(PageNumberPagination):
    page_size = 10  # Default number of items per page
    page_query_param = "page"
    page_size_query_param = "page_size"
    max_page_size = 100


class JobSearchView(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Title to search"
                ),
                "page": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Page number", default=1
                ),
                "page_size": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Number of items per page",
                    default=10,
                ),
                "category": openapi.Schema(
                    type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description="List of categories to filter"
                ),
                "salaryRange": openapi.Schema(
                    type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description="List of salary ranges"
                ),
                "experienceLevel": openapi.Schema(
                    type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description="List of experience levels"
                ),
                "jobType": openapi.Schema(
                    type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description="List of job types"
                ),
            },
            required=["page", "page_size"],
        ),
        responses={
            200: openapi.Response(
                "List of jobs",
                openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "title": openapi.Schema(type=openapi.TYPE_STRING),
                            "job_created": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "job_expiry": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "salary_min": openapi.Schema(
                                type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT
                            ),
                            "salary_max": openapi.Schema(
                                type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT
                            ),
                            "job_type": openapi.Schema(type=openapi.TYPE_STRING),
                            "featured": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        },
                    ),
                ),
            )
        },
    )
    def post(self, request, format=None):
        # Extracting filter parameters from the request
        search_query = request.data.get("title", "").lower()
        categories = request.data.get("category", [])
        salary_ranges = request.data.get("salaryRange", [])
        experience_levels = request.data.get("experienceLevel", [])
        job_types = request.data.get("jobType", [])

        # Get pagination parameters
        page = request.data.get("page", 1)
        page_size = request.data.get("page_size", 10)

        # Fetch jobs from Redis or database (assuming Redis is used)
        redis_client = cache.client.get_client()
        job_keys = redis_client.keys("job:*")

        # Use a pipeline to batch Redis calls
        pipeline = redis_client.pipeline()
        for job_key in job_keys:
            pipeline.get(job_key)
        job_data_list = pipeline.execute()

        # Initialize matching jobs
        matching_jobs = []

        # Filter through the jobs
        for job_data in job_data_list:
            job_data = json.loads(job_data.decode("utf-8"))
            job_title = job_data.get("title", "").lower()
            job_category = job_data.get("category", "").lower()
            job_salary_min = float(job_data.get("salary_min", 0))
            job_salary_max = float(job_data.get("salary_max", 0))
            job_experience = float(job_data.get("experience", 0))
            job_type_data = job_data.get("job_type", "").lower()
            job_company_name = job_data.get("created_by", {}).get("company_name", "").lower()
            job_company_logo = job_data.get("created_by", {}).get("company_logo", "").lower()
            job_description = job_data.get("description", "").lower()

            # Salary filtering logic
            valid_salary = False
            for salary_range in salary_ranges:
                try:
                    min_salary, max_salary = map(float, salary_range.split("-"))
                    if min_salary <= job_salary_min <= max_salary:
                        valid_salary = True
                        break
                except ValueError:
                    valid_salary = False  # Invalid salary range format

            # Check filters
            if (
                (not search_query or search_query in job_title)
                and (not categories or job_category in [cat.lower() for cat in categories])
                and (valid_salary or not salary_ranges)  # If no salary range provided, skip filtering
                and (not experience_levels or any(exp_level.lower() in job_data.get("experience", "").lower() for exp_level in experience_levels))
                and (not job_types or job_type_data in [jt.lower() for jt in job_types])
            ):
                matching_jobs.append(job_data)

        # Sort jobs by job_created
        matching_jobs.sort(key=lambda x: x.get("job_created"), reverse=True)

        # Apply pagination
        paginator = JobPagination()
        paginator.page_size = page_size
        paginated_jobs = paginator.paginate_queryset(matching_jobs, request)

        # Return the paginated response
        return paginator.get_paginated_response(paginated_jobs)




class JobDetailView(APIView):
    # Set default permission classes for all methods
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Override this method to set custom permissions for each HTTP method.
        """
        if self.request.method == "GET":
            # Allow anyone to access the GET method
            return [AllowAny()]
        # Default to IsAuthenticated for all other methods
        return [permission() for permission in self.permission_classes]

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response("Job details", JobSerializer),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                "Job not found",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        }
    )

    def get(self, request, pk, format=None):

        try:
            job = BugJob.objects.get(pk=pk)
        except BugJob.DoesNotExist:
            return Response(
                {"error": "BugJob not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        # check whether Job is applied or not
        job_applied = JobsApplied.objects.filter(job__id=pk, user=request.user.id).exists()

        # check whether Job is saved or not
        job_saved = JobSaved.objects.filter(job=job, user=request.user.id).exists()

        serializer = model_to_dict(job)
        serializer["category"] = job.category.name.title() if job.category else ""
        serializer["applied"] = job_applied
        serializer["saved"] = job_saved
        serializer["is_approved"] = JobsApplied.objects.filter(job=job, user=request.user).first().is_approved if job_applied else False

        # Calculate the expiry time in seconds
        current_time = timezone.now()

        # Convert job_expiry to datetime if it's a date
        if isinstance(job.job_expiry, date) and not isinstance(job.job_expiry, datetime):
            job_expiry_datetime = datetime.combine(job.job_expiry, datetime.min.time(), tzinfo=current_time.tzinfo)
        else:
            job_expiry_datetime = job.job_expiry

        expiry_seconds = int((job_expiry_datetime - current_time).total_seconds())

        job_data = {
                "id": job.id,
                "title": job.title.lower(),
                "job_created": job.job_posted.isoformat(),
                "job_expiry": job.job_expiry.isoformat(),
                "salary_min": str(job.salary_min),
                "salary_max": str(job.salary_max),
                "job_type": job.job_type,
                "featured": job.featured,
                "category": job.category.name.lower() if job.category else "",
            }

        if expiry_seconds > 0:
            # Save in Redis with the new expiry time
            cache.set(
                f"job:{job.id}", job_data, timeout=expiry_seconds
            )

        return Response(serializer, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        request_body=JobSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response(
                "Job Updated Successfully", JobSerializer
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                "Job not found",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                "Invalid input",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def put(self, request, pk, format=None):
        try:
            job = BugJob.objects.get(pk=pk)
        except BugJob.DoesNotExist:
            return Response(
                {"error": "BugJob not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        if 'is_active' in request.data:
            job.is_active = request.data.get('is_active')
            job.save()
        else:
            serializer = JobSerializer(job, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        # Calculate the expiry time in seconds
        current_time = timezone.now()
        expiry_seconds = int((job.job_expiry - current_time).total_seconds())

        if expiry_seconds > 0:
            # Update the job data in Redis
            cache.set(
                f"job:{job.id}", json.dumps(serializer.data), timeout=expiry_seconds
            )

        return Response(
            {"msg": "BugJob Updated Successfully"}, status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response("Job Deleted Successfully"),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                "Job not found",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        }
    )
    def delete(self, request, pk, format=None):
        try:
            job = BugJob.objects.get(pk=pk)
        except BugJob.DoesNotExist:
            return Response(
                {"error": "BugJob not found"}, status=status.HTTP_404_NOT_FOUND
            )

        job.delete()

        # Remove job from Redis
        cache.delete(f"job:{pk}")

        return Response(
            {"msg": "BugJob Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class JobAppliedCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "job_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the job applied to"
                )
            },
            required=["job_id"],
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                "Job Applied Successfully", openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                "Invalid input",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def post(self, request, format=None):
        job_id = request.data.get("job_id")

        try:
            job = BugJob.objects.get(pk=job_id)
        except BugJob.DoesNotExist:
            return Response(
                {"error": "BugJob not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Create a new job application
        job_application = JobsApplied(job=job, user=request.user)
        job_application.save()

        return Response(
            {"msg": "Job Applied Successfully"}, status=status.HTTP_201_CREATED
        )
    
    def put(self, request, format=None):
        job_id = int(request.data.get("job_id"))
        user_id = request.data.get("user_id")
        is_approved = request.data.get("is_approved")
        job_applied = JobsApplied.objects.get(user=user_id, job=job_id)
        job_applied.is_approved = is_approved
        job_applied.save()
        return Response(
            {"msg": "Job Approved Successfully"}, status=status.HTTP_200_OK)

    
    def get(self, request, format=None):
        job_applied = JobsApplied.objects.filter(user=request.user)
        serializer = JobAppliedSerializer(job_applied, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class JobSavedCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "job_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the job saved"
                )
            },
            required=["job_id"],
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                "Job Saved Successfully", openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                "Invalid input",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def post(self, request, format=None):
        job_id = request.data.get("job_id")

        try:
            job = BugJob.objects.get(pk=job_id)
        except BugJob.DoesNotExist:
            return Response(
                {"error": "BugJob not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Create a new job saved record
        job_saved = JobSaved(job=job, user=request.user)
        job_saved.save()

        return Response(
            {"msg": "Job Saved Successfully"}, status=status.HTTP_201_CREATED
        )
    
    def get(self, request, format=None):
        job_saved = JobSaved.objects.filter(user=request.user)
        serializer = JobSavedSerializer(job_saved, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class JobUnSaveCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "job_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the job to unsave"
                )
            },
            required=["job_id"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                "Job Unsaved Successfully", openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                "Invalid input",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def post(self, request, format=None):
        job_id = request.data.get("job_id")

        try:
            job = BugJob.objects.get(pk=job_id)
        except BugJob.DoesNotExist:
            return Response(
                {"error": "BugJob not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Delete the job saved record
        JobSaved.objects.filter(job=job, user=request.user).delete()

        return Response(
            {"msg": "Job Unsaved Successfully"}, status=status.HTTP_200_OK)


class JobCategoryView(APIView):

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                "List of job categories",
                openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "name": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            )
        },
    )
    def get(self, request, format=None):
        job_categories = BugJobCategory.objects.all()
        serializer = JobCategorySerializer(job_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ChangeJobStatus(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "job_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the job"
                ),
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING, description="New status of the job"
                ),
            },
            required=["job_id", "status"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                "Job status updated successfully", openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                "Invalid input",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def post(self, request, format=None):
        job_id = request.data.get("job_id")
        status = request.data.get("status")

        try:
            job = BugJob.objects.get(pk=job_id)
        except BugJob.DoesNotExist:
            return Response(
                {"error": "BugJob not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if status not in ["active", "inactive"]:
            return Response(
                {"error": "Invalid status. Must be 'active' or 'inactive'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        job.is_active = status == "active"
        job.save()

        # find the job from redis and update the is_active
        job_key = f"job:{job_id}"
        job_data = cache.get(job_key)
        if job_data:
            job_data = json.loads(job_data)
            job_data["is_active"] = job.is_active
            cache.set(job_key, json.dumps(job_data))

        return Response(
            {"msg": f"Job status updated to {status}"},
            status=status.HTTP_200_OK
        )
    

class GetJobStats(APIView):

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                "Job statistics",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total_jobs": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "active_jobs": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "inactive_jobs": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            )
        },
    )
    def get(self, request, format=None):
        user = request.user
        total_jobs = BugJob.objects.filter(company=user).count()
        active_jobs = BugJob.objects.filter(company=user, is_active=True).count()
        inactive_jobs = BugJob.objects.filter(company=user, is_active=False).count()

        return Response(
            {
                "total_jobs": total_jobs,
                "active_jobs": active_jobs,
                "inactive_jobs": inactive_jobs,
            },
            status=status.HTTP_200_OK,
        )
    

class JobListView(APIView):

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                "List of jobs",
                openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "title": openapi.Schema(type=openapi.TYPE_STRING),
                            "job_created": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "job_expiry": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                            ),
                            "salary_min": openapi.Schema(
                                type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT
                            ),
                            "salary_max": openapi.Schema(
                                type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT
                            ),
                            "job_type": openapi.Schema(type=openapi.TYPE_STRING),
                            "featured": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        },
                    ),
                ),
            )
        },
    )
    def get(self, request, slug, format=None):
        """
        Retrieve a list of jobs based on the slug filter.
        Slug can be 'all', 'open', or 'closed'.
        """
        try:
            # Base queryset
            jobs = BugJob.objects.all()

            # Apply filters based on slug
            if slug == "open":
                jobs = jobs.filter(is_active=True)
            elif slug == "closed":
                jobs = jobs.filter(is_active=False)
            elif slug != "all":
                return Response(
                    {"detail": "Invalid slug parameter."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Optional: Implement additional filters from query parameters
            # Example: Filter by category, location, etc.
            category = request.query_params.get('category', None)
            if category:
                jobs = jobs.filter(category__iexact=category.lower())

            location = request.query_params.get('location', None)
            if location:
                jobs = jobs.filter(location__iexact=location.lower())

            response_dict = []
            for job in jobs:
                job_data = {
                    "id": job.id,
                    "title": job.title.lower(),
                    "location": job.location,
                    "job_created": job.job_posted.isoformat(),
                    "job_expiry": job.job_expiry.isoformat(),
                    "salary_min": str(job.salary_min),
                    "salary_max": str(job.salary_max),
                    "job_type": job.job_type,
                    "featured": job.featured,
                    "is_active": job.is_active,
                }
                response_dict.append(job_data)
            return Response(response_dict, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            # Log the exception as needed
            return Response(
                {"detail": "An error occurred while fetching jobs."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    # def get(self, request, slug, format=None):
    #     # Fetch jobs from Redis or database (assuming Redis is used)
    #     redis_client = cache.client.get_client()
    #     job_keys = redis_client.keys("job:*")

    #     # Use a pipeline to batch Redis calls
    #     pipeline = redis_client.pipeline()
    #     for job_key in job_keys:
    #         pipeline.get(job_key)
    #     job_data_list = pipeline.execute()

    #     # Initialize matching jobs
    #     matching_jobs = []

    #     # Filter through the jobs
    #     for job_data in job_data_list:
    #         print(job_data)
    #         job_data = json.loads(job_data.decode("utf-8"))
    #         job_title = job_data.get("title", "").lower()
    #         job_category = job_data.get("category", "").lower()
    #         job_salary_min = float(job_data.get("salary_min", 0))
    #         job_salary_max = float(job_data.get("salary_max", 0))
    #         job_experience = float(job_data.get("experience", 0))
    #         job_type_data = job_data.get("job_type", "").lower()
    #         job_location = job_data.get("location", "").lower()

    #         # Check filters
    #         if slug == "all":
    #             matching_jobs.append(job_data)
    #         elif slug == "open":
    #             if job_data.get("is_active", True):
    #                 matching_jobs.append(job_data)
    #         elif slug == "closed":
    #             if not job_data.get("is_active", False):
    #                 matching_jobs.append(job_data)

    #     return Response(matching_jobs, status=status.HTTP_200_OK)
                

        # Sort jobs by job_created


class ApplicantsListView(APIView):
    permission_classes = [IsAuthenticated]

    from django.db.models import Q

    def post(self, request, pk, format=None):
        # Get the search term from the query params
        search_term = request.data.get('searchTerm', "")

        # Filter applicants by job id and search term using Q objects
        job_applied = JobsApplied.objects.filter(
            Q(job__id=pk) & 
            Q(user__buguserdetail__first_name__icontains=search_term)
        )

        response_dict = []

        for job in job_applied:
            # Fetch BugUserDetail for the user
            try:
                bug_user_detail = BugUserDetail.objects.get(user=job.user)
            except BugUserDetail.DoesNotExist:
                bug_user_detail = None

            # Construct the response for each applicant
            job_data = {
                "id": job.id,
                "job_id": job.job.id,
                "job_title": job.job.title,
                "applied_date": job.applied_date,
                "is_approved": job.is_approved,
                "user": {
                    "id": job.user.id,
                    "email": job.user.email,
                    "first_name": bug_user_detail.first_name if bug_user_detail else None,
                    "last_name": bug_user_detail.last_name if bug_user_detail else None,
                    "position": bug_user_detail.position if bug_user_detail else None,
                    "dob": bug_user_detail.dob if bug_user_detail else None,
                    "country": bug_user_detail.country if bug_user_detail else None,
                    "city": bug_user_detail.city if bug_user_detail else None,
                    "address": bug_user_detail.address if bug_user_detail else None,
                    "phone": bug_user_detail.phone if bug_user_detail else None,
                    "profile_pic": settings.WEB_URL + str(bug_user_detail.profile_pic.url) if bug_user_detail and bug_user_detail.profile_pic else None,
                    "gender": bug_user_detail.gender if bug_user_detail else None,
                    "about_me": bug_user_detail.about_me if bug_user_detail else None,
                }
            }
            response_dict.append(job_data)

        return Response(response_dict, status=status.HTTP_200_OK)


class JobsAppliedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        # Filter jobs applied by user and search term using Q objects
        job_applied = JobsApplied.objects.filter(
            Q(user=request.user)
        )

        response_dict = []

        for job in job_applied:
            # Construct the response for each job applied
            job_data = {
                "id": job.job.id,
                "job_title": job.job.title,
                "job_created": job.job.job_posted,
                "job_expiry": job.job.job_expiry,
                "salary_min": job.job.salary_min,
                "salary_max": job.job.salary_max,
                "job_type": job.job.job_type,
                "featured": job.job.featured,
                "category": job.job.category.name if job.job.category else "",
                "location": job.job.location,
                "is_active": job.job.is_active,
                "description": job.job.responsibilities,
                "applied_date": job.applied_date,
                "is_approved": job.is_approved,
                "company_name": job.job.company.organization.current_company_name,
                "company_logo": settings.WEB_URL + str(job.job.company.organization.company_logo.url),
            }
            response_dict.append(job_data)

        return Response(response_dict, status=status.HTTP_200_OK)
    

class JobsSavedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        # Filter jobs saved by user
        job_saved = JobSaved.objects.filter(
            Q(user=request.user)
        )

        response_dict = []

        for job in job_saved:
            # Construct the response for each job saved
            job_data = {
                "id": job.job.id,
                "job_title": job.job.title,
                "job_created": job.job.job_posted,
                "job_expiry": job.job.job_expiry,
                "salary_min": job.job.salary_min,
                "salary_max": job.job.salary_max,
                "job_type": job.job.job_type,
                "featured": job.job.featured,
                "category": job.job.category.name if job.job.category else "",
                "location": job.job.location,
                "is_active": job.job.is_active,
                "description": job.job.responsibilities,
                "company_name": job.job.company.organization.current_company_name,
                "company_logo": settings.WEB_URL + str(job.job.company.organization.company_logo.url),
            }
            response_dict.append(job_data)

        return Response(response_dict, status=status.HTTP_200_OK)
    


class JobCategoryCountView(APIView):

    def get(self, request, format=None):
        # Fetch all job categories
        job_categories = BugJobCategory.objects.all()

        response_dict = []

        for category in job_categories:
            # Count the number of jobs in each category
            job_count = BugJob.objects.filter(category=category).count()

            # Construct the response for each category
            category_data = {
                "id": category.id,
                "name": category.name,
                "job_count": job_count,
            }
            response_dict.append(category_data)

        return Response(response_dict, status=status.HTTP_200_OK)
    