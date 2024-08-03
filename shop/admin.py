from django.contrib import admin
from .models import Product, ShoppingCart, UserProfile, GeneratedBarcode

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'isle', 'barcode')
    search_fields = ('name', 'category')
    list_filter = ('category',)

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    search_fields = ('user__username', 'product__name')
    list_filter = ('user',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone_number', 'address')
    search_fields = ('user__username', 'full_name')

admin.site.register(GeneratedBarcode)