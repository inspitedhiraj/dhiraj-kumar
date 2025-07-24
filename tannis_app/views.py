from django.shortcuts import render, redirect
from tannis_app.models import *
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from array import *
from django.db import connection
import random
from django.db.models import *
import datetime
import os
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
    

# Admin Panel

def AdminLogin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.filter(username=username)
        if not user.exists():
            messages.info(request, 'User does not exist.')
            return redirect('/admin-login')
        user = authenticate(username=username, password=password)
        if not user.is_superuser:
            messages.info(request, 'Sorry, You are not admin.')
            return redirect('/admin-login')
        if user is not None:
            login(request, user)
            return redirect('/dashboard')
        else:
            messages.info(request, 'Password is incorrect.')
            return redirect('/admin-login')
    return render(request, 'admin-panel/login.html')

def AdminLogout(request):
    logout(request)
    return redirect('/admin-login')

@login_required(login_url='/admin-login/')
def Dashboard(request):
    number_of_product = Product.objects.all().count()
    total_banner = Banner.objects.all().count()
    total_category = Category.objects.all().count()
    total_brand = Brand.objects.all().count()
    total_vendor = Vendor.objects.all().count()
    total_order = Order.objects.all().count()
    CONTEXT = {'number_of_product':number_of_product, 'total_banner':total_banner, 'total_category':total_category, 'total_brand':total_brand, 'total_vendor':total_vendor, 'total_order':total_order}
    return render(request, 'admin-panel/index.html', CONTEXT)

def ListCustomer(request):
    return render(request, 'admin-panel/customers.html')

def FilterProduct(request):
    return render(request, 'admin-panel/customers.html')

def FetchSubCategory(request):
    if request.method =='POST':
        category = request.POST.get('category')
        sub_category = Sub_category.objects.filter(category_id = category)
        sub_category_o = '<option value="Select Product Category">Select Product sub Category</option>'
        for s in sub_category:
            option = '<option value="'+str(s.id)+'">'+s.s_name+'</option>'
            sub_category_o += option
    return HttpResponse(sub_category_o)

def ListVendor(request):
    vendor = Vendor.objects.select_related('user').all()
    CONTEXT = {'vendor':vendor}
    return render(request, 'admin-panel/list-vendor.html', CONTEXT)

def ListOrder(request):
    order = Order.objects.all()
    if request.method == 'GET':
        if request.GET.get('status'):
            order=order.filter(status=request.GET.get('status'))
    CONTEXT = {'order':order}
    return render(request, 'admin-panel/list-order.html', CONTEXT)

def Invoice(request, id):
    order = Order.objects.get(id=id)
    item = Ordered_item.objects.filter(order=order)
    user = User.objects.get(id=order.user_id)
    CONTEXT = {'order':order, 'item':item, 'name':user.first_name, 'random_number':random.randint(1000, 9999)}
    return render(request, 'admin-panel/invoice.html', CONTEXT)

@login_required(login_url='/admin-login/')
def AddBrand(request):
    if request.method =='POST':
        try:
            brand_name = request.POST.get('brand-name')
            img = request.FILES.get('img')
            brand = Brand(brand_name=brand_name, image=img, wishlist=False)
            brand.full_clean()
            brand.save()
            messages.info(request, 'Brand is saved.')
            return redirect('/add-brand/')
        except ValidationError as e:
            error_messages = []
            for field, errors in e.message_dict.items():
                field_name = brand._meta.get_field(field).verbose_name.capitalize()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            for message in error_messages:
                messages.error(request, message)
            return render(request, 'admin-panel/add-brand.html', {'message':message})
    return render(request, 'admin-panel/add-brand.html')

def ListBrand(request):
    brand = Brand.objects.all()
    CONTEXT = {'brand':brand}
    return render(request, 'admin-panel/list-brand.html', CONTEXT)

def AddProductType(request):
    if request.method == 'POST':
        product_type = request.POST.get('product-type')
        type_of_product = ProductType(product_type=product_type)
        type_of_product.save()
        messages.info(request, 'Product Type is saved.')
    return render(request, 'admin-panel/add-product-type.html')

def ListProductType(request):
    product_type = ProductType.objects.all()
    CONTEXT = {'product_type':product_type}
    return render(request, 'admin-panel/list-product-type.html', CONTEXT)

