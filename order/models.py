# models.py
from django.db import models
import secrets
from product.models import Product
from branch.models import Branch

def generate_order_number():
    """Generate a unique order number using secrets module"""
    return f"ORD-{secrets.token_hex(6).upper()}"  # Use 6 hex chars for better length

class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed','Completed'),
        ('cancelled', 'Cancelled'),
    )
    ORDER_TYPE = (
        ('dine-in', 'Dine-in'),
        ('take-away', 'Take-away'),
    )

    order_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS, default='pending')
    order_type = models.CharField(max_length=50, choices=ORDER_TYPE, default='dine-in', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    user = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    special_requests = models.TextField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        """Override save to generate order number if not provided"""
        if not self.order_number:
            max_attempts = 10
            attempts = 0
            while attempts < max_attempts:
                order_num = generate_order_number()
                if not Order.objects.filter(order_number=order_num).exists():
                    self.order_number = order_num
                    break
                attempts += 1
            
            if not self.order_number:
                # Fallback if we can't generate unique number
                import time
                self.order_number = f"ORD-{int(time.time())}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number if self.order_number else f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)