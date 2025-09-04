from django.db import models
from branch.models import Branch
# Create your models here.
class ProductCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.name

class ProductSize(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.FileField(upload_to='product_images',null=True,blank=True)
    image_alt_description = models.CharField(max_length=100,null=True,blank=True)
    size = models.ManyToManyField(ProductSize,blank=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    redeem_points = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    featured_points = models.PositiveIntegerField(default=0)
    

    def __str__(self):
        return self.name

class ProductAddOns(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='add_ons')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name