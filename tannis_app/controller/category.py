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

# Create your views here.
    


@login_required(login_url='/admin-login/')
def AddCategory(request):
    if request.method =='POST':
        try:
            c_name = request.POST.get('category-name')
            img = request.FILES.get('img')
            c_name_array = c_name.split()
            slug = category_slug(c_name)
            category = Category(c_name=c_name, image=img, slug=slug, status=True, created_at=datetime.datetime.now())
            category.full_clean()
            category.save()
            messages.info(request, 'Category is saved.')
            return redirect('/add-category/')
        except ValidationError as e:
            error_messages = []
            for field, errors in e.message_dict.items():
                field_name = Category._meta.get_field(field).verbose_name.capitalize()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            for message in error_messages:
                messages.error(request, message)
            return render(request, 'admin-panel/add-category.html', {'message':message})
    return render(request, 'admin-panel/add-category.html')

def ListCategory(request):
    category = Category.objects.all()
    CONTEXT = {'category':category}
    return render(request, 'admin-panel/list-category.html', CONTEXT)

@login_required(login_url='/admin-login/')
def AddMidCategory(request):
    if request.method =='POST':
        c_id = request.POST.get('category')
        mid_category_name = request.POST.get('mid-category-name')
        img = request.FILES.get('img')
        slug = mid_category_name
        mid_category = MidCategory(m_name=mid_category_name, image=img, slug=slug, category_id=c_id, status=True, created_at=datetime.datetime.now())
        mid_category.save()
        messages.info(request, 'Mid category is saved.')
        return redirect('/add-mid-category/')
    category = Category.objects.all()
    return render(request, 'admin-panel/add-mid-category.html', {'category':category})

def ListMidCategory(request):
    mid_category = MidCategory.objects.all()
    CONTEXT = {'mid_category':mid_category}
    return render(request, 'admin-panel/list-mid-category.html', CONTEXT)

@login_required(login_url='/admin-login/')
def AddSubCategory(request):
    if request.method =='POST':
        try:
            m_id = request.POST.get('mid-category')
            sub_category = request.POST.get('sub-category')
            img = request.FILES.get('img')
            slug = sub_category
            
            mid_category = MidCategory.objects.get(id=m_id)
            sub_category = SubCategory(s_name=sub_category, slug=slug, mid_category=mid_category, status=True, created_at=datetime.datetime.now())
            sub_category.full_clean()
            sub_category.save()
            messages.info(request, 'Sub category is saved.')
            return redirect('/add-sub-category/')
        except ValidationError as e:
            error_messages = []
            for field, errors in e.message_dict.items():
                field_name = SubCategory._meta.get_field(field).verbose_name.capitalize()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            for message in error_messages:
                messages.error(request, message)
            return render(request, 'admin-panel/add-sub-category.html', {'message':message})
    category = Category.objects.all()
    return render(request, 'admin-panel/add-sub-category.html', {'category':category})

def ListSubCategory(request):
    sub_category = SubCategory.objects.all()
    CONTEXT = {'sub_category':sub_category}
    return render(request, 'admin-panel/list-sub-category.html', CONTEXT)


def category_slug(name:str)->str:
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

def sub_category_slug(name:str)->str:
    value = name.lower()
    allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789- "
    value = ''.join(char if char in allowed_chars else ' ' for char in value)
    value = '-'.join(value.split())
    name =  value.strip('-')
    while(SubCategory.objects.filter(slug=name).exists()):
        value = name.lower()
        allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789- "
        value = ''.join(char if char in allowed_chars else ' ' for char in value)
        value = '-'.join(value.split())
        name =  value.strip('-')
    return name

def mid_category_slug(name:str)->str:
    value = name.lower()
    allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789- "
    value = ''.join(char if char in allowed_chars else ' ' for char in value)
    value = '-'.join(value.split())
    name =  value.strip('-')
    while(MidCategory.objects.filter(slug=name).exists()):
        value = name.lower()
        allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789- "
        value = ''.join(char if char in allowed_chars else ' ' for char in value)
        value = '-'.join(value.split())
        name =  value.strip('-')
    return name

def DeleteCategory(request, id):
    try:
        category = Category.objects.get(id=id)
        if category.image:
            try:
                os.remove(category.image.path)
            except FileNotFoundError:
                pass
        category.delete()
        return redirect('/list-category/')
    except ObjectDoesNotExist:
        return redirect('/list-category/')

def DeleteSubCategory(request, id):
    sub_category = Sub_category.objects.get(id=id)
    os.remove(sub_category.image.path)
    sub_category.delete()
    return redirect('/list-sub-category/')


@login_required(login_url='/admin-login/')
def EditCategory(request, id):
    if request.method =='POST':
        id = request.POST.get('id')
        c_name = request.POST.get('category-name')
        image = request.FILES.get('img')
        slug = category_slug(c_name)
        category = Category.objects.get(id=id)
        category.c_name = c_name
        if image is not None:
            if category.image:
                category.image.delete()
            category.image = image
        category.slug = slug
        category.save()
        messages.info(request, 'Category updated.')
        return redirect('/list-category/')
    category = Category.objects.get(id=id)
    context = {'id':id, 'category':category}
    return render(request, 'admin-panel/edit-category.html', context)

@login_required(login_url='/admin-login/')
def EditSubCategory(request, id):
    if request.method =='POST':
        
        try:
            id = request.POST.get('id')
            c_id = request.POST.get('category')
            sub_category_name = request.POST.get('sub-category-name')
            img = request.FILES.get('img')
            slug = sub_category_slug(sub_category_name)
            category = Category.objects.get(id=c_id)
            sub_category = Sub_category.objects.get(id=id)
            sub_category.category = category
            sub_category.s_name = sub_category_name
            sub_category.slug = slug
            if img is not None:
                if sub_category.image:
                    sub_category.image.delete()
                sub_category.image = img
            sub_category.full_clean()
            sub_category.save()
            messages.info(request, 'Sub category is updated.')
            return redirect('/edit-sub-category/' + str(id))
        except ValidationError as e:
            error_messages = []
            for field, errors in e.message_dict.items():
                field_name = Sub_category._meta.get_field(field).verbose_name.capitalize()
                for error in errors:
                    error_messages.append(f"{field_name}: {error}")
            for message in error_messages:
                messages.error(request, message)
            return render(request, 'admin-panel/edit-sub-category.html', {'message':message})
    category = Category.objects.all()
    sub_category = Sub_category.objects.get(id=id)
    context = {'category':category, 'sub_category':sub_category}
    return render(request, 'admin-panel/edit-sub-category.html', context)

def FetchMidCategory(request):
    if request.method =='POST':
        category = request.POST.get('category')
        mid_category = MidCategory.objects.filter(category = category)
        mid_category_o = '<option value="Select Mid Category">Select Mid Category</option>'
        for m in mid_category:
            option = '<option value="'+str(m.id)+'">'+m.m_name+'</option>'
            mid_category_o += option
        return HttpResponse(mid_category_o)

def FetchSubCategory(request):
    if request.method =='POST':
        mid_category = request.POST.get('mid_category')
        sub_category = SubCategory.objects.filter(mid_category = mid_category)
        sub_category_o = '<option value="Select Sub Category">Select Sub Category</option>'
        for s in sub_category:
            option = '<option value="'+str(s.id)+'">'+s.s_name+'</option>'
            sub_category_o += option
        return HttpResponse(sub_category_o)
