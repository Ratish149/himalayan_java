from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import secrets

from .models import CustomUser
from .serializers import CustomUserSerializer, LoginSerializer, VerifyOTPSerializer


# 🔹 Helper function to generate OTP
def generate_otp(length=6):
    digits = "0123456789"
    return ''.join(secrets.choice(digits) for _ in range(length))


class CustomUserList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')

        if CustomUser.objects.filter(phone_number=phone_number).exists():
            return Response({'error': 'User with this phone number already exists.'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(username=serializer.validated_data['phone_number'])

        # Generate OTP
        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)


# 🔹 Step 1: Login - Generate OTP
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    http_method_names = ['post']   # ✅ POST only

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']

        user = CustomUser.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response({'error': 'User with this phone number does not exist.'},
                            status=status.HTTP_400_BAD_REQUEST)

        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        # TODO: send OTP via SMS/Email
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)


# 🔹 Step 2: Verify OTP
class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    http_method_names = ['post']   # ✅ POST only

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        otp = serializer.validated_data['otp']

        user = CustomUser.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        # Temporary: allow only fixed OTP
        if otp == '123456':
            refresh = RefreshToken.for_user(user)
            refresh['full_name'] = user.full_name
            refresh['email'] = user.email
            refresh['phone_number'] = user.phone_number
            refresh['profile_picture'] = user.profile_picture.url if user.profile_picture else None

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


# 🔹 Profile API (secured)
class ProfileView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
