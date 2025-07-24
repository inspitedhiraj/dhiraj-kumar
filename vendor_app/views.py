from django.shortcuts import render, redirect
from tannis_app.models import *
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# from array import *
# from django.contrib.sessions.backends.db import SessionStore
# from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
# from tannis_app.serializer import *
# from rest_framework.response import Response
import datetime
from django.utils.text import slugify
import uuid
from django.db.models import F
import os
import random

# Create your views here.

@login_required(login_url='/vendor/login/')
def VendorDashboard(request):
    vendor_contact = request.user.email
    number_of_product = Product.objects.filter(vendor_contact=vendor_contact).count()
    number_of_order = Ordered_item.objects.filter(variant__product__vendor_contact=vendor_contact).count()
    CONTEXT = {'number_of_product':number_of_product, 'number_of_order':number_of_order}
    return render(request, 'vendor/index.html', CONTEXT)

def VendorLogout(request):
    logout(request)
    return redirect('/vendor/login')

def VendorLogin(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.filter(username=email)
        if not user.exists():
            messages.info(request, 'User does not exist.')
            return redirect('/vendor/login')
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/vendor/dashboard')
        else:
            messages.info(request, 'Password is incorrect.')
            return redirect('/vendor/login')
    return render(request, 'vendor/login.html')

@login_required(login_url='/vendor/login/')
def ListProduct(request):
    product = Product.objects.all()
    CONTEXT = {'product':product}
    return render(request, 'vendor/list-product.html', CONTEXT)

@login_required(login_url='/vendor/login/')
def AddProduct(request):
    if request.method =='POST':
        try:
            category_id = request.POST.get('category')
            category = Category.objects.get(id=category_id)
            mid_category_id = request.POST.get('mid-category')
            mid_category = MidCategory.objects.get(id=mid_category_id)
            p_name = request.POST.get('product-name')
            sub_category_id = request.POST.get('sub-category')
            sub_category = SubCategory.objects.get(id=sub_category_id)
            mrp = request.POST.get('mrp')
            discount = request.POST.get('discount')
            selling_price = float(mrp) - float(mrp)*float(discount)/100
            slug = p_name
            p_type = request.POST.get('product-type')
            brand = request.POST.get('brand')
            short_description = request.POST.get('short-description')
            long_description = request.POST.get('long-description')
            created_at = datetime.datetime.now()
            product = Product(p_name=p_name, category=category, mid_category=mid_category, sub_category=sub_category, mrp=mrp, selling_price=selling_price, discount=discount, slug=slug, short_description=short_description, long_description=long_description, product_type=p_type, brand=brand, vendor_name=request.user.first_name, vendor_contact=request.user.email, trending=False, deals_of_the_day=False, most_popular=False, status=1, admin=False, created_at=created_at)
            product.full_clean()
            product.save()
            messages.info(request, 'Product is saved.')
            return redirect('/vendor/add-product/')
        except ValidationError as e:
            error_messages = []
            for field, errors in e.message_dict.items():
                field_name = Product._meta.get_field(field).verbose_name.capitalize()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            for message in error_messages:
                messages.error(request, message)
            return render(request, 'vendor/add-product.html', {'message':message})
    category = Category.objects.all()
    brand = Brand.objects.all()
    product_type = ProductType.objects.all()
    CONTEXT = {'category':category, 'brand':brand, 'product_type':product_type}
    return render(request, 'vendor/add-product.html', CONTEXT)

def ListOrder(request):
    vendor_contact = request.user.email
    if request.method == 'GET':
        if request.GET.get('status'):
            order=Order.objects.filter(ordered_items__variant__product__vendor_contact=vendor_contact, status=request.GET.get('status'))
        else:
            order = Order.objects.filter(ordered_items__variant__product__vendor_contact=vendor_contact)
    else:
        order = Order.objects.filter(vendor_contact=vendor_contact)
    CONTEXT = {'order':order}
    return render(request, 'vendor/list-order.html', CONTEXT)

def product_slug(name:str)->str:
    value = name.lower()
    allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789- "
    value = ''.join(char if char in allowed_chars else ' ' for char in value)
    value = '-'.join(value.split())
    name =  value.strip('-')
    while(Product.objects.filter(slug=name).exists()):
        value = name.lower()
        allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789- "
        value = ''.join(char if char in allowed_chars else ' ' for char in value)
        value = '-'.join(value.split())
        name =  value.strip('-')
    return name

def AddVariant(request, p_id):
    if request.method == 'POST':
        shades_id = request.POST.get('p_shades')
        shades = Shades.objects.get(id=shades_id)
        size = request.POST.get('size')
        thumbnail = request.FILES.get('thumbnail')
        image = request.FILES.getlist('img[]')
        qty = request.POST.get('qty')
        variant = Variant(product_id=p_id, shades=shades, size=size, thumbnail=thumbnail, qty=qty)
        variant.save()
        # v_id = variant.id
        for img in image:
            product_image = ProductImage(variant=variant, image=img)
            product_image.save()
        messages.info(request, 'Variant is saved.')
        return redirect('/vendor/add-variant/'+str(p_id))
    shades = Shades.objects.all()
    context = {"shades":shades}
    return render(request, 'vendor/add-variant.html', context)

def ListVariant(request, p_id):
    variant = Variant.objects.filter(product=p_id)
    CONTEXT = {'variant':variant}
    return render(request, 'vendor/show-variant.html', CONTEXT)

def ChangeProductStatus(request):
    id = request.POST.get('id')
    product = Product.objects.get(id=id)
    if product.admin:
        return HttpResponse('You can not update.')
    if product.status == True:
        product.status = False
    else:
        product.status = True
    product.save()
    return HttpResponse("Status Changed.")

def DeleteProduct(request, id):
    product = Product.objects.get(id=id)
    product_image = Product_image.objects.filter(p_id=id)
    for p in product_image:
        os.remove(p.image.path)
        p.delete()
    os.remove(product.thumbnail.path)
    product.delete()
    return redirect('/vendor/list-product/')

def Invoice(request, id):
    order = Order.objects.get(id=id)
    user = User.objects.get(username=order.customer)
    CONTEXT = {'order':order, 'name':user.first_name, 'random_number':random.randint(1000, 9999)}
    return render(request, 'vendor/invoice.html', CONTEXT)

@login_required(login_url='/vendor/login/')
def EditProduct(request, id):
    if request.method =='POST':
        try:
            category = request.POST.get('category')
            p_name = request.POST.get('product-name')
            sub_category_id = request.POST.get('sub-category')
            sub_category = Sub_category.objects.get(id=sub_category_id)
            mrp = request.POST.get('mrp')
            selling_price = request.POST.get('selling-price')
            discount = float(mrp) - float(selling_price)
            qty = request.POST.get('qty')
            sku = request.POST.get('sku')
            slug = ''
            p_type = request.POST.get('product-type')
            brand = request.POST.get('brand')
            short_description = request.POST.get('short-description')
            long_description = request.POST.get('long-description')
            thumbnail = request.FILES.get('thumbnail')
            img = request.FILES.getlist('img[]')
            product = Product.objects.get(id=id)
            product.category = category
            product.name = p_name
            product.sub_category = sub_category
            product.mrp = mrp
            product.selling_price = selling_price
            product.discount = discount
            product.qty = qty
            product.sku = sku
            product.p_type = p_type
            product.brand = brand
            product.short_description = short_description
            product.long_description = long_description
            if thumbnail is not None:
                if product.thumbnail:
                    product.thumbnail.delete()
                product.thumbnail = thumbnail
            if img:
                for image in img:
                    product_image = Product_image(p_id=product, image=image)
                    product_image.save()
            product.full_clean()
            product.save()
            messages.info(request, 'Product is updated.')
            return redirect('/vendor/edit-product/' + str(id))
        except ValidationError as e:
            error_messages = []
            for field, errors in e.message_dict.items():
                field_name = Product._meta.get_field(field).verbose_name.capitalize()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            for message in error_messages:
                messages.error(request, message)
            return render(request, 'vendor/edit-product.html', {'message':message})
    category = Category.objects.all()
    brand = Brand.objects.all()
    product_type = ProductType.objects.all()
    product = Product.objects.get(id=id)
    images = Product_image.objects.filter(p_id=id)
    p_sub_category = product.sub_category
    sub_category = Sub_category.objects.filter(category=product.category)
    CONTEXT = {'category':category, 'brand':brand, 'product_type':product_type, 'product':product, 'p_sub_category':p_sub_category, 'sub_category':sub_category, 'images':images}
    return render(request, 'vendor/edit-product.html', CONTEXT)

@login_required(login_url='/vendor/login/')
def EditProfile(request):
    if request.method =='POST':
        try:
            username = request.POST.get('user-name')
            name = request.POST.get('name')
            gst = request.POST.get('gst')
            e_mail = request.POST.get('e-mail')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            user = User.objects.get(username=username)
            user.first_name = name
            user.name = p_name
            user.email = e_mail
            profile = Vendor.objects.get(user_id=user.id)
            profile.gst = gst
            product.phone = phone
            product.address = address
            product.city = city
            product.state = state
            user.full_clean()
            profile.full_clean()
            user.save()
            profile.save()
            messages.info(request, 'Profile is updated.')
            return redirect('/vendor/edit-profile/')
        except ValidationError as e:
            error_messages = []
            for field, errors in e.message_dict.items():
                field_name = User._meta.get_field(field).verbose_name.capitalize()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            for message in error_messages:
                messages.error(request, message)
            return render(request, 'vendor/edit-profile.html', {'message':message})
    user = User.objects.get(username=request.user)
    id = user.id
    profile = Vendor.objects.get(user_id=id)
    CONTEXT = {'user':user, 'profile':profile}
    return render(request, 'vendor/profile.html', CONTEXT)

def DeleteVariant(request, id):
    variant = Variant.objects.get(id=id)
    variant.delete()
    return redirect('/vendor/list-product/')

def DeleteProductImage(request):
    id = request.POST.get('id')
    product_image = Product_image.objects.get(id=id)
    product_image.delete()
    return HttpResponse('Deleted')

def ChangeOrderStatus(request):
    order_status = request.POST.get('order-status')
    id = request.POST.get('order-id')
    order = Order.objects.get(id=id)
    order.status = order_status
    order.save()
    return HttpResponse("Status Changed.")

@login_required(login_url='/vendor/login/')
def ListOrderedItem(request, id):
    ordered_item = Ordered_item.objects.filter(order_id=id)
    CONTEXT = {'ordered_item':ordered_item}
    return render(request, 'vendor/list-ordered-item.html', CONTEXT)

def ChangeOrderedItemStatus(request):
    order_status = request.POST.get('order-status')
    id = request.POST.get('order-id')
    order = Ordered_item.objects.get(id=id)
    order.status = order_status
    order.save()
    return HttpResponse("Status Changed.")

def ListCustomer(request):
    customer = Profile.objects.select_related('user').all()
    CONTEXT = {'customer':customer}
    return render(request, 'vendor/list-customer.html', CONTEXT)