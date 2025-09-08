from django.db import models


class Redeem(models.Model):
    redeem_points = models.PositiveIntegerField()
    sub_category = models.ForeignKey('product.SubCategory', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sub_category.name} - {self.redeem_points} points"


class UserRedeem(models.Model):
    """Tracks individual user redemptions/orders"""
    user = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE)
    redeem = models.ForeignKey(Redeem, on_delete=models.CASCADE)
    points_used = models.PositiveIntegerField(null=True, blank=True)  # Points deducted
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.redeem} - {self.points_used} points"

    def save(self, *args, **kwargs):
        if not self.points_used:
            self.points_used = self.redeem.redeem_points
        super().save(*args, **kwargs)
