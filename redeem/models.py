from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Redeem(models.Model):
    redeem_points = models.PositiveIntegerField()
    sub_category = models.ForeignKey('product.SubCategory', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sub_category.name} - {self.redeem_points} points"


class UserRedeem(models.Model):
    """Track individual redemptions/orders"""
    user = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE,null=True,blank=True)
    redeem = models.ForeignKey(Redeem, on_delete=models.CASCADE)
    points_used = models.PositiveIntegerField(null=True, blank=True)  # Points deducted for this redemption
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.redeem} - {self.points_used} points"

    def save(self, *args, **kwargs):
        # Set points_used to redeem item's points if not already set
        if not self.points_used:
            self.points_used = self.redeem.redeem_points
        super().save(*args, **kwargs)
