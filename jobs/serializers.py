from rest_framework import serializers
from .models import BugJob, BugJobCategory, JobsApplied, JobSaved
from buguser.serializers import BugOrganizationDetailSerializer, BugUserDetailSerializer


class JobSerializer(serializers.ModelSerializer):
    organisation = BugOrganizationDetailSerializer(source='company', read_only=True)

    class Meta:
        model = BugJob
        fields = ["id", "title", "skills", "qualifications", "responsibilities", "job_posted", "job_expiry",
                  "salary_min", "salary_max", "location", "job_type", "experience", "education", "featured",
                  "organisation", "category"]


class JobTitleSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BugJobCategory
        fields = ["id", "name"]


class JobAppliedSerializer(serializers.ModelSerializer):
    job = JobSerializer()
    a_user = BugUserDetailSerializer(source='user', read_only=True)

    class Meta:
        model = JobsApplied
        fields = ["id", "job", "a_user", "applied_date", "is_approved"]


class JobSavedSerializer(serializers.ModelSerializer):
    job = JobSerializer()
    a_user = BugUserDetailSerializer(source='user', read_only=True)

    class Meta:
        model = JobSaved
        fields = ["id", "job", "a_user", "saved_date"]

