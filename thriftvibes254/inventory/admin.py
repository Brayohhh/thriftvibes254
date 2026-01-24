from django.contrib import admin
from .models import Product, Sale, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'created_at')
    list_filter = ('status',)
    inlines = [OrderItemInline]


admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(Order, OrderAdmin)
