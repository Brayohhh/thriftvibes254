from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Sale
from decimal import Decimal
from django.contrib import messages
from .forms import ProductForm, SaleForm
from django.db.models import Sum
from django.utils.timezone import now


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

            if sale.quantity_sold > product.quantity:
                messages.error(request, 'Not enough stock available')
            else:
                product.quantity -= sale.quantity_sold
                product.save()

                sale.total_price = Decimal(sale.quantity_sold) * product.selling_price
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

    return render(request, 'inventory/dashboard.html', context)
