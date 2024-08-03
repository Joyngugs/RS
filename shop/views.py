from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth import logout as auth_logout
from .forms import UserUpdateForm, UserProfileForm
from django.db.models import F, FloatField, ExpressionWrapper, Sum
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse, HttpResponse
from .models import Product, ShoppingCart, UserProfile
from .forms import UserRegistrationForm
from barcode import Code39
from barcode.writer import ImageWriter
from pyzbar.pyzbar import decode
from PIL import Image
from .models import GeneratedBarcode
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.generic.edit import CreateView
from django.views.generic import ListView
import requests
import json
import io

def homepage(request):
    search_query = request.GET.get('search', '')
    selected_category = request.GET.get('category', '')

    # Get all category choices
    categories = Product.CATEGORY_CHOICES

    # Filter products based on search query and category
    products = Product.objects.all()
    if search_query:
        products = products.filter(name__icontains=search_query)  # Filter by name
    if selected_category:
        products = products.filter(category=selected_category)  # Filter by category

    return render(request, "shop/homepage.html", {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'search': search_query
    })

def logout(request):
    auth_logout(request)
    return redirect('homepage')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save the new user
            user = form.save()
            # Get cleaned data for additional fields
            full_name = form.cleaned_data.get('full_name')
            phone_number = form.cleaned_data.get('phone_number')
            address = form.cleaned_data.get('address')
            
            # Create the UserProfile object
            UserProfile.objects.create(user=user, full_name=full_name, phone_number=phone_number, address=address)
            
            # Authenticate and log in the user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('homepage')  # Redirect to the correct URL pattern name
    else:
        form = UserRegistrationForm()
    return render(request, 'shop/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('homepage')  # Adjust this to the correct URL name
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def privacy_policy(request):
    return render(request, 'shop/privacy_policy.html')

def terms_of_use(request):
    return render(request, 'shop/terms_of_use.html')

def sales_and_refund_policy(request):
    return render(request, 'shop/sales_and_refund_policy.html')

@login_required
def personal_details(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=request.user.userprofile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save()
            update_session_auth_hash(request, user)  # Important for password changes
            return redirect('personal_details')
    else:
        user_form = UserUpdateForm(instance=request.user)
        # Get or create the user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'shop/personal_details.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

def search_results(request):
    query = request.GET.get('query', '')
    
    # Define category keywords
    category_keywords = {
        'electronics': ['phone', 'laptop', 'headphones', 'camera'],
        'clothing': ['tshirt', 'short', 'dress', 'jeans', 'jacket'],
        'home': ['furniture', 'decor', 'appliances'],
        'groceries': ['food', 'beverages', 'snacks'],
        'health_beauty': ['skincare', 'makeup', 'vitamins'],
        'toys': ['action figure', 'doll', 'game']
    }
    
    # Default category
    category = None
    
    # Check if the query matches any category keywords
    for cat, keywords in category_keywords.items():
        if any(keyword in query.lower() for keyword in keywords):
            category = cat
            break
    
    # Debug: Print category and query to console
    print(f"Query: {query}")
    print(f"Category: {category}")
    
    # Filter products based on category and query
    if category:
        products = Product.objects.filter(category=category, name__icontains=query)
    else:
        products = Product.objects.filter(name__icontains=query)
    
    # Debug: Print number of products found
    print(f"Number of products found: {products.count()}")
    
    return render(request, 'shop/search_results.html', {'products': products, 'query': query})


@csrf_exempt
def complete_shopping(request):
    if request.method == 'POST':
        user = request.user
        cart_items = ShoppingCart.objects.filter(user=user)
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        tax = subtotal * 0.005
        total_price = subtotal + tax 

        if 'mpesa_number' in request.POST:
            mpesa_number = request.POST.get('mpesa_number')
            mpesa_response = requests.post('https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', json={
                'BusinessShortCode': '174379',
                'Password': 'YOUR_PASSWORD',
                'Timestamp': 'YOUR_TIMESTAMP',
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': total_price,
                'PartyA': mpesa_number,
                'PartyB': '174379',
                'PhoneNumber': mpesa_number,
                'CallBackURL': 'YOUR_CALLBACK_URL',
                'AccountReference': 'Shopping',
                'TransactionDesc': 'Shopping Payment'
            })

            if mpesa_response.status_code == 200:
                cart_items.delete()
                return JsonResponse({'message': 'Payment successful'})
            else:
                return JsonResponse({'error': 'Payment failed'}, status=400)

    return render(request, 'shop/complete_shopping.html', {'total_price': total_price})

def product_list(request):
    selected_category = request.GET.get('category', '')
    categories = Product.CATEGORY_CHOICES

    if selected_category:
        products = Product.objects.filter(category=selected_category)
    else:
        products = Product.objects.all()

    return render(request, 'shop/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category
    })

class ProductListView(ListView):
    model = Product
    template_name = 'shop/product_list.html'  # Define your template here
    context_object_name = 'products'

@login_required
@csrf_exempt
def add_to_cart(request, product_id):
    if request.method == "GET":
        try:
            product = Product.objects.get(id=product_id)
            cart_item, created = ShoppingCart.objects.get_or_create(user=request.user, product=product)
            if not created:
                cart_item.quantity += 1
                cart_item.save()

            return JsonResponse({'success': True, 'message': 'Product added to cart'})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required(login_url='/register/')
def shopping_cart(request):
    user = request.user
    cart_items = ShoppingCart.objects.filter(user=user)
    
    # Compute total price for each item and overall total price
    cart_items = cart_items.annotate(
        total_price=ExpressionWrapper(
            F('product__price') * F('quantity'),
            output_field=FloatField()
        )
    )
    
    total_price = cart_items.aggregate(total=Sum('total_price'))['total'] or 0
    
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
@csrf_exempt
@require_POST
def update_cart(request, product_id):
    try:
        data = json.loads(request.body)
        quantity = data.get('quantity', 0)
        if quantity < 1:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)

        product = Product.objects.get(id=product_id)
        cart_item, created = ShoppingCart.objects.get_or_create(user=request.user, product=product)
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()
        return JsonResponse({'success': True})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
