from django.shortcuts import render, redirect
from store.models import Product, Category
from store.models import Order
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from store.models import Product, Category, Order, Variation, VariationOption

@login_required
def dashboard_home(request):
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='Pending').count()
    total_products = Product.objects.count()
    total_categories = Category.objects.count()

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'total_categories': total_categories,
    }
    return render(request, 'dashboard/dashboard_home.html', context)


@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'dashboard/product_list.html', {'products': products})


@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'dashboard/order_list.html', {'orders': orders})


@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'dashboard/category_list.html', {'categories': categories})


@login_required
def add_product(request):
    if request.method == 'POST':
        # Save product first
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product = product_form.save()

            # Handle variations and options
            for key in request.POST:
                if key.startswith('variation-') and key.endswith('-name'):
                    var_name = request.POST[key]
                    variation = Variation.objects.create(product=product, name=var_name)

                    # Get options for this variation
                    options_container = request.POST.getlist(f'options-{var_name}-name')
                    price_container = request.POST.getlist(f'options-{var_name}-price')
                    for option_name, price in zip(options_container, price_container):
                        if option_name:
                            VariationOption.objects.create(
                                variation=variation,
                                name=option_name,
                                price_modifier=price or 0
                            )
            return redirect('dashboard_products')
    else:
        product_form = ProductForm()

    return render(request, 'dashboard/add_product.html', {'product_form': product_form})