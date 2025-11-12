from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Cart, CartItem, UserProfile, Address

# Category Admin
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

# Product Admin  
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'stock', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock']

# Order Admin (UPDATED)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'payment_method', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['user__username', 'id']
    readonly_fields = ['created_at', 'updated_at']

# OrderItem Admin 
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'get_total_price']
    list_filter = ['order__status']
    
    def get_total_price(self, obj):
        return obj.quantity * obj.price
    get_total_price.short_description = 'Total Price'

# Cart Admin
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_key']

# CartItem Admin
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'added_at']
    list_filter = ['added_at']
    search_fields = ['product__name']

# UserProfile Admin
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_picture']

# Address Admin (NEW)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'city', 'state', 'postal_code', 'is_default']
    list_filter = ['city', 'state', 'is_default']
    search_fields = ['user__username', 'full_name', 'city']

# Register your models with custom admin
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Address, AddressAdmin)