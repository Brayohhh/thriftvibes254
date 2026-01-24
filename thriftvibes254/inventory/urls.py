from django.urls import path
from django.contrib.auth import views as auth_views
from.views import dashboard, order_confirmation, signup, checkout_order
from . import views
from .forms import CustomLoginForm
from .views import create_order, add_order_items
from .views import customer_dashboard, redirect_after_login


app_name = 'inventory'

urlpatterns = [
    path('', auth_views.LoginView.as_view( template_name="registration/login.html",
        authentication_form=CustomLoginForm),name='login'), # type: ignore
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('add/', views.product_create, name='product_create'),
    path('edit/<int:pk>/', views.product_update, name='product_update'),
    path('delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('sale/', views.record_sale, name='record_sale'),
    path('gallery/', views.product_gallery, name='product_gallery'),
    path("signup/", signup, name="signup"), 
    path(
    "accounts/login/",
    auth_views.LoginView.as_view(
        template_name="registration/login.html",
        authentication_form=CustomLoginForm
    ),
    name="login",
),
    path('orders/new/', views.create_order, name='create_order'),
    path(
        'orders/<int:order_id>/items/',
        views.add_order_items,
        name='add_order_items'
    ),
    path('orders/<int:order_id>/checkout/', checkout_order, name='checkout_order'),
    path('orders/<int:order_id>/confirmation/', order_confirmation, name='order_confirmation'),
    path("customer/dashboard/", customer_dashboard, name="customer_dashboard"),
    path("redirect/", redirect_after_login, name="redirect_after_login"),
]
    

