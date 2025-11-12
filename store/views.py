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


from .forms import AddressForm, CheckoutForm
from .models import Address, Order, OrderItem

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    if not cart_items:
        return redirect('cart_view')
    
    total_price = sum(item.get_total_price() for item in cart_items)
    
    # Get user's saved addresses
    addresses = Address.objects.filter(user=request.user)
    
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        checkout_form = CheckoutForm(request.POST)
        
        if address_form.is_valid() and checkout_form.is_valid():
            # Save address
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                shipping_address=address,
                payment_method=checkout_form.cleaned_data['payment_method'],
                payment_status='pending'
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Clear cart
            cart_items.delete()
            
            return redirect('order_confirmation', order_id=order.id)
    else:
        address_form = AddressForm()
        checkout_form = CheckoutForm()
    
    return render(request, 'checkout/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'address_form': address_form,
        'checkout_form': checkout_form,
        'addresses': addresses
    })

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    return render(request, 'checkout/order_confirmation.html', {
        'order': order,
        'order_items': order_items
    })

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'checkout/order_history.html', {
        'orders': orders
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    return render(request, 'checkout/order_detail.html', {
        'order': order,
        'order_items': order_items
    })

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.ORDER_STATUS):
            order.status = new_status
            order.save()
            return redirect('/admin/store/order/')
    
    return render(request, 'admin/order_status_update.html', {
        'order': order,
        'status_choices': Order.ORDER_STATUS
    })

# User ke liye order status check karne ka view
@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    # Status progress calculation
    status_progress = {
        'pending': 25,
        'processing': 50,
        'shipped': 75,
        'delivered': 100
    }
    
    return render(request, 'checkout/track_order.html', {
        'order': order,
        'order_items': order_items,
        'progress': status_progress.get(order.status, 0)
    })