@login_required
@csrf_exempt
def delete_from_cart(request, product_id):
    if request.method == 'DELETE':
        product = get_object_or_404(Product, id=product_id)
        cart_item = get_object_or_404(ShoppingCart, user=request.user, product=product)
        cart_item.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

def generate_barcode(request, code):
    code_obj = Code39(code, writer=ImageWriter())
    buffer = io.BytesIO()
    code_obj.write(buffer)
    buffer.seek(0)
    barcode_obj, created = GeneratedBarcode.objects.get_or_create(code=code)
    
    if created:
        barcode_obj.image.save(f'{code}.png', buffer, save=True)
        action_performed = "created"
    else:
        action_performed = "fetched"

    return HttpResponse(f'Barcode "{code}" {action_performed} successfully! <a href="{barcode_obj.image.url}">IMAGE LINK</a>')

@login_required
@csrf_exempt
def scan_barcode(request):
    if request.method == 'POST':
        try:
            barcode_image = request.FILES['barcode_image']
            image = Image.open(barcode_image)
            decoded_objects = decode(image)
            
            if decoded_objects:
                barcode_data = decoded_objects[0].data.decode('utf-8')
                barcode_obj = GeneratedBarcode.objects.get(code=barcode_data)
                return HttpResponse(f'Scanned Barcode: {barcode_obj.code}, Image: <a href="{barcode_obj.image.url}">IMAGE LINK</a>.')
            else:
                return HttpResponse('No barcode found.')
        except Exception as e:
            return HttpResponse(f'Error: {str(e)}', status=500)
    else:
        return render(request, 'shop/scan.html')