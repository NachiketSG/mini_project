from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('category/<int:category_id>/', views.products_by_category, name='products_by_category'),
    path('search/', views.search_products, name='search_products'),
    # NEW AUTHENTICATION URLs
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('upload-photo/', views.upload_profile_picture, name='upload_photo'),
]