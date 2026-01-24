from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Sale, Order,  OrderItem
from decimal import Decimal
from django.contrib import messages
from .forms import ProductForm, SaleForm, OrderItemForm
from django.db.models import Sum
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.http import HttpResponse
from django.templatetags.static import static
from.forms import CustomerSignupForm



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
def dashboard(request):
    total_products = Product.objects.count()

    today = now().date()
    today_sales = Sale.objects.filter(date_sold__date=today)

    total_sales_today = today_sales.count()
    total_revenue_today = today_sales.aggregate(
        total=Sum('total_price')
    )['total'] or 0

    low_stock = Product.objects.filter(quantity__lte=5)

    context = {
        'total_products': total_products,
        'total_sales_today': total_sales_today,
        'total_revenue_today': total_revenue_today,
        'low_stock': low_stock,
    }

    products = Product.objects.all()
    return render(request, 'inventory/dashboard.html', {'products': products})

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
    items = order.items.all()

    if request.method == 'POST':
        form = OrderItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.order = order

            # 🔐 Stock protection
            if item.quantity > item.product.quantity:
                form.add_error('quantity', 'Not enough stock available')
            else:
                item.product.quantity -= item.quantity
                item.product.save()
                item.save()
                return redirect('inventory:add_order_items', order_id=order.id)
    else:
        form = OrderItemForm()

    context = {
        'order': order,
        'items': items,
        'form': form
    }
    return render(request, 'inventory/orders/add_items.html', context)



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
        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'orders/checkout.html', {'order': order})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )
    return render(request, 'orders/confirmation.html', {'order': order})