def ListProduct(request):
    product = Product.objects.all()
    CONTEXT = {'product':product}
    return render(request, 'admin-panel/list-product.html', CONTEXT)

def ListVariant(request, p_id):
    variant = Variant.objects.filter(product=p_id)
    CONTEXT = {'variant':variant}
    return render(request, 'admin-panel/show-variant.html', CONTEXT)

def ChangeProductStatus(request):
    id = request.POST.get('id')
    product = Product.objects.get(id=id)
    if product.status == True:
        product.status = False
    else:
        product.status = True
    if product.admin == True:
        product.admin = False
    else:
        product.admin = True
    product.save()
    return HttpResponse("Status Changed.")

def DeleteProductType(request, id):
    product_type = ProductType.objects.get(id=id)
    product_type.delete()
    return redirect('/list-product-type/')

def DeleteBrand(request, id):
    brand = Brand.objects.get(id=id)
    os.remove(brand.image.path)
    brand.delete()
    return redirect('/list-brand/')

def ChangeVendorStatus(request):
    id = request.POST.get('id')
    vendor = Vendor.objects.get(id=id)
    if vendor.status == True:
        vendor.status = False
    else:
        vendor.status = True
    vendor.save()
    return HttpResponse("Status Changed.")

def DeleteVendor(request, id):
    vendor = Vendor.objects.get(id=id)
    vendor.delete()
    return redirect('/list-vendor/')

@login_required(login_url='/admin-login/')
def EditBrand(request, id):
    if request.method =='POST':
        id = request.POST.get('id')
        brand_name = request.POST.get('brand-name')
        image = request.FILES.get('img')
        slug = ''
        brand = Brand.objects.get(id=id)
        brand.brand_name = brand_name
        if image is not None:
            if brand.image:
                brand.image.delete()
            brand.image = image
        brand.slug = slug
        brand.save()
        messages.info(request, 'Brand updated.')
        return redirect('/edit-brand/' + str(id))
    brand = Brand.objects.get(id=id)
    context = {'id':id, 'brand':brand}
    return render(request, 'admin-panel/edit-brand.html', context)

@login_required(login_url='/admin-login/')
def AddBanner(request):
    if request.method =='POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            img = request.FILES.get('img')
            brand = request.POST.get('brand')
            banner = Banner(title=title, description=description, image=img, brand=brand, status=True, created_at=datetime.datetime.now())
            banner.full_clean()
            banner.save()
            messages.info(request, 'Banner is saved.')
            return redirect('/add-banner/')
        except ValidationError as e:
            error_messages = []
            for field, errors in e.message_dict.items():
                field_name = banner._meta.get_field(field).verbose_name.capitalize()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            for message in error_messages:
                messages.error(request, message)
            return render(request, 'admin-panel/add-banner.html', {'message':message})
    return render(request, 'admin-panel/add-banner.html')

def ListBanner(request):
    banner = Banner.objects.all()
    CONTEXT = {'banner':banner}
    return render(request, 'admin-panel/list-banner.html', CONTEXT)

def ChangeOrderStatus(request):
    order_status = request.POST.get('order-status')
    id = request.POST.get('order-id')
    order = Order.objects.get(id=id)
    order.status = order_status
    order.save()
    return HttpResponse("Status Changed.")

@login_required(login_url='/admin-login/')
def UpdateVendor(request, id):
    vendor = Vendor.objects.get(id=id)
    user_id = vendor.user_id
    user = User.objects.get(id=user_id)
    if request.method =='POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            gst = request.POST.get('gst')
            state = request.POST.get('state')
            city = request.POST.get('city')
            address = request.POST.get('address')
            sub_category = request.POST.getlist('sub-category[]')
            commission_value = request.POST.getlist('commission[]')
            user.first_name = name
            vendor.phone = phone
            vendor.gst = gst
            vendor.state = state
            vendor.city = city
            vendor.address = address
            commission = Commission.objects.filter(vendor=user).delete()
            for i in range(len(sub_category)):
                sub_category_id = sub_category[i]
                s_category = Sub_category.objects.get(id=sub_category_id)
                c = commission_value[i]
                add_new_commission = Commission(vendor=user, sub_category=s_category, commission=c)
                add_new_commission.save()
            messages.info(request, 'Vendor updated.')
            return redirect('/edit-vendor/' + str(id))
        except ValidationError as e:
            error_messages = []
            for field, errors in e.message_dict.items():
                field_name = Sub_category._meta.get_field(field).verbose_name.capitalize()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            for message in error_messages:
                messages.error(request, message)
            return render(request, 'admin-panel/edit-vendor.html', {'message':message})
    sub_category = Sub_category.objects.all()
    commission = Commission.objects.filter(vendor=user)
    return render(request, 'admin-panel/edit-vendor.html', {'sub_category':sub_category, 'vendor':vendor, 'commission':commission})

