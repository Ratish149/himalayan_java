from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.



class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(null=True,blank=True)
    phone_number=models.CharField(max_length=15)
    profile_picture=models.FileField(upload_to='profile_pictures',null=True,blank=True)

    def __str__(self):
        return self.full_name
