from django.db import models

# Create your models here.

class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    order_number=models.CharField(max_length=50,null=True,blank=True)
    order_status=models.CharField(max_length=50, choices=ORDER_STATUS,default='pending')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    total_price=models.DecimalField(max_digits=10, decimal_places=2)
    user=models.ForeignKey('account.CustomUser', on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return self.order_number
    
class OrderItem(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product=models.ForeignKey('product.Product', on_delete=models.CASCADE)
    quantity=models.IntegerField()
    price=models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)