@login_required(login_url='/admin-login/')
def AddVendor(request):
    if request.method =='POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            gst = request.POST.get('gst')
            address = request.POST.get('address')
            state = request.POST.get('state')
            city = request.POST.get('city')
            password = random.randint(1000, 9999)
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email is already in use.')
                return render(request, 'admin-panel/add-vendor.html')
            
            user = User.objects.create_user(email=email, username=email, password=str(password))
            user.first_name=name
            user.save()
            
            vendor = Vendor(phone=phone, gst=gst, state=state, city=city, address=address, status=True, user=user, added_by='admin')
            vendor.full_clean()
            vendor.save()
            messages.info(request, 'Vendor is saved. Password: ' + str(password))
            return redirect('/add-brand/')
        except ValidationError as e:
            error_messages = []
            for field, errors in e.message_dict.items():
                field_name = vendor._meta.get_field(field).verbose_name.capitalize()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            for message in error_messages:
                messages.error(request, message)
            return render(request, 'admin-panel/add-vendor.html', {'message':message})
    return render(request, 'admin-panel/add-vendor.html')

def ListCustomer(request):
    customer = Profile.objects.select_related('user').all()
    CONTEXT = {'customer':customer}
    return render(request, 'admin-panel/list-customer.html', CONTEXT)

def ChangeCustomerStatus(request):
    id = request.POST.get('id')
    customer = Profile.objects.get(id=id)
    if customer.status == True:
        customer.status = False
    else:
        customer.status = True
    customer.save()
    return HttpResponse("Status Changed.")

def ChangeBrandWishlistStatus(request):
    id = request.POST.get('id')
    brand = Brand.objects.get(id=id)
    if brand.wishlist == True:
        brand.wishlist = False
    else:
        brand.wishlist = True
    brand.save()
    return HttpResponse("Status Changed.")

def AddTrandingOffer(request):
    if request.method == 'POST':
        coupon = request.POST.get('coupon-code')
        image = request.FILES.get('img')
        discount = request.POST.get('discount')
        description = request.POST.get('description')
        trandingOffer = TrandingOffer(coupon=coupon, image=image, discount=discount, description=description)
        trandingOffer.save()
        messages.info(request, 'Tranding offer is saved.')
        return redirect('/add-tranding-offer/')
    return render(request, 'admin-panel/add-tranding-offer.html')

def ListTrandingOffer(request):
    tranding_offer = TrandingOffer.objects.all()
    CONTEXT = {'tranding_offer':tranding_offer}
    return render(request, 'admin-panel/list-tranding-offer.html', CONTEXT)

@login_required(login_url='/admin-login/')
def AddShades(request):
    if request.method =='POST':
        try:
            s_name = request.POST.get('shades-name')
            img = request.FILES.get('img')
            shades = Shades(s_name=s_name, image=img, status=True, created_at=datetime.datetime.now())
            shades.full_clean()
            shades.save()
            messages.info(request, 'Shades is saved.')
            return redirect('/add-shades/')
        except ValidationError as e:
            error_messages = []
            for field, errors in e.message_dict.items():
                field_name = Shades._meta.get_field(field).verbose_name.capitalize()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            for message in error_messages:
                messages.error(request, message)
            return render(request, 'admin-panel/add-shades.html', {'message':message})
    return render(request, 'admin-panel/add-shades.html')

def ListShades(request):
    shades = Shades.objects.all()
    CONTEXT = {'shades':shades}
    return render(request, 'admin-panel/list-shades.html', CONTEXT)