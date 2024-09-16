from rest_framework import serializers
from django.conf import settings
from .models import (
    User,
    BugUserDetail,
    Message,
    BugUserEducation,
    BugBearSkill,
    BugUserSkill,
    BugOrganizationDetail,
)
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if "data:" in data and ";base64," in data:
                # Break out the header from the base64 content
                header, data = data.split(";base64,")

            # Try to decode the file. Return validation error if it fails.
            try:
                print(data)
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail("invalid_image")

            # Generate file name:
            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (
                file_name,
                file_extension,
            )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class UserRegistrationSerializer(serializers.ModelSerializer):
    # We are writing this becoz we need confirm password field in our Registratin Request
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "password2", "tc", "user_type"]
        extra_kwargs = {"password": {"write_only": True}}

    # Validating Password and Confirm Password while Registration
    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password != password2:
            raise serializers.ValidationError(
                "Password and Confirm Password doesn't match"
            )

        email = attrs.get("email")
        # check if email is already taken
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email is already taken")

        return attrs

    def create(self, validate_data):
        print(validate_data)
        return User.objects.create_user(**validate_data)


class UserLoginSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ["email", "password"]


class UserProfileSerializer(serializers.ModelSerializer):
    user_type_name = serializers.CharField(source="user_type.name", read_only=True)
    profile_pic_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "is_active", "user_type_name", "profile_pic_url"]

    def get_profile_pic_url(self, obj):
        request = self.context.get("request")
        if obj.profile_pic and request:
            return request.build_absolute_uri(obj.profile_pic.url)
        return None


class BugUserDetailSerializer(serializers.ModelSerializer):
    profile_pic_url = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = BugUserDetail
        fields = [
            "id",
            "first_name",
            "last_name",
            "dob",
            "country",
            "city",
            "address",
            "phone",
            "profile_pic_url",
            "about_me",
            "position",
            "email",
        ]
        extra_kwargs = {"profile_pic": {"read_only": True}}

    def get_profile_pic_url(self, obj):
        try:
            if obj.profile_pic:

                return settings.WEB_URL + str(obj.profile_pic.url)
            return None
        except BugUserDetail.DoesNotExist:
            return None

    def get_email(self, obj):
        return obj.user.email


class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        fields = ["password", "password2"]

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        user = self.context.get("user")
        if password != password2:
            raise serializers.ValidationError(
                "Password and Confirm Password doesn't match"
            )
        user.set_password(password)
        user.save()
        return attrs


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print("Encoded UID", uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print("Password Reset Token", token)
            link = "http://localhost:3000/api/user/reset/" + uid + "/" + token
            print("Password Reset Link", link)
            # Send EMail
            body = "Click Following Link to Reset Your Password " + link
            data = {
                "subject": "Reset Your Password",
                "body": body,
                "to_email": user.email,
            }
            # Util.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError("You are not a Registered User")


class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        fields = ["password", "password2"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            password2 = attrs.get("password2")
            uid = self.context.get("uid")
            token = self.context.get("token")
            if password != password2:
                raise serializers.ValidationError(
                    "Password and Confirm Password doesn't match"
                )
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Token is not Valid or Expired")
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError("Token is not Valid or Expired")


class PostUserSerializer(serializers.ModelSerializer):
    profile_pic_url = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    class Meta:
        model = BugUserDetail
        fields = ["id", "first_name", "last_name", "profile_pic_url"]

    def get_first_name(self, obj):
        print(obj.buguserdetail)
        return obj.buguserdetail.first_name

    def get_last_name(self, obj):
        return obj.buguserdetail.last_name

    def get_profile_pic_url(self, obj):
        # Access the User object associated with the BugUserDetail object
        user = obj.buguserdetail
        # Now you can access the profile_pic field of the User object
        if user.profile_pic:
            return "http://127.0.0.1:8000" + str(user.profile_pic.url)
        return None


class MessageSerializer(serializers.ModelSerializer):
    author = PostUserSerializer()
    friend = PostUserSerializer()

    class Meta:
        model = Message
        fields = ["id", "author", "friend", "message", "timestamp"]


class BugUserEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BugUserEducation
        fields = [
            "id",
            "user",
            "school_name",
            "degree",
            "field_of_study",
            "start_date",
            "end_date",
        ]

        # make id read_only
        extra_kwargs = {"id": {"read_only": True}}


class BugBearSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = BugBearSkill
        fields = ["id", "name", "description"]

        # make id read_only
        extra_kwargs = {"id": {"read_only": True}}


class BugUserSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = BugUserSkill
        fields = ["id", "user", "skill"]

        # make id read_only
        extra_kwargs = {"id": {"read_only": True}}


class BugOrganizationDetailSerializer(serializers.ModelSerializer):
    profile_pic_url = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    company_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = BugOrganizationDetail
        fields = [
            'id',
            'user',
            'first_name',
            'last_name',
            'current_location',
            'current_company_name',
            'current_designation',
            'about_company',
            'address',
            'city',
            'state',
            'country',
            'zip_code',
            'profile_pic_url',
            'email',
            'company_logo_url',
        ]
        read_only_fields = ['user', 'profile_pic']  # You might want the user to be read-only, if it's auto-assigned

    def get_profile_pic_url(self, obj):
        try:
            if obj.profile_pic:

                return settings.WEB_URL + str(obj.profile_pic.url)
            return None
        except BugUserDetail.DoesNotExist:
            return None
        
    def get_company_logo_url(self, obj):
        try:
            if obj.company_logo:

                return settings.WEB_URL + str(obj.company_logo.url)
            return None
        except BugUserDetail.DoesNotExist:
            return None
        
    def get_email(self, obj):
        return obj.user.email

    def create(self, validated_data):
        # You can add custom logic if needed before creating the instance
        return BugOrganizationDetail.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Custom logic for updating, if necessary
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.current_location = validated_data.get('current_location', instance.current_location)
        instance.current_company_name = validated_data.get('current_company_name', instance.current_company_name)
        instance.current_designation = validated_data.get('current_designation', instance.current_designation)
        instance.address = validated_data.get('address', instance.address)
        instance.about_company = validated_data.get('about_company', instance.about_company)
        instance.city = validated_data.get('city', instance.city)
        instance.state = validated_data.get('state', instance.state)
        instance.country = validated_data.get('country', instance.country)
        instance.zip_code = validated_data.get('zip_code', instance.zip_code)

        instance.save()
        return instance
