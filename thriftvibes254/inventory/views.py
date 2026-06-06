import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, JsonResponse
from django.templatetags.static import static
from django.utils.timezone import now
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt

from .models import Product, Sale, Order, OrderItem, MpesaTransaction, UserProfile
from .forms import ProductForm, SaleForm, OrderItemForm, CustomerSignupForm
from .mpesa import stk_push



def signup(request):
    if request.method == "POST":
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("inventory:dashboard")  
    else:
        form = CustomerSignupForm()

    
    return render(request, "registration/signup.html", {"form": form})   

def product_list(request):
    products = Product.objects.all().order_by('-date_added')
    return render(request, 'inventory/product_list.html', {'products': products})


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form})


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('inventory:product_list')
    return render(request, 'inventory/product_form.html', {'form': form})


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('inventory:product_list')
    return render(request, 'inventory/product_delete.html', {'product': product})

def record_sale(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            product = sale.product

            # ✅ FIXED FIELD NAME
            if sale.quantity > product.quantity:
                messages.error(request, 'Not enough stock available')
            else:
                # reduce stock
                product.quantity -= sale.quantity
                product.save()

                # calculate total
                sale.total_amount = Decimal(sale.quantity) * product.selling_price
                sale.save()

                messages.success(request, 'Sale recorded successfully')
                return redirect('inventory:product_list')
    else:
        form = SaleForm()

    return render(request, 'inventory/sale_form.html', {'form': form})

def product_gallery(request):
    products = Product.objects.all().order_by('-id')

    context = {
        'products': products
    }
    return render(request, 'inventory/product_gallery.html', context)
@login_required
def dashboard(request):
    products = Product.objects.all()
    return render(request, 'inventory/dashboard.html', {'products': products})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('inventory:dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'inventory/login.html', {'form': form})


def service_worker(request):
    sw_path = static("pwa/service-worker.js")
    with open("." + sw_path, "r") as f:
        return HttpResponse(f.read(), content_type="application/javascript")
    
@login_required
def create_order(request):
    order = Order.objects.create(customer=request.user)
    return redirect('inventory:add_order_items', order_id=order.id)

@login_required
def add_order_items(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    # 🚫 Lock order if not pending
    if order.status != "pending":
        messages.error(request, "You cannot modify this order.")
        return redirect("inventory:order_detail", order.id)

    items = order.items.all()

    if request.method == "POST":
        form = OrderItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.order = order
            item.save()

            messages.success(request, "Item added successfully")
            return redirect("inventory:add_order_items", order.id)
    else:
        form = OrderItemForm()

    context = {
        "order": order,
        "form": form,
        "items": items,
    }

    return render(request, "inventory/orders/add_items.html", context)



@login_required
def checkout_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user,
        status='pending'
    )

    if not order.items.exists():
        messages.error(request, "Your order has no items.")
        return redirect('add_order_items', order_id=order.id)

    if request.method == "POST":
        order.status = 'confirmed'
        order.save()
        return redirect('inventory:order_confirmation', order_id=order.id)

    return render(request, 'inventory/orders/checkout.html', {'order': order})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )
    return render(request, 'inventory/orders/confirmation.html', {'order': order})

@login_required
def customer_dashboard(request):
    return render(request, "customers/dashboard.html")




def redirect_after_login(request):
    if request.user.is_staff:
        return redirect("inventory:dashboard")
    else:
        return redirect("inventory:customer_dashboard")


@login_required
def pay_order(request, order_id):

    if request.method == "POST":

        phone = request.POST['phone']

        order = Order.objects.get(id=order_id)

        response = stk_push(
            phone,
            order.total_amount
        )

        Payment.objects.create(
            order=order,
            phone_number=phone,
            amount=order.total_amount,
            checkout_request_id=
                response.get("CheckoutRequestID")
        )

        return redirect('orders')

@csrf_exempt
def mpesa_callback(request):

    data = json.loads(
        request.body
    )

    callback = data['Body'][
        'stkCallback'
    ]

    checkout_id = callback[
        'CheckoutRequestID'
    ]

    result_code = callback[
        'ResultCode'
    ]

    payment = Payment.objects.get(
        checkout_request_id=checkout_id
    )

    if result_code == 0:

        payment.status = "PAID"

        payment.save()

        payment.order.payment_status = "PAID"

        payment.order.save()

    else:

        payment.status = "FAILED"

        payment.save()

    return JsonResponse({
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    })

@login_required
def user_profile(request):
    """Display user profile with details including email and signup date"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    context = {
        'user': user,
        'profile': profile,
        'signup_date': user.date_joined,
        'last_login': user.last_login,
    }
    return render(request, 'inventory/profile.html', context)

@login_required
def user_settings(request):
    """Settings page for users to manage profile and upload profile picture"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == "POST":
        # Handle profile picture upload
        if 'profile_pic' in request.FILES:
            profile.profile_pic = request.FILES['profile_pic']
            profile.save()
            messages.success(request, 'Profile picture updated successfully')
            return redirect('inventory:user_settings')
    
    context = {
        'user': user,
        'profile': profile,
        'is_staff': user.is_staff,
    }
    return render(request, 'inventory/settings.html', context)