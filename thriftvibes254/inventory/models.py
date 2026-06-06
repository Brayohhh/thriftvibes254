from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True, default='profiles/default_avatar.png')
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('T-SHIRT', 'T-Shirt'),
        ('HOODIE', 'Hoodie'),
        ('JEANS', 'Jeans'),
        ('SHOES', 'Shoes'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    size = models.CharField(max_length=10)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.size})"



class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    order_id = models.CharField(max_length=40, blank=True, null=True)

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Order {self.order_id} - {self.customer.username}"

    def save(self, *args, **kwargs):
        # Generate a human-friendly unique order_id on first save
        if not self.order_id:
            base = timezone.now().strftime('%Y%m%d%H%M%S')
            rand = get_random_string(4).upper()
            candidate = f"TV-{base}-{rand}"
            # Ensure uniqueness
            while Order.objects.filter(order_id=candidate).exists():
                rand = get_random_string(4).upper()
                candidate = f"TV-{base}-{rand}"
            self.order_id = candidate
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    
    class Meta:
        unique_together = ('order', 'product')

class Payment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )

    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    checkout_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    mpesa_receipt_number = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    merchant_request_id= models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.phone_number
    
    class Meta:
        ordering = ['-created_at']

class MpesaTransaction(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="mpesa_transaction"
    )
    checkout_request_id = models.CharField(max_length=100)
    merchant_request_id = models.CharField(max_length=100)
    amount = models.IntegerField()
    phone = models.CharField(max_length=20)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    transaction_date = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Prefer the human-friendly order identifier when available
        order_ref = getattr(self.order, 'order_id', None) or self.order.id
        return f"M-Pesa Order {order_ref} - {self.status}"
