from django.db import models

# Create your models here.


class Branch(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    operating_hours = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
