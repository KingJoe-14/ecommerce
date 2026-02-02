from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages

def cart_summary(request):
    #get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    return render(request, "cart_summary.html", {"cart_products": cart_products, "quantities": quantities, "totals": totals})


def cart_add(request):
    #get cart
    cart = Cart(request)
    #test for post
    if request.POST.get('action') == 'post':
        #get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = request.POST.get('product_qty', '1') 

        product = get_object_or_404(Product, id=product_id)

        #save to session
        cart.add(product=product, quantity=product_qty)
        
        #get cart quantity
        cart_quantity = cart.__len__()

        #return response
        #response = JsonResponse({ 'product Name: ': product.name})    
        response = JsonResponse({'qty': cart_quantity})   
        messages.success(request, ("Product Added To Cart")) 
        return response

def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        #call delete function in cart
        cart.delete(product=product_id)

        response = JsonResponse({'product':product_id})
        messages.success(request, ("Item Deleted From Shopping Cart"))
        return response


def cart_update(request):
    cart = Cart(request)
    
    # Ensure the request method is POST and the correct action is triggered
    if request.POST.get('action') == 'post':
        product_id = request.POST.get('product_id')
        product_qty = request.POST.get('product_qty')

        # Validate product_id
        if not product_id or not product_id.isdigit():
            return JsonResponse({'error': 'Invalid product ID'}, status=400)

        # Validate product_qty
        if not product_qty or not product_qty.isdigit():
            return JsonResponse({'error': 'Invalid product quantity'}, status=400)

        # Cast to integers after validation
        product_id = int(product_id)
        product_qty = int(product_qty)
        
        # Check if quantity is a positive number
        if product_qty <= 0:
            return JsonResponse({'error': 'Quantity must be greater than zero'}, status=400)
        
        # Update the cart
        cart.update(product=product_id, quantity=product_qty)
        
        # Add Django message
        messages.success(request, "Your Cart Has Been Updated")

        # Include the message in the JSON response
        return JsonResponse({'qty': product_qty, })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

