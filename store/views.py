from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Product, Category, UserProfile, Cart, CartItem
from .forms import UserEditForm, ProfilePictureForm

# Helper function for cart (NEW)
def get_or_create_cart(request):
    """Get cart for logged-in user or create for guest"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # Guest user - use session
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart

# Home Page View - Product listings with categories
def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'home.html', {
        'products': products,
        'categories': categories
    })

# Product Details Page
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {
        'product': product
    })

# Products by Category
def products_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    return render(request, 'products.html', {
        'products': products,
        'categories': categories,
        'current_category': category
    })

# Search Products
def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'products.html', {
        'products': products,
        'categories': categories,
        'query': query
    })

# User Registration - SIGNUP
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# User Profile - PROFILE
@login_required
def profile(request):
    # Create profile if doesn't exist
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'registration/profile.html', {
        'user': request.user,
        'profile': profile
    })

# Edit Profile
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'registration/edit_profile.html', {'form': form})

# Upload Profile Picture
@login_required
def upload_profile_picture(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfilePictureForm(instance=profile)
    
    return render(request, 'registration/upload_photo.html', {'form': form})

# Add to Cart Function (UPDATED for guest users)
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get or create cart for user (guest or logged-in)
    cart = get_or_create_cart(request)
    
    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('cart_view')

# Cart View Page (UPDATED for guest users)
def cart_view(request):
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=cart)
    
    total_price = sum(item.get_total_price() for item in cart_items)
    
    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'user': request.user  # Add user context for template
    })

# Remove from Cart (UPDATED for guest users)
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    return redirect('cart_view')

# Update Cart Quantity (UPDATED for guest users)
def update_cart_quantity(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    
    return redirect('cart_view')