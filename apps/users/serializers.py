from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import PasswordResetSerializer
from django.contrib.auth import get_user_model
from django_countries.serializer_fields import CountryField
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from apps.profiles.models import PhysicianPatient
from django.core.exceptions import ValidationError
from .forms import CustomResetForm

User = get_user_model()

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        token["user_is_admin"] = user.is_admin
        return token


class UserSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(source="profile.gender")
    phone_number = PhoneNumberField(source="profile.phone_number")
    profile_photo = serializers.ReadOnlyField(source="profile.profile_photo.url")
    country = CountryField(source="profile.country")
    city = serializers.CharField(source="profile.city")

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "gender",
            "phone_number",
            "profile_photo",
            "country",
            "city",
        ]

    def to_representation(self, instance):
        representation = super(UserSerializer, self).to_representation(instance)
        if instance.is_superuser:
            representation["admin"] = True
        return representation


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    is_admin = serializers.BooleanField(required=False)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    referral_code = serializers.CharField(required=False)

    def get_cleaned_data(self):
        return {
            "email": self.validated_data.get("email", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "is_admin": self.validated_data.get("is_admin", False),
            "password1": self.validated_data.get("password1", ""),
            "referral_code": self.validated_data.get("referral_code", ""),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user.email = self.cleaned_data.get("email")
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.is_admin = self.cleaned_data.get("is_admin")
        if (
            self.cleaned_data.get("referral_code")
            and self.cleaned_data.get("is_admin") == True
        ):
            raise serializers.ValidationError(
                {"permission_error": "You can't be a physician and a patient"}
            )
        # if self.cleaned_data.get("referral_code"):
        #     try:
        #         physician = PhysicianPatient.objects.get(
        #             referral_code=self.cleaned_data.get("referral_code")
        #         )
        #     except (PhysicianPatient.DoesNotExist, ValidationError):
        #         raise serializers.ValidationError(
        #             {"referral_code": "Invalid referral code."}
        #         )
        #     else:
        #         user.save()
        #         physician.patients.add(user)
        else:
            user.save()
            adapter.save_user(request, user, self)
            setup_user_email(request, user, [])

        return user


class SignInSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True, write_only=True)

    class Meta:
        model = User
        fields = ("email", "password")


class CustomPasswordResetSerializer(PasswordResetSerializer):
    """
    Serializer for requesting a password reset e-mail.
    """

    @property
    def password_reset_form_class(self):
        return CustomResetForm
