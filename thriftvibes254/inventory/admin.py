from django.contrib import admin
from .models import Product, Sale, Order, OrderItem, Payment


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


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order',
        'phone_number',
        'amount',
        'status',
        'created_at'
    )
    list_filter = ('status',)
    search_fields = ('phone_number', 'mpesa_receipt_number')
