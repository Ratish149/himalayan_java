import secrets

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .serializers import (
    AdminLoginSerializer,
    AdminRegisterSerializer,
    CustomUserSerializer,
    LoginSerializer,
    UserProfileSerializer,
    VerifyOTPSerializer,
)


# 🔹 Helper function to generate OTP
def generate_otp(length=6):
    digits = "0123456789"
    return "".join(secrets.choice(digits) for _ in range(length))


class CustomUserList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")

        if CustomUser.objects.filter(phone_number=phone_number).exists():
            return Response(
                {"error": "User with this phone number already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(username=serializer.validated_data["phone_number"])

        # Generate OTP
        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]

        user = CustomUser.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response(
                {"error": "User with this phone number does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        # TODO: send OTP via SMS/Email
        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        otp = serializer.validated_data["otp"]

        user = CustomUser.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response(
                {"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Temporary: allow only fixed OTP
        if otp == "123456":
            refresh = RefreshToken.for_user(user)
            refresh["full_name"] = user.full_name
            refresh["email"] = user.email
            refresh["phone_number"] = user.phone_number
            refresh["profile_picture"] = (
                user.profile_picture.url if user.profile_picture else None
            )

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )

        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.GenericAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)


# Admin Login with Email and password


class CreateAdminView(generics.CreateAPIView):
    serializer_class = AdminRegisterSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        phone_number = request.data.get("phone_number")
        full_name = request.data.get("full_name", "")
        role = request.data.get("role", "")

        # Check if user with this phone number already exists
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            return Response(
                {"error": "User with this phone number already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create the admin user with proper password hashing
        user = CustomUser.objects.create_user(
            username=phone_number,  # Required for AbstractUser
            email=email,
            password=password,
            phone_number=phone_number,
            full_name=full_name,
            role=role,
        )

        # Convert to dict for JSON response (remove password)
        user_data = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

        return Response(user_data, status=status.HTTP_201_CREATED)


class AdminLoginView(generics.GenericAPIView):
    serializer_class = AdminLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not user.check_password(password):
            return Response(
                {"error": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST
            )
        refresh = RefreshToken.for_user(user)
        refresh["full_name"] = user.full_name
        refresh["email"] = user.email
        refresh["phone_number"] = user.phone_number
        refresh["profile_picture"] = (
            user.profile_picture.url if user.profile_picture else None
        )
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class UserListApiView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()

    def get_queryset(self, *args, **kwargs):
        user = self.request.user

        if hasattr(user, "role") and user.role in ["admin"]:
            return CustomUser.objects.filter(
                branch=user.branch, role__in=["admin", "staff"]
            )
        elif hasattr(user, "role") and user.role == "superadmin":
            return CustomUser.objects.all()

        else:
            return CustomUser.objects.none()
