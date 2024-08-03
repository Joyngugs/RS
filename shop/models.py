from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('home', 'Home'),
        ('groceries', 'Groceries'),
        ('health_beauty', 'Health & Beauty'),
        ('toys', 'Toys'),
        # Add more categories as needed
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=100)
    details = models.TextField()
    size_or_amount = models.CharField(max_length=50)
    picture = models.ImageField(upload_to='products/')
    isle = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    barcode = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username}'s cart - {self.product.name}"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=False)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username

class GeneratedBarcode(models.Model):
    code = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='media/barcodes/')

    def __str__(self):
        return self.code
