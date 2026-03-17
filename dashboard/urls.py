from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('products/', views.product_list, name='dashboard_products'),
    path('products/add/', views.add_product, name='dashboard_add_product'),
    path('orders/', views.order_list, name='dashboard_orders'),
    path('categories/', views.category_list, name='dashboard_categories'),
]