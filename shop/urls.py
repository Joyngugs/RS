from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import complete_shopping, shopping_cart, homepage, register, user_login, product_list, search_results, ProductListView

urlpatterns = [
    path("", homepage, name="homepage"),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('complete_shopping/', complete_shopping, name='complete_shopping'),
    path('logout/', views.logout, name='logout'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('shopping_cart/', shopping_cart, name='shopping_cart'),
    path('delete_from_cart/<int:product_id>/', views.delete_from_cart, name='delete_from_cart'),
    path('product_list/', product_list, name='product_list'),  
    path('update_cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('search/', search_results, name='search_results'),
    path('generate/<str:code>/', views.generate_barcode, name='generate_barcode'),
    path('scan/', views.scan_barcode, name='scan_barcode'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-use/', views.terms_of_use, name='terms_of_use'),
    path('sales-and-refund-policy/', views.sales_and_refund_policy, name='sales_and_refund_policy'),
    path('my-account/', views.personal_details, name='personal_details'),
    path('complete-shopping/', views.complete_shopping, name='complete_shopping'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
]
