from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('category/<int:category_id>/', views.products_by_category, name='products_by_category'),
    path('search/', views.search_products, name='search_products'),
]