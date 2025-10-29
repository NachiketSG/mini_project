from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Product, Category, UserProfile  # ✅ UserProfile ADD kiya
from .forms import UserEditForm, ProfilePictureForm  # ✅ ProfilePictureForm ADD kiya

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