from django.shortcuts import render
from rest_framework import generics

# Create your views here.

from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


class CustomUserList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        
        phone_number = request.data.get('phone_number')
        
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            return Response({'error': 'User with this phone number already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user= serializer.save()
            user.username=serializer.validated_data['phone_number']
            user.save()
            refresh = RefreshToken.for_user(user)
            refresh['full_name']=user.full_name
            refresh['email']=user.email
            refresh['phone_number']=user.phone_number
            refresh['profile_picture']=user.profile_picture.url if user.profile_picture else None

            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(generics.GenericAPIView):
    serializer_class = CustomUserSerializer

    def post(self, request):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(phone_number=phone_number).first()

        if not user:
            return Response({'error': 'User with this phone number does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        refresh['full_name']=user.full_name
        refresh['email']=user.email
        refresh['phone_number']=user.phone_number
        refresh['profile_picture']=user.profile_picture if user.profile_picture else None


        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response(data, status=status.HTTP_200_OK)

class ProfileView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]  # ensures only logged-in users can access

    def get_object(self):
        # Returns the currently authenticated user
        return self.request.user
    

