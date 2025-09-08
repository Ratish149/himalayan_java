from django.db import models
from product.models import Product
from account.models import CustomUser

class Favorite(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "user")  # prevent duplicates
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} -> {self.product.name}"
