from django.shortcuts import render, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from .models import *
from django.contrib import messages

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    context = {
        'item_cats': Item_Category.objects.all(),
        'items': Item.objects.all(),
        'toppings': Topping.objects.all()
    }
    return render(request, 'orders/index.html', context)

def addItem_view(request):

    if request.method == 'POST':
        try:
            item_id = request.POST['item-id']
        except:
            item_id = None
        try:
            max_topping = request.POST['max-topping']
        except:
            max_topping = None
        try:
            size = request.POST['size-select']
        except:
            size = None
        
        toppings = []
        if max_topping:
            for i in max_topping:
                try:
                    top = request.POST[f'select-{i}']
                    toppings.append(Topping.objects.get(pk=top))
                except:
                    pass

        item = Item.objects.get(pk=item_id)
        if size == 'S':
            price = item.price_small
        elif size == 'L':
            price = item.price_large

        cart = Cart.objects.get(user=request.user)
        cart_item = Cart_Item(cart=cart, item_detail=item, size=size, price=price)
        cart_item.save()
        if len(toppings) > 0:
            for topping in toppings:
                cart_item.topping.add(topping)
            cart_item.save()
        cart.total += cart_item.price
        cart.save()
    messages.add_message(request, messages.INFO, f'Item {cart_item.item_detail} added!')
    return HttpResponseRedirect(reverse('home'))

def removeItem_view(request, cart_item_id):
    cart_item = Cart_Item.objects.get(pk=cart_item_id)
    cart = Cart.objects.get(user=request.user)
    cart.total -= cart_item.price
    cart_item.delete()
    cart.save()
    messages.add_message(request, messages.INFO, f'Item {cart_item.item_detail} removed!')
    return HttpResponseRedirect(reverse('cart'))

def emptyCart_view(request):
    cart = Cart.objects.get(user=request.user)
    cart.total = 0
    cart.save()
    cart_items = Cart_Item.objects.filter(cart=cart)
    if cart_items:
        for cart_item in cart_items:
            cart_item.delete()
    messages.add_message(request, messages.INFO, 'Cleared your cart!')
    return HttpResponseRedirect(reverse('cart'))

def cart_view(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = Cart_Item.objects.filter(cart=cart)
    if not cart_items:
        return render(request, 'orders/cart.html', {'empty': True})
    return render(request, 'orders/cart.html', {'empty': False, 'cart_items': cart_items, 'cart':cart})  

def order_view(request):
    cart = Cart.objects.get(user=request.user)
    cart_items =  Cart_Item.objects.filter(cart=cart)

    #create a new empty order
    order = Order(user=request.user, total=cart.total)
    order.save()

    for cart_item in cart_items:
        order_item = Order_Item(order=order, item_detail=cart_item.item_detail, size=cart_item.size, price=cart_item.price)
        order_item.save()
        order_item.topping.set(cart_item.topping.all())
        order_item.save()
    messages.add_message(request, messages.SUCCESS, f'Order #{order.pk} placed successfully!')
    emptyCart_view(request)
    return HttpResponseRedirect(reverse('home'))

def orders_view(request):
    orders = Order.objects.filter(user=request.user)
    if not orders:
        return render(request, 'orders/orders.html', {'empty': True})
    dic = dict()
    for order in orders:
        order_items = Order_Item.objects.filter(order=order)
        dic.update({order: order_items})

    return render(request, 'orders/orders.html', {'empty': False, 'dic': dic})

def viewOrders_view(request):
    if request.method == 'POST':
        pass
    else:
        if request.user.is_staff:
            orders = Order.objects.exclude(status='Completed')
            if not orders:
                return render(request, 'orders/vieworders.html', {'empty': True})
            dic = dict()
            for order in orders:
                order_items = Order_Item.objects.filter(order=order)
                dic.update({order: order_items})

            return render(request, 'orders/vieworders.html', {'empty': False, 'dic': dic})

def markComplete_view(request, order_item_id):
    order = Order.objects.get(pk=order_item_id)
    order.status = 'Completed'
    order.save()
    messages.add_message(request, messages.SUCCESS, f'Marked Order #{order.pk} as completed')
    return HttpResponseRedirect(reverse('vieworders'))

def register(request):
    if request.method == 'GET':
        return render(request, 'orders/register.html')
    try:
        username = request.POST['username']
        password = request.POST['password']
    except KeyError:
        messages.add_message(request, messages.ERROR, 'Invalid Entry')
        return HttpResponseRedirect(reverse('register'))
    if not username:
        messages.add_message(request, messages.ERROR, 'Invalid Username')
        return HttpResponseRedirect(reverse('register'))
    if not password:
        messages.add_message(request, messages.ERROR, 'Invalid password')
        return HttpResponseRedirect(reverse('register'))
    
    check_user = User.objects.filter(username=username)
    if check_user:
        messages.add_message(request, messages.ERROR, 'UserName already exists, try something else')
        return HttpResponseRedirect(reverse('register'))

    user = User.objects.create_user(username=username, password=password)
    user.save()
    login(request, user)

    cart = Cart(user=request.user)
    cart.save()
    messages.add_message(request, messages.SUCCESS, 'Registeration successful!')
    return HttpResponseRedirect(reverse('home'))

def login_view(request):
    if request.method == 'GET':
        return render(request, 'orders/login.html')
    try:
        username = request.POST['username']
        password = request.POST['password']
        
    except KeyError:
        messages.add_message(request, messages.ERROR, 'Invalid Entry')
        return HttpResponseRedirect(reverse('login'))
    if not username:
        messages.add_message(request, messages.ERROR, 'Invalid Username')
        return HttpResponseRedirect(reverse('login'))
    if not password:
        messages.add_message(request, messages.ERROR, 'Invalid password')
        return HttpResponseRedirect(reverse('login'))

    user = authenticate(request, username=username, password=password)
    if not user:
        return render(request, 'orders/login.html', {'errmsg': 'Invalid credentials'})
    else:
        login(request, user)
        messages.add_message(request, messages.SUCCESS, 'Logged in successfully')
        return HttpResponseRedirect(reverse('home'))

def logout_view(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, 'Logged Out successfully')
    return HttpResponseRedirect(reverse('home'